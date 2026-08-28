#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagram_geometry — 图表质量校验共享库
=====================================

借鉴 archify 的"布局判断靠 agent、路由判断靠代码、质量兜底靠校验"哲学：
所有函数都是纯函数，接收测量好的矩形/线段，返回 Problem 列表。

每个 Problem 都带：
  - code: 稳定错误码（如 "clean-flow/edge-through-node"）
  - severity: "error"（硬失败）| "warning"（showcase 失败）
  - message: 含数字阈值 + 修复动词的人类可读消息
  - subject: 精确定位（哪个边/节点/标签）
  - evidence: 测量数据（坐标、重叠量等）
  - supported_fixes: 只允许的修复手段

用法：
  from diagram_geometry import Rect, Problem, clean_flow_problems, ...
  problems = clean_flow_problems(edges, nodes)
  if problems:
      for p in problems: print(p)
      sys.exit(1)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# ============== 数据类 ==============


@dataclass
class Rect:
    """矩形：统一适配 {x,y,w,h} 和 {x,y,width,height} 两种 dict 格式"""
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @classmethod
    def from_dict(cls, d: dict) -> "Rect":
        """从 dict 构建：兼容 w/width, h/height"""
        w = d.get("w", d.get("width", 0))
        h = d.get("h", d.get("height", 0))
        return cls(float(d.get("x", 0)), float(d.get("y", 0)), float(w), float(h))

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}


@dataclass
class Problem:
    """质量问题：带错误码 + 修复建议，让 LLM 能自愈"""
    code: str
    severity: str  # "error" | "warning"
    message: str
    subject: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    supported_fixes: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag = "❌" if self.severity == "error" else "⚠️"
        fixes = "; ".join(self.supported_fixes) if self.supported_fixes else "无"
        return f"  {tag} [{self.code}] {self.message} → 修复: {fixes}"


# ============== 基础几何 ==============


def rects_overlap(a: Rect, b: Rect, gap: float = 0) -> bool:
    """两个矩形是否重叠（gap > 0 表示要求间距至少 gap px）"""
    return not (
        a.right <= b.x + gap
        or b.right <= a.x + gap
        or a.bottom <= b.y + gap
        or b.bottom <= a.y + gap
    )


def segment_intersects_rect(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    rect: Rect,
    clearance: float = 0,
) -> bool:
    """线段 [p1,p2] 是否与矩形（含 clearance 外扩）相交。
    用 Liang-Barsky 线段裁剪算法：裁剪后若有剩余部分则相交。
    """
    x1, y1 = p1
    x2, y2 = p2
    rx1 = rect.x - clearance
    ry1 = rect.y - clearance
    rx2 = rect.right + clearance
    ry2 = rect.bottom + clearance

    dx = x2 - x1
    dy = y2 - y1
    t_enter, t_exit = 0.0, 1.0

    for p, q in [
        (-dx, x1 - rx1),
        (dx, rx2 - x1),
        (-dy, y1 - ry1),
        (dy, ry2 - y1),
    ]:
        if abs(p) < 1e-12:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t_exit:
                    return False
                if t > t_enter:
                    t_enter = t
            else:
                if t < t_enter:
                    return False
                if t < t_exit:
                    t_exit = t

    return t_enter <= t_exit


def polyline_intersects_rect(
    points: Sequence[Tuple[float, float]],
    rect: Rect,
    clearance: float = 0,
) -> bool:
    """折线（多点正交路径）是否与矩形相交：逐段检测"""
    for i in range(len(points) - 1):
        if segment_intersects_rect(points[i], points[i + 1], rect, clearance):
            return True
    return False


def point_in_rect(p: Tuple[float, float], rect: Rect, gap: float = 0) -> bool:
    """点是否在矩形内（含 gap 外扩）"""
    return (
        rect.x - gap <= p[0] <= rect.right + gap
        and rect.y - gap <= p[1] <= rect.bottom + gap
    )


# ============== 文本测量与适配 ==============

# 全宽字符正则：CJK 统一汉字 + 日文 + 韩文 + 全角符号 + emoji 等
_FULLWIDTH_RE = re.compile(
    r"[\u1100-\u115F"  # 韩文 Jamo
    r"\u2E80-\u303E"   # CJK 部首/标点
    r"\u3040-\u33FF"   # 日文假名 + CJK 符号
    r"\u3400-\u4DBF"   # CJK 扩展 A
    r"\u4E00-\u9FFF"   # CJK 统一汉字
    r"\uA000-\uA4CF"   # 彝文
    r"\uAC00-\uD7A3"   # 韩文音节
    r"\uF900-\uFAFF"   # CJK 兼容汉字
    r"\uFE30-\uFE4F"   # CJK 兼容形式
    r"\uFF00-\uFF60"   # 全角 ASCII
    r"\uFFE0-\uFFE6"   # 全角符号
    r"\U0001F000-\U0001F9FF"  # emoji
    r"\U00020000-\U0002FFFD"  # CJK 扩展 B-F
    r"]"
)

