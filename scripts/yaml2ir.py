#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaml2ir.py — flowchart-generator YAML → fireworks-tech-graph JSON IR 转换器
=============================================================================

方案 A 落地：直接用原版 fireworks-tech-graph（opensource-reference/fireworks-tech-graph）
作为渲染引擎。本脚本把我们自研 flowchart-generator 的 YAML（含坐标）转换成
原版要求的 JSON IR（schema_version=1），从而获得原版 12 风格渲染器 + 组合质检。

数据流：
  YAML（自研，含坐标）
      ↓  [yaml2ir.py]
  JSON IR（原版 schema-v1）
      ↓  [fireworks.py render]（原版引擎）
  SVG → PNG（原版 12 风格，带形状语言/语义色/装饰）

用法：
  python yaml2ir.py <input.yaml> --style 13 --target-style 5 -o out.json
  python yaml2ir.py <input.yaml> --style 13 --target-style 5 --render --out-dir out/

参数：
  --style          输入 YAML 的风格（13 架构 / 14 agent 编排 / 16 数据流），默认自动推断
  --target-style   原版风格 1-12（默认 5 玻璃拟态；暗色建议 2 Dark Terminal / 8 Dark Luxury；
                   暖色建议 6 Claude Official / 4 Notion Clean）
  --profile        standard（宽松，默认）| showcase（严格：节点间距≥40 / 容器边距≥20）
  --title/--subtitle  覆盖标题/副标题
  --render         转换后直接调用原版渲染 + PNG 导出
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("❌ 缺少 PyYAML，请安装：pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ============ 常量 ============

# 自研风格 → 原版风格的推荐映射（可被 --target-style 覆盖）
STYLE_MAP = {
    13: 5,   # 架构图 → Glassmorphism（暗色玻璃拟态）
    14: 5,   # Agent 编排 → Glassmorphism
    15: 6,   # 数据管线 → Claude Official
    16: 6,   # 数据流 → Claude Official
    17: 4,   # 泳道 → Notion Clean
    18: 18,  # 时序图不支持，占位
}

# 节点标签关键词 → 原版 kind（形状语言）
KIND_RULES: List[Tuple[Tuple[str, ...], str]] = [
    (("coordinator", "orchestrator", "planner", "编排", "协调", "规划", "调度"), "double_rect"),
    (("memory", "store", "storage", "vector", "db", "cache", "记忆", "存储", "向量", "数据库"), "cylinder"),
    (("terminal", "console", "shell", "sandbox", "沙箱", "终端", "命令行"), "terminal"),
    (("user", "console", "app", "client", "用户", "控制台", "客户端", "入口", "应用"), "rect"),
    (("agent", "智能体", "gateway", "网关", "tool", "工具", "service", "服务", "cluster", "集群"), "rect"),
]

# 箭头 label/属性 → flow 语义（原版用 flow 决定箭头颜色与线型）
FLOW_RULES: List[Tuple[Tuple[str, ...], str]] = [
    (("tool_call", "inference", "write", "execute", "调用", "执行", "写入"), "write"),
    (("dispatch", "delegate", "task", "control", "派发", "下发", "任务"), "control"),
    (("result", "feedback", "review", "回", "反馈", "结果", "审查"), "feedback"),
]


# ============ 几何工具 ============

class Rect:
    """轴对齐矩形。"""

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y, self.w, self.h = float(x), float(y), float(w), float(h)

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    def contains_point(self, px: float, py: float, tol: float = 0.01) -> bool:
        return self.x - tol <= px <= self.x2 + tol and self.y - tol <= py <= self.y2 + tol

    def overlaps(self, other: "Rect", pad: float = 0.0) -> bool:
        return not (self.x2 + pad < other.x or other.x2 + pad < self.x or
                    self.y2 + pad < other.y or other.y2 + pad < self.y)


def _pick_ports(frm: Rect, to: Rect) -> Tuple[str, str]:
    """按几何关系推断连接端口，保证正交且无微段。

    优先"对边直连"：水平重叠 → 左右端口；垂直重叠 → 上下端口；
    否则按相对方位选边。返回 (source_port, target_port)，取值
    left/right/top/bottom。
    """
    horiz_overlap = max(0.0, min(frm.x2, to.x2) - max(frm.x, to.x))
    vert_overlap = max(0.0, min(frm.y2, to.y2) - max(frm.y, to.y))

    if horiz_overlap >= min(16, min(frm.h, to.h)):
        # 左右相邻（水平重叠 → 用左右端口）
        if to.cx >= frm.cx:
            return "right", "left"
        return "left", "right"
    if vert_overlap >= min(16, min(frm.w, to.w)):
        # 上下相邻（垂直重叠 → 用上下端口）
        if to.cy >= frm.cy:
            return "bottom", "top"
        return "top", "bottom"
    # 对角：优先水平方向（向右）
    if abs(to.cx - frm.cx) >= abs(to.cy - frm.cy):
        return ("right", "left") if to.cx >= frm.cx else ("left", "right")
    return ("bottom", "top") if to.cy >= frm.cy else ("top", "bottom")


# ============ 转换核心 ============

def _infer_kind(label: str, sublabel: str = "") -> str:
    """启发式推断节点形状（形状语言是原版好看的关键之一）。"""
    text = (label + " " + sublabel).lower()
    for keywords, kind in KIND_RULES:
        if any(kw.lower() in text for kw in keywords):
            return kind
    return "rect"


def _infer_flow(label: str, dashed: bool) -> str:
    """推断箭头语义流。"""
    text = (label or "").lower()
    for keywords, flow in FLOW_RULES:
        if any(kw in text for kw in keywords):
            return flow
    return "feedback" if dashed else "read"


def collect_style13(data: dict, sx: float) -> Tuple[List[Tuple[str, Rect, Dict[str, Any]]],
                                                   List[Tuple[str, Rect, Dict[str, Any]]],
                                                   List[Dict[str, Any]]]:
    """style13 架构图：收集节点/容器/边。

    返回 (nodes, containers, arrows)：
      - nodes: [(id, rect, attrs)]  可视节点（含层内 items / 组内 sub_items / cards）
      - containers: [(id, rect, attrs)]  分组容器（每组一个）
      - arrows: [{from_x, from_y, to_x, to_y, label, dashed}]
    """
    nodes: List[Tuple[str, Rect, Dict[str, Any]]] = []
    containers: List[Tuple[str, Rect, Dict[str, Any]]] = []

    def abs_x(x: float) -> float:
        return float(x) + sx  # 内容坐标 → 画布坐标（与 gen.py 一致）

    for layer in data.get("layers", []):
        lid = str(layer.get("id", ""))
        ly = layer.get("y", 0)
        layer_label = layer.get("label", "")
        if lid == "L0":
            # 顶层入口卡片：直接是节点
            for it in layer.get("items", []):
                nid = f"L0_{it.get('en', '?')}"
                nodes.append((nid, Rect(abs_x(it.get("x", 0)), float(it.get("y", ly)),
                                        float(it.get("w", 140)), float(it.get("h", 52))), it))
        else:
            # 组容器 + 组内子节点
            for g in layer.get("groups", []):
                gid = f"{lid}_{g.get('en', '?')}"
                gx, gy = abs_x(g.get("x", 0)), float(g.get("y", ly))
                gw, gh = float(g.get("w", 240)), float(g.get("h", 60))
                gattrs = {"label": g.get("en", ""), "zh": g.get("zh", ""),
                          "layer": layer_label, "side": layer.get("side_label", "")}
                containers.append((gid, Rect(gx, gy, gw, gh), gattrs))
                # sub_items（带内部小卡片）
                for sub in g.get("sub_items", []):
                    sid = f"{gid}_{sub.get('en', '?')}"
                    nodes.append((sid, Rect(abs_x(sub.get("x", 0)), float(sub.get("y", gy)),
                                            float(sub.get("w", 200)), float(sub.get("h", 60))), sub))
                # items（组内列表项：dict=节点矩形；str=容器内小标签，跳过）
                for it in g.get("items", []):
                    if not isinstance(it, dict):
                        continue
                    iid = f"{gid}_{it.get('en', '?')}"
                    nodes.append((iid, Rect(abs_x(it.get("x", 0)), float(it.get("y", gy)),
                                            float(it.get("w", 200)), float(it.get("h", 44))), it))
    # 边：坐标点形式
    arrows = []
    for arr in data.get("arrows", []):
        frm, to = arr.get("from"), arr.get("to")
        if isinstance(frm, (list, tuple)) and len(frm) == 2 and isinstance(to, (list, tuple)) and len(to) == 2:
            arrows.append({"from": [float(frm[0]) + sx, float(frm[1])],
                           "to": [float(to[0]) + sx, float(to[1])],
                           "label": arr.get("label", ""), "dashed": bool(arr.get("dashed"))})
    return nodes, containers, arrows


def match_endpoint(px: float, py: float, nodes: List[Tuple[str, Rect, Dict[str, Any]]]) -> Optional[str]:
    """把箭头端点坐标匹配到节点 id（点在内 → 该节点；否则最近节点）。"""
    best, best_dist = None, float("inf")
    for nid, rect, _ in nodes:
        if rect.contains_point(px, py, tol=2):
            return nid
        dist = (rect.cx - px) ** 2 + (rect.cy - py) ** 2
        if dist < best_dist:
            best, best_dist = nid, dist
    return best


def build_ir(data: dict, style: int, target_style: int, profile: str,
             title: Optional[str], subtitle: Optional[str]) -> Dict[str, Any]:
    """把 YAML 组装成原版 JSON IR。"""
    meta = data.get("meta", {})
    sx = 26 if meta.get("sidebar", True) else 0
    canvas_w = float(meta.get("width", 1280)) + sx
    canvas_h = float(meta.get("height", 800))

    if style == 13:
        nodes, containers, arrows = collect_style13(data, sx)
    else:
        raise ValueError(f"style {style} 转换器尚未实现（当前支持 13）")

    ir_nodes: List[Dict[str, Any]] = []
    for nid, rect, attrs in nodes:
        en = attrs.get("en", "")
        zh = attrs.get("zh", "")
        label = zh or en  # 中文优先（用户重点看中文适配）
        sub = attrs.get("desc", "")
        kind = _infer_kind(en + " " + zh, sub)
        node = {
            "id": nid, "kind": kind, "label": label,
            "x": round(rect.x, 1), "y": round(rect.y, 1),
            "width": round(rect.w, 1), "height": round(rect.h, 1),
        }
        if sub:
            node["sublabel"] = sub
        if kind == "double_rect":
            node["type_label"] = "编排器"
        elif kind == "cylinder":
            node["type_label"] = "存储"
        ir_nodes.append(node)

    ir_containers: List[Dict[str, Any]] = []
    for cid, rect, attrs in containers:
        label = attrs.get("zh") or attrs.get("label") or cid
        ir_containers.append({
            "id": cid, "label": label,
            "x": round(rect.x, 1), "y": round(rect.y, 1),
            "width": round(rect.w, 1), "height": round(rect.h, 1),
        })

    ir_arrows: List[Dict[str, Any]] = []
    for idx, arrow in enumerate(arrows):
        src = match_endpoint(arrow["from"][0], arrow["from"][1], nodes)
        tgt = match_endpoint(arrow["to"][0], arrow["to"][1], nodes)
        flow = _infer_flow(arrow["label"], arrow["dashed"])
        entry: Dict[str, Any] = {"id": f"e{idx:02d}", "flow": flow}
        if src and tgt:
            entry["source"], entry["target"] = src, tgt
            rects = {nid: rect for nid, rect, _ in nodes}
            sp, tp = _pick_ports(rects[src], rects[tgt])
            entry["source_port"], entry["target_port"] = sp, tp
        else:
            # 找不到节点引用 → 直接用坐标点做路由
            entry["route_points"] = [arrow["from"], arrow["to"]]
        if arrow["label"]:
            entry["label"] = arrow["label"]
        ir_arrows.append(entry)

    # 组装 IR
    ir: Dict[str, Any] = {
        "schema_version": 1,
        "mode": "agent" if style == 14 else "architecture",
        "template_type": "agent" if style == 14 else "architecture",
        "style": target_style,
        "quality_profile": profile,
        "width": round(canvas_w, 1),
        "height": round(canvas_h, 1),
        "title": title or meta.get("title_en") or meta.get("title") or "架构图",
        "nodes": ir_nodes,
        "arrows": ir_arrows,
    }
    if ir_containers:
        ir["containers"] = ir_containers
    if subtitle or meta.get("subtitle"):
        ir["subtitle"] = subtitle or meta.get("subtitle")
    return ir


# ============ CLI ============

def main() -> int:
    parser = argparse.ArgumentParser(description="flowchart-generator YAML → fireworks JSON IR 转换器")
    parser.add_argument("input", help="输入 YAML 文件")
    parser.add_argument("--style", type=int, default=0, help="输入风格 13/14/16（默认自动推断）")
    parser.add_argument("--target-style", type=int, default=0, help="原版风格 1-12（默认按 STYLE_MAP）")
    parser.add_argument("--profile", default="standard", choices=["standard", "showcase"],
                        help="组合质检档位（standard 宽松 / showcase 严格）")
    parser.add_argument("--title", default=None)
    parser.add_argument("--subtitle", default=None)
    parser.add_argument("-o", "--output", default=None, help="输出 JSON IR 路径")
    parser.add_argument("--render", action="store_true", help="转换后调用原版渲染并导出 PNG")
    parser.add_argument("--out-dir", default=None, help="渲染产物目录")
    args = parser.parse_args()

    data = yaml.safe_load(Path(args.input).read_text(encoding="utf-8"))
    style = args.style or _infer_style(data)
    target_style = args.target_style or STYLE_MAP.get(style, 5)
    if style == 18:
        print("❌ style18 时序图不在转换范围（原版用 sequence 模式）", file=sys.stderr)
        return 1

    ir = build_ir(data, style, target_style, args.profile, args.title, args.subtitle)

    out_path = args.output or str(Path(args.input).with_suffix(".ir.json"))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(ir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ IR 已生成: {out_path}  (style {style} → 原版 style {target_style}, {len(ir['nodes'])} 节点 / {len(ir['arrows'])} 箭头)")

    if args.render:
        fw = find_fireworks()
        if not fw:
            print("❌ 未找到 fireworks.py（预期在 opensource-reference/fireworks-tech-graph/scripts）", file=sys.stderr)
            return 1
        out_dir = Path(args.out_dir or Path(args.input).parent)
        out_dir.mkdir(parents=True, exist_ok=True)
        svg_path = out_dir / (Path(args.input).stem + f"-fw-style{target_style}.svg")
        mode = ir["mode"]
        r = subprocess.run([sys.executable, str(fw), "render", mode, out_path, str(svg_path)],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print("❌ 原版渲染失败:", r.stdout.strip() or r.stderr.strip(), file=sys.stderr)
            return 1
        print(f"✅ SVG: {svg_path}")
        png = export_png(svg_path, out_dir)
        if png:
            print(f"✅ PNG: {png}")
    return 0


def _infer_style(data: dict) -> int:
    if "layers" in data:
        return 13
    if "main_flow" in data:
        return 14
    if "nodes" in data and "edges" in data:
        return 16
    if "steps" in data:
        return 15
    return 13


def find_fireworks() -> Optional[Path]:
    """定位原版 fireworks.py（支持绝对路径/常见相对位置）。"""
    for cand in [
        Path("d:/ai/latex/opensource-reference/fireworks-tech-graph/scripts/fireworks.py"),
        Path.cwd() / "fireworks.py",
    ]:
        if cand.exists():
            return cand
    return None


def export_png(svg_path: Path, out_dir: Path) -> Optional[Path]:
    """SVG → PNG（优先 cairosvg，其次 playwright，最次 chrome headless）。"""
    png_path = out_dir / (svg_path.stem + ".png")
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), scale=2.0)
        return png_path
    except Exception:
        pass
    try:
        from playwright.sync_api import sync_playwright
        svg = svg_path.read_text(encoding="utf-8")
        import re
        m = re.search(r'viewBox="([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)"', svg)
        w = int(float(m.group(3)) * 2) if m else 1920
        h = int(float(m.group(4)) * 2) if m else 1400
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(svg_path.resolve().as_uri(), wait_until="load")
            page.wait_for_timeout(800)
            page.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": w, "height": h})
            browser.close()
        return png_path
    except Exception:
        pass
    chrome = shutil.which("chrome") or shutil.which("msedge")
    if chrome:
        subprocess.run([chrome, "--headless", "--disable-gpu", f"--screenshot={png_path}",
                        "--window-size=1920,1400", str(svg_path.resolve())], check=False)
        if png_path.exists():
            return png_path
    return None


if __name__ == "__main__":
    sys.exit(main())