# 宽度系数：每个 text unit 每像素字号占多少像素宽
WIDTH_FACTOR = 0.6
# 盒内水平留白（文字不贴边）
HORIZONTAL_PADDING = 8


def text_units(text: Any) -> float:
    """文本宽度单位：全宽字符(CJK/emoji/全角) = 2.0，ASCII = 1.0"""
    if not text:
        return 0.0
    s = str(text)
    units = 0.0
    for ch in s:
        if _FULLWIDTH_RE.match(ch):
            units += 2.0
        else:
            units += 1.0
    return units


def text_width_px(text: Any, font_size: float) -> float:
    """估算文本像素宽度（CJK 全宽 ×字号 + ASCII ×0.58×字号）"""
    if not text:
        return 0.0
    w = 0.0
    for ch in str(text):
        o = ord(ch)
        if o > 0x2E80:
            w += font_size
        elif 0x2000 <= o <= 0x206F:
            w += font_size * 0.55
        elif o == 0x20:
            w += font_size * 0.3
        else:
            w += font_size * 0.58
    return w


def fitted_font_size(
    text: Any, width: float, preferred: float, minimum: float
) -> float:
    """渲染时缩小字号适配盒宽：取 [preferred, minimum] 之间能放下的最大值。

    借鉴 archify fittedNodeFontSize：
      fontSize = min(preferred, (width - padding) / (units × widthFactor))
      floored at minimum（低于 minimum 不再缩小，应由校验报告问题）
    """
    units = max(1.0, text_units(text))
    available = max(1.0, width - HORIZONTAL_PADDING)
    fitted = min(preferred, available / (units * WIDTH_FACTOR))
    return max(minimum, round(fitted * 10) / 10)


def minimum_text_width(text: Any, minimum: float) -> float:
    """文本在最小字号下仍需要的宽度（用于校验：超过盒宽则拒绝）"""
    return text_units(text) * minimum * WIDTH_FACTOR


def available_text_width(width: float) -> float:
    """盒内可用文本宽度"""
    return max(1.0, width - HORIZONTAL_PADDING)


# ============== 质量校验函数 ==============


def clean_overlap_problems(
    rects: List[Tuple[str, Rect]],
    gap: float = 8.0,
) -> List[Problem]:
    """节点重叠检测：任意两个节点间距 < gap px 则报错（硬失败）。

    rects: [(id, Rect), ...]
    """
    problems: List[Problem] = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            id_a, ra = rects[i]
            id_b, rb = rects[j]
            if rects_overlap(ra, rb, gap):
                # 计算重叠量
                ox = min(ra.right, rb.right) - max(ra.x, rb.x)
                oy = min(ra.bottom, rb.bottom) - max(ra.y, rb.y)
                problems.append(
                    Problem(
                        code="layout/node-overlap",
                        severity="error",
                        message=(
                            f'节点 "{id_a}" 与 "{id_b}" 重叠 '
                            f"(水平 {ox:.0f}px × 垂直 {oy:.0f}px，"
                            f"需要至少 {gap:.0f}px 间距)"
                        ),
                        subject={"node_a": id_a, "node_b": id_b},
                        evidence={
                            "rect_a": ra.to_dict(),
                            "rect_b": rb.to_dict(),
                            "overlap_x": round(ox, 1),
                            "overlap_y": round(oy, 1),
                            "required_gap": gap,
                        },
                        supported_fixes=[
                            f'增大 "{id_a}" 或 "{id_b}" 的 y 坐标使间距 ≥ {gap:.0f}px',
                            "缩小其中一个节点的尺寸",
                        ],
                    )
                )
    return problems


def clean_flow_problems(
    edges: List[dict],
    nodes: List[dict],
    clearance: float = 2.0,
) -> List[Problem]:
    """边穿节点检测（硬失败）：边的路径不能穿过非端点节点。

    edges: [{from: id, to: id, points: [(x,y),...]}] 或
           [{from: (x,y), to: (x,y)}]（坐标对形式）
    nodes: [{id, x, y, w, h}]
    """
    problems: List[Problem] = []
    node_rects = {n["id"]: Rect.from_dict(n) for n in nodes if "id" in n}

    for edge in edges:
        from_val = edge.get("from")
        to_val = edge.get("to")
        points = edge.get("points")

        # 确定 skip_ids（端点节点的 id，不检测穿过自身）
        # 支持显式 _skip_ids 字段（坐标对边无法用 from/to 表示端点节点时用）
        skip_ids = set(edge.get("_skip_ids", []) or [])
        if isinstance(from_val, str):
            skip_ids.add(from_val)
        if isinstance(to_val, str):
            skip_ids.add(to_val)

        # 如果没有显式 points，尝试从 from/to 构建
        if points is None:
            if isinstance(from_val, str) and isinstance(to_val, str):
                if from_val in node_rects and to_val in node_rects:
                    ra, rb = node_rects[from_val], node_rects[to_val]
                    points = [(ra.cx, ra.cy), (rb.cx, rb.cy)]
                else:
                    continue
            elif isinstance(from_val, (list, tuple)) and isinstance(
                to_val, (list, tuple)
            ):
                points = [tuple(from_val), tuple(to_val)]
            else:
                continue

        edge_label = f"{from_val}→{to_val}"
        for node in nodes:
            nid = node.get("id", "")
            if nid in skip_ids:
                continue
            rect = Rect.from_dict(node)
            if polyline_intersects_rect(points, rect, clearance):
                problems.append(
                    Problem(
                        code="clean-flow/edge-through-node",
                        severity="error",
                        message=(
                            f"边 {edge_label} 穿过无关节点 \"{nid}\" "
                            f"(clearance {clearance:.0f}px)"
                        ),
                        subject={"edge": edge_label, "node": nid},
                        evidence={
                            "edge_points": [list(p) for p in points],
                            "node_rect": rect.to_dict(),
                        },
                        supported_fixes=[
                            f"调整边 {edge_label} 的路由绕过节点 \"{nid}\"",
                            "为边添加 via 中转点",
                            f'移动节点 "{nid}" 或调整其尺寸',
                        ],
                    )
                )
    return problems


def clean_out_of_bounds(
    rects: List[Tuple[str, Rect]],
    canvas_w: float,
    canvas_h: float,
    margin: float = 20.0,
) -> List[Problem]:
    """出界检测（硬失败）：节点不能超出画布边界（含 margin 留白）"""
    problems: List[Problem] = []
    for rid, r in rects:
        if r.x < margin:
            problems.append(
                Problem(
                    code="layout/out-of-bounds",
                    severity="error",
                    message=(
                        f'节点 "{rid}" 左端 {r.x:.0f}px 超出画布左边界'
                        f"（需要 ≥ {margin:.0f}px 留白）"
                    ),
                    subject={"node": rid, "side": "left"},
                    evidence={"rect": r.to_dict(), "canvas_w": canvas_w},
                    supported_fixes=[f"增大 \"{rid}\" 的 x 坐标至 ≥ {margin:.0f}"],
                )
            )
        if r.y < margin:
            problems.append(
                Problem(
                    code="layout/out-of-bounds",
                    severity="error",
                    message=(
                        f'节点 "{rid}" 顶端 {r.y:.0f}px 超出画布上边界'
                        f"（需要 ≥ {margin:.0f}px 留白）"
                    ),
                    subject={"node": rid, "side": "top"},
                    evidence={"rect": r.to_dict(), "canvas_h": canvas_h},
                    supported_fixes=[f"增大 \"{rid}\" 的 y 坐标至 ≥ {margin:.0f}"],
                )
            )
        if r.right > canvas_w - margin:
            problems.append(
                Problem(
                    code="layout/out-of-bounds",
                    severity="error",
                    message=(
                        f'节点 "{rid}" 右端 {r.right:.0f}px 超出画布右边界'
                        f"（画布宽 {canvas_w:.0f}px，需要 ≤ {canvas_w - margin:.0f}px）"
                    ),
                    subject={"node": rid, "side": "right"},
                    evidence={"rect": r.to_dict(), "canvas_w": canvas_w},
                    supported_fixes=[
                        f"减小 \"{rid}\" 的 x 坐标或宽度，使右端 ≤ {canvas_w - margin:.0f}px",
                        f"增大 canvas.width 至 ≥ {r.right + margin:.0f}px",
                    ],
                )
            )
        if r.bottom > canvas_h - margin:
            problems.append(
                Problem(
                    code="layout/out-of-bounds",
                    severity="error",
                    message=(
                        f'节点 "{rid}" 底端 {r.bottom:.0f}px 超出画布下边界'
                        f"（画布高 {canvas_h:.0f}px，需要 ≤ {canvas_h - margin:.0f}px）"
                    ),
                    subject={"node": rid, "side": "bottom"},
                    evidence={"rect": r.to_dict(), "canvas_h": canvas_h},
                    supported_fixes=[
                        f"减小 \"{rid}\" 的 y 坐标或高度，使底端 ≤ {canvas_h - margin:.0f}px",
                        f"增大 canvas.height 至 ≥ {r.bottom + margin:.0f}px",
                    ],
                )
            )
    return problems


def clean_text_overflow(
    text_items: List[dict],
) -> List[Problem]:
    """文本超宽检测（硬失败）：文本在最小字号下仍超过盒宽则拒绝。

    text_items: [{id, text, width, minimum_fontsize}]
    """
    problems: List[Problem] = []
    for item in text_items:
        tid = item.get("id", "?")
        text = item.get("text", "")
        width = item.get("width", 0)
        min_fs = item.get("minimum_fontsize", 6)
        needed = minimum_text_width(text, min_fs)
        available = available_text_width(width)
        if needed > available:
            problems.append(
                Problem(
                    code="layout/text-overflow",
                    severity="error",
                    message=(
                        f'文本 "{text}" 在最小字号 {min_fs}px 下仍需 {needed:.0f}px 宽，'
                        f"超过盒宽 {width:.0f}px（可用 {available:.0f}px）"
                    ),
                    subject={"id": tid, "text": text},
                    evidence={
                        "text": text,
                        "needed_width": round(needed, 1),
                        "available_width": round(available, 1),
                        "minimum_fontsize": min_fs,
                    },
                    supported_fixes=[
                        f"增大 \"{tid}\" 的宽度至 ≥ {needed + HORIZONTAL_PADDING:.0f}px",
                        "缩短文本内容",
                        "允许文本换行",
                    ],
                )
            )
    return problems


def validate_references(
    refs: List[Tuple[str, str, str]],
    valid_ids: set,
) -> List[Problem]:
    """引用完整性检测（硬失败）：边引用的节点 id 必须存在。

    refs: [(edge_id, field, referenced_id), ...]
    """
    problems: List[Problem] = []
    for edge_id, field, ref_id in refs:
        if ref_id not in valid_ids:
            problems.append(
                Problem(
                    code="schema/broken-reference",
                    severity="error",
                    message=(
                        f"边 \"{edge_id}\" 的 {field}=\"{ref_id}\" "
                        f"引用了不存在的节点"
                    ),
                    subject={"edge": edge_id, "field": field, "ref": ref_id},
                    evidence={"valid_ids": sorted(valid_ids)[:20]},
                    supported_fixes=[
                        f'添加 id="{ref_id}" 的节点',
                        f"修正 {field} 为已存在的节点 id",
                    ],
                )
            )
    return problems


# ============== 自动端口扇出 ==============


def automatic_port_spread(
    relations: List[dict],
    side: str,
    side_length: float,
    gutter: float = 16.0,
    max_spacing: float = 14.0,
) -> Dict[str, float]:
    """自动端口扇出：多条连接共享同一组件同一侧时，对称分布端点避免堆叠。

    借鉴 archify automaticPortSpread：
      - 按 `(component_id, side)` 分组共享端点的连接
      - 每组 < 2 条不扇出
      - 按对端中心坐标排序（确定性）
      - spacing = min(max_spacing, (side_length - 2×gutter) / (n-1))
      - offset = (index - (n-1)/2) × spacing，绕侧中点对称分布

    relations: [{id, component_id, peer_cx, peer_cy}]
      - peer_cx/peer_cy: 对端组件的中心坐标（用于排序）
    side: "left" | "right" | "top" | "bottom"
    side_length: 该侧的长度（left/right 用 height，top/bottom 用 width）

    返回: {relation_id: offset}（相对于侧中点的偏移量）
    """
    # 按 component_id 分组
    groups: Dict[str, List[dict]] = {}
    for rel in relations:
        cid = rel.get("component_id", "")
        groups.setdefault(cid, []).append(rel)

    result: Dict[str, float] = {}
    for cid, group in groups.items():
        if len(group) < 2:
            continue
        # 按对端坐标排序（侧是 left/right 时按 peer_cy，top/bottom 时按 peer_cx）
        sort_key = "peer_cy" if side in ("left", "right") else "peer_cx"
        sorted_group = sorted(group, key=lambda r: (r.get(sort_key, 0), r.get("id", "")))
        n = len(sorted_group)

        # 计算间距
        usable = side_length - 2 * gutter
        if usable <= 0:
            continue
        spacing = min(max_spacing, usable / (n - 1)) if n > 1 else 0
        if spacing <= 0:
            continue

        # 对称分布
        for i, rel in enumerate(sorted_group):
            offset = (i - (n - 1) / 2) * spacing
            result[rel["id"]] = round(offset, 1)

    return result


# ============== 批量校验入口 ==============


def report_problems(problems: List[Problem]) -> bool:
    """打印所有 Problem 并返回是否通过（0 problem = pass）"""
    errors = [p for p in problems if p.severity == "error"]
    warnings = [p for p in problems if p.severity == "warning"]

    if not problems:
        return True

    if errors:
        print(f"  ❌ {len(errors)} 个错误:")
        for p in errors:
            print(p)
    if warnings:
        print(f"  ⚠️ {len(warnings)} 个警告:")
        for p in warnings:
            print(p)

    return len(errors) == 0
