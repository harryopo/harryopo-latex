#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
super-diagram v2.1 渲染引擎（论文白主题）
=========================================
输入：JSON（canvas + nodes + edges，坐标由 LLM 算好）
处理：正交箭头路由 + 避障 + 质量校验
输出：SVG + PNG + HTML（自适应宽度）

设计原则（对标学术论文架构图）：
1. 白底、灰框、细线、黑字（可打印、可嵌入论文）
2. 横平竖直严格对齐：所有节点中心对齐到网格
3. 箭头正交：只走水平/垂直，Z 形/L 形路由
4. 直接输出 PNG（playwright 截图 SVG）

用法：
  python render_v2.py input.json -o output.png
  python render_v2.py input.json -o output.png --scale 2
  python render_v2.py input.json -o output.svg
  python render_v2.py input.json -o output.html
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

# Windows GBK 终端兼容：强制 stdout/stderr 用 UTF-8（emoji/中文不崩）
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 共享几何校验库（项目根 shared/diagram_geometry.py）
# 优先用环境变量 DIAGRAM_SHARED_DIR，否则从脚本位置向上查找项目根
def _find_shared_geometry():
    """向上遍历查找 shared/diagram_geometry.py（跳过 .trae 内目录——
    skill 内嵌副本会抢先命中，与 office.py _find_project_root 同理）"""
    cur = Path(__file__).resolve().parent
    for parent in [cur] + list(cur.parents):
        if '.trae' in parent.parts:
            continue
        cand = parent / 'shared' / 'diagram_geometry.py'
        if cand.exists():
            return cand
    return None

_SHARED_CANDIDATES = [
    Path(os.environ.get("DIAGRAM_SHARED_DIR", "")) / "diagram_geometry.py",
    _find_shared_geometry() or Path("_nonexistent_"),
]
_SHARED_FOUND = None
for _cand in _SHARED_CANDIDATES:
    if _cand.exists():
        sys.path.insert(0, str(_cand.parent))
        _SHARED_FOUND = _cand.parent
        break

if _SHARED_FOUND:
    from diagram_geometry import (
        Rect, Problem, report_problems,
        clean_overlap_problems, clean_flow_problems, clean_out_of_bounds,
        clean_text_overflow, validate_references, text_units, fitted_font_size,
        automatic_port_spread,
    )
else:
    # 无共享库时降级（不阻塞渲染）
    Rect = Problem = report_problems = None
    automatic_port_spread = None

# ============== 论文白色主题 ==============

LIGHT = {
    "bg": "#FFFFFF", "grid": "#F3F4F6", "border": "#D1D5DB",
    "text": "#111827", "text_sec": "#6B7280", "arrow": "#374151",
    # 论文风格：低饱和度、可打印
    "backend": "#2563EB", "db": "#7C3AED", "frontend": "#059669",
    "bus": "#D97706", "security": "#DC2626", "cloud": "#D97706",
    "external": "#6B7280",
}
LIGHT_FILL = {
    "backend": "#EFF6FF", "db": "#F5F3FF", "frontend": "#ECFDF5",
    "bus": "#FFFBEB", "security": "#FEF2F2", "cloud": "#FFFBEB",
    "external": "#F9FAFB",
}

FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,"PingFang SC","Microsoft YaHei",sans-serif'

# ============== 工具函数 ==============

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def rects_overlap(a, b, padding=0):
    return not (
        a["x"] + a["w"] + padding <= b["x"]
        or b["x"] + b["w"] + padding <= a["x"]
        or a["y"] + a["h"] + padding <= b["y"]
        or b["y"] + b["h"] + padding <= a["y"]
    )


# ============== 质量校验 ==============

def validate(data):
    """校验：architecture（nodes+edges）走完整质量校验；sequence 校验消息引用完整性。
    返回 Problem 对象列表（空列表 = 通过）。"""
    if data.get("type") == "sequence":
        return validate_sequence(data)

    # 无共享库时降级到旧的字符串校验
    if Rect is None:
        return _validate_legacy(data)

    canvas = data["canvas"]
    nodes = data["nodes"]
    edges = data.get("edges", [])
    W, H = canvas["width"], canvas["height"]
    node_map = {n["id"]: n for n in nodes}

    problems: list = []

    # 1. 引用完整性（硬失败）
    refs = []
    for e in edges:
        eid = e.get("from", "?") + "->" + e.get("to", "?")
        refs.append((eid, "from", e.get("from")))
        refs.append((eid, "to", e.get("to")))
    problems.extend(validate_references(refs, set(node_map.keys())))

    # 只对有效引用继续做几何校验
    valid_edges = [e for e in edges if e.get("from") in node_map and e.get("to") in node_map]
    valid_node_ids = {e["from"] for e in valid_edges} | {e["to"] for e in valid_edges}

    # 2. 节点重叠（硬失败，gap=10px）
    node_rects = [(n["id"], Rect.from_dict(n)) for n in nodes]
    problems.extend(clean_overlap_problems(node_rects, gap=10))

    # 3. 出界检测（硬失败）
    problems.extend(clean_out_of_bounds(node_rects, W, H, margin=20))

    # 4. 边穿节点（硬失败）——用 route_edge 算出的实际路径检测
    #    与渲染一致：应用端口扇出偏移（compute_port_offsets 内部第一轮路由与渲染同参）
    #    判据与 route_edge 的 _path_ok 对齐（严格内判定），避免"贴边被 clearance 误判穿"的假阳性
    port_offsets = compute_port_offsets(valid_edges, nodes, node_map)
    for ei, e in enumerate(valid_edges):
        fn = node_map[e["from"]]
        tn = node_map[e["to"]]
        from_off, to_off = port_offsets.get(ei, ((0, 0), (0, 0)))
        pts = route_edge(fn, tn, nodes, from_off=from_off, to_off=to_off)
        skip = {e["from"], e["to"]}
        if not _path_ok(pts, nodes, skip, fn, tn):
            problems.append(Problem(
                code="clean-flow/edge-through-node",
                severity="error",
                message=f"边 {e['from']}→{e['to']} 的实际路由穿过无关节点",
                subject={"edge": f"{e['from']}→{e['to']}"},
                evidence={"edge_points": [list(p) for p in pts]},
                supported_fixes=[
                    f"调整边 {e['from']}→{e['to']} 的路由绕过障碍",
                    f'移动遮挡节点或调整其尺寸',
                ],
            ))

    # 5. 文本超宽（硬失败）——检测节点 label 是否放得下
    text_items = []
    for n in nodes:
        label = n.get("label", n.get("en", ""))
        if label:
            text_items.append({
                "id": n["id"],
                "text": label,
                "width": n["w"],
                "minimum_fontsize": 7,
            })
    problems.extend(clean_text_overflow(text_items))

    return problems


def _validate_legacy(data):
    """无共享库时的降级校验（保持向后兼容）"""
    errors = []
    canvas = data["canvas"]
    nodes = data["nodes"]
    edges = data.get("edges", [])
    W, H = canvas["width"], canvas["height"]
    node_map = {n["id"]: n for n in nodes}

    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if rects_overlap(a, b, padding=10):
                errors.append(f"节点重叠: {a['id']} ↔ {b['id']}")

    for n in nodes:
        if n["x"] < 20:
            errors.append(f"节点出界(左): {n['id']} x={n['x']}")
        if n["y"] < 20:
            errors.append(f"节点出界(上): {n['id']} y={n['y']}")
        if n["x"] + n["w"] > W - 20:
            errors.append(f"节点出界(右): {n['id']} 右端={n['x']+n['w']} 画布宽={W}")
        if n["y"] + n["h"] > H - 20:
            errors.append(f"节点出界(下): {n['id']} 下端={n['y']+n['h']} 画布高={H}")

    for e in edges:
        if e["from"] not in node_map:
            errors.append(f"边引用了不存在的节点: {e['from']}")
        if e["to"] not in node_map:
            errors.append(f"边引用了不存在的节点: {e['to']}")

    return errors


def validate_sequence(data):
    """时序图校验：消息引用的参与者必须存在（返回 Problem 列表，与 validate() 统一形态）"""
    problems = []
    participants = data.get("participants", [])
    pid = {p.get("id", p.get("en", p.get("label", ""))) for p in participants}

    if Problem is not None:
        for m in data.get("messages", []):
            mid = m.get("from", "?") + "->" + m.get("to", "?")
            if m.get("from") not in pid:
                problems.append(Problem(
                    code="schema/broken-reference",
                    severity="error",
                    message=f'消息 "{mid}" 的 from="{m.get("from")}" 引用了不存在的参与者',
                    subject={"message": mid, "field": "from", "ref": m.get("from")},
                    evidence={"valid_ids": sorted(pid)[:20]},
                    supported_fixes=[f'添加 id="{m.get("from")}" 的参与者', "修正 from 为已存在的参与者 id"],
                ))
            if m.get("to") not in pid:
                problems.append(Problem(
                    code="schema/broken-reference",
                    severity="error",
                    message=f'消息 "{mid}" 的 to="{m.get("to")}" 引用了不存在的参与者',
                    subject={"message": mid, "field": "to", "ref": m.get("to")},
                    evidence={"valid_ids": sorted(pid)[:20]},
                    supported_fixes=[f'添加 id="{m.get("to")}" 的参与者', "修正 to 为已存在的参与者 id"],
                ))
    else:
        # 降级：无共享库时返回字符串列表
        for m in data.get("messages", []):
            if m.get("from") not in pid:
                problems.append(f"消息引用不存在的参与者(from): {m.get('from')}")
            if m.get("to") not in pid:
                problems.append(f"消息引用不存在的参与者(to): {m.get('to')}")

    return problems


# ============== 端口扇出（多条边共享节点时端点错开） ==============

def _detect_side(p1, p2):
    """从线段方向推断出发/到达侧：返回 "top"/"bottom"/"left"/"right"
    p1 是节点端点，p2 是路径的下一个点"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    return "bottom" if dy > 0 else "top"


def compute_port_offsets(edges, nodes, node_map):
    """两轮路由端口扇出：多条边共享同一节点的同一侧时，端点对称错开。
    返回 {edge_idx: (from_off, to_off)}，off = (dx, dy)"""
    if automatic_port_spread is None:
        return {}

    # 第一轮路由：确定每条边的出口/入口侧
    edge_sides = {}
    for i, e in enumerate(edges):
        fn = node_map.get(e["from"])
        tn = node_map.get(e["to"])
        if not fn or not tn:
            continue
        pts = route_edge(fn, tn, nodes)
        from_side = _detect_side(pts[0], pts[1])
        to_side = _detect_side(pts[-1], pts[-2])
        edge_sides[i] = (from_side, to_side)

    # 按 (node_id, side, role) 分组共享端点的边
    groups = {}
    for i, e in enumerate(edges):
        if i not in edge_sides:
            continue
        fn, tn = node_map[e["from"]], node_map[e["to"]]
        fcx, fcy = fn["x"] + fn["w"] / 2, fn["y"] + fn["h"] / 2
        tcx, tcy = tn["x"] + tn["w"] / 2, tn["y"] + tn["h"] / 2
        from_side, to_side = edge_sides[i]

        groups.setdefault((e["from"], from_side, "from"), []).append({
            "id": str(i), "component_id": e["from"],
            "peer_cx": tcx, "peer_cy": tcy,
        })
        groups.setdefault((e["to"], to_side, "to"), []).append({
            "id": str(i), "component_id": e["to"],
            "peer_cx": fcx, "peer_cy": fcy,
        })

    # 对每组调用 automatic_port_spread
    raw = {}  # edge_idx -> {"from": (dx,dy), "to": (dx,dy)}
    for (nid, side, role), rels in groups.items():
        n = node_map[nid]
        side_len = n["h"] if side in ("left", "right") else n["w"]
        spread = automatic_port_spread(rels, side, side_len)
        for eid_str, off in spread.items():
            ei = int(eid_str)
            raw.setdefault(ei, {"from": (0, 0), "to": (0, 0)})
            # port_spread offset 沿侧方向：left/right→dy，top/bottom→dx
            if side in ("left", "right"):
                raw[ei][role] = (0, off)
            else:
                raw[ei][role] = (off, 0)

    # 安全回退：偏移后的路径若穿节点则逐边回退偏移（借鉴 archify "过滤失败即放弃"）。
    # 保证渲染路径与校验一致、且绝不因扇出引入新穿节点。
    safe = {}
    for ei, pair in raw.items():
        foff, toff = pair["from"], pair["to"]
        e = edges[ei]
        fn, tn = node_map[e["from"]], node_map[e["to"]]
        skip = {fn["id"], tn["id"]}
        pts = route_edge(fn, tn, nodes, from_off=foff, to_off=toff)
        if _path_ok(pts, nodes, skip, fn, tn):
            safe[ei] = (foff, toff)
            continue
        # 尝试只回退 from 偏移
        pts = route_edge(fn, tn, nodes, from_off=(0, 0), to_off=toff)
        if _path_ok(pts, nodes, skip, fn, tn):
            safe[ei] = ((0, 0), toff)
            continue
        # 尝试只回退 to 偏移
        pts = route_edge(fn, tn, nodes, from_off=foff, to_off=(0, 0))
        if _path_ok(pts, nodes, skip, fn, tn):
            safe[ei] = (foff, (0, 0))
            continue
        # 全部失败 → 放弃该边扇出（保持无偏移原始路径）
        safe[ei] = ((0, 0), (0, 0))

    return safe


# ============== 箭头路由（严格正交） ==============

def _line_blocked(x1, y1, x2, y2, nodes, skip_ids):
    """检查正交线段 [p1,p2] 是否穿过非 skip 节点的内部（排除端点贴边）"""
    for n in nodes:
        if n["id"] in skip_ids:
            continue
        nx1, nx2 = n["x"], n["x"] + n["w"]
        ny1, ny2 = n["y"], n["y"] + n["h"]
        if x1 == x2:  # 垂直线
            if nx1 < x1 < nx2:
                lo, hi = min(y1, y2), max(y1, y2)
                if ny1 < hi and ny2 > lo:
                    return True
        else:  # 水平线
            if ny1 < y1 < ny2:
                lo, hi = min(x1, x2), max(x1, x2)
                if nx1 < hi and nx2 > lo:
                    return True
    return False


def _detour_y(sx, tx, sy, nodes, skip_ids):
    """水平直线被节点挡住时，找最近的折弯走廊 y（上下两侧，向外扩到不撞为止）"""
    blockers = []
    for n in nodes:
        if n["id"] in skip_ids:
            continue
        nx1, nx2 = n["x"], n["x"] + n["w"]
        ny1, ny2 = n["y"], n["y"] + n["h"]
        xlo, xhi = min(sx, tx), max(sx, tx)
        if ny1 < sy < ny2 and nx1 < xhi and nx2 > xlo:
            blockers.append((ny1, ny2))
    if not blockers:
        return sy
    cands = []
    for ny, sign in ((min(ny1 for ny1, _ in blockers) - 30, -1),
                     (max(ny2 for _, ny2 in blockers) + 30, 1)):
        y = ny
        while True:
            ok = True
            for n in nodes:
                if n["id"] in skip_ids:
                    continue
                nx1, nx2 = n["x"], n["x"] + n["w"]
                ny1, ny2 = n["y"], n["y"] + n["h"]
                xlo, xhi = min(sx, tx), max(sx, tx)
                if ny1 < y < ny2 and nx1 < xhi and nx2 > xlo:
                    ok = False
                    break
            if ok:
                cands.append((abs(y - sy), y))
                break
            y += sign * 30
    cands.sort(key=lambda t: t[0])
    return cands[0][1]


def _detour_x(sy, ty, sx, nodes, skip_ids):
    """垂直直线被节点挡住时，找最近的折弯走廊 x（左右两侧，向外扩到不撞为止）"""
    blockers = []
    for n in nodes:
        if n["id"] in skip_ids:
            continue
        nx1, nx2 = n["x"], n["x"] + n["w"]
        ny1, ny2 = n["y"], n["y"] + n["h"]
        ylo, yhi = min(sy, ty), max(sy, ty)
        if nx1 < sx < nx2 and ny1 < yhi and ny2 > ylo:
            blockers.append((nx1, nx2))
    if not blockers:
        return sx
    cands = []
    for nx, sign in ((min(nx1 for nx1, _ in blockers) - 30, -1),
                     (max(nx2 for _, nx2 in blockers) + 30, 1)):
        x = nx
        while True:
            ok = True
            for n in nodes:
                if n["id"] in skip_ids:
                    continue
                nx1, nx2 = n["x"], n["x"] + n["w"]
                ny1, ny2 = n["y"], n["y"] + n["h"]
                ylo, yhi = min(sy, ty), max(sy, ty)
                if nx1 < x < nx2 and ny1 < yhi and ny2 > ylo:
                    ok = False
                    break
            if ok:
                cands.append((abs(x - sx), x))
                break
            x += sign * 30
    cands.sort(key=lambda t: t[0])
    return cands[0][1]


def _seg_in_node_len(x1, y1, x2, y2, n):
    """正交线段在节点 n 内部的长度（像素）；不相交返回 0"""
    nx1, nx2 = n["x"], n["x"] + n["w"]
    ny1, ny2 = n["y"], n["y"] + n["h"]
    if x1 == x2:  # 垂直线
        if not (nx1 < x1 < nx2):
            return 0
        lo, hi = max(ny1, min(y1, y2)), min(ny2, max(y1, y2))
        return max(0, hi - lo)
    if y1 == y2:  # 水平线
        if not (ny1 < y1 < ny2):
            return 0
        lo, hi = max(nx1, min(x1, x2)), min(nx2, max(x1, x2))
        return max(0, hi - lo)
    return 0


def _path_ok(pts, nodes, skip_ids, from_n=None, to_n=None):
    """整条正交折线合格：①所有段不穿过非 skip 节点；②任一段不得横穿 from/to 节点内部（>8px）"""
    for k in range(len(pts) - 1):
        if _line_blocked(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], nodes, skip_ids):
            return False
    if from_n is not None and to_n is not None:
        for k in range(len(pts) - 1):
            x1, y1 = pts[k]
            x2, y2 = pts[k + 1]
            if _seg_in_node_len(x1, y1, x2, y2, from_n) > 8 or \
               _seg_in_node_len(x1, y1, x2, y2, to_n) > 8:
                return False
    return True


def _inside(x, y, n):
    """点 (x,y) 是否在节点 n 内部（严格内）"""
    return n["x"] < x < n["x"] + n["w"] and n["y"] < y < n["y"] + n["h"]


def _corridor_path(sx, sy, tx, ty, from_n, to_n, nodes, skip_ids):
    """通用走廊绕行（兜底）：走廊取所有节点边界 ±30，按离起点距离近优先，
    构造 2 拐弯正交路径，返回第一条无碰撞且出发段不横穿端点节点的。
    变体 A：先水平后垂直；变体 B：先垂直后水平。找不到返回 None。"""
    xs, ys = set(), set()
    for n in nodes:
        if n["id"] in skip_ids:
            continue
        xs.add(n["x"] - 30)
        xs.add(n["x"] + n["w"] + 30)
        ys.add(n["y"] - 30)
        ys.add(n["y"] + n["h"] + 30)
    xs.add(sx); xs.add(tx)
    ys.add(sy); ys.add(ty)
    xs = sorted((v for v in xs if 20 <= v <= 2000), key=lambda v: abs(v - sx))
    ys = sorted((v for v in ys if 20 <= v <= 2000), key=lambda v: abs(v - sy))
    # 变体 A：先水平后垂直（走廊 x）
    for x in xs:
        if abs(x - sx) < 20 and abs(x - tx) < 20:
            continue
        if _inside((sx + x) / 2, sy, from_n) or _inside((sx + x) / 2, sy, to_n):
            continue  # 出发段横穿端点节点
        pts = [(sx, sy), (x, sy), (x, ty), (tx, ty)]
        if _path_ok(pts, nodes, skip_ids, from_n, to_n):
            return pts
    # 变体 B：先垂直后水平（走廊 y）
    for y in ys:
        if abs(y - sy) < 20 and abs(y - ty) < 20:
            continue
        if _inside(sx, (sy + y) / 2, from_n) or _inside(sx, (sy + y) / 2, to_n):
            continue
        pts = [(sx, sy), (sx, y), (tx, y), (tx, ty)]
        if _path_ok(pts, nodes, skip_ids, from_n, to_n):
            return pts
    return None


def _edge_penalty(pts, nodes, skip_ids):
    """贴边惩罚：路径与节点边界贴线并横穿的节点数（0=无贴边横穿）。
    贴边横穿 ≥2 个节点边界会被 route_edge 过滤（视觉上被方块边框咬住）。"""
    n_hit = 0
    for k in range(len(pts) - 1):
        x1, y1 = pts[k]
        x2, y2 = pts[k + 1]
        for n in nodes:
            if n["id"] in skip_ids:
                continue
            nx1, nx2 = n["x"], n["x"] + n["w"]
            ny1, ny2 = n["y"], n["y"] + n["h"]
            if x1 == x2:  # 垂直线贴左右边界
                if abs(x1 - nx1) < 1 or abs(x1 - nx2) < 1:
                    lo, hi = min(y1, y2), max(y1, y2)
                    if ny1 < hi and ny2 > lo:
                        n_hit += 1
            else:  # 水平线贴上下边界
                if abs(y1 - ny1) < 1 or abs(y1 - ny2) < 1:
                    lo, hi = min(x1, x2), max(x1, x2)
                    if nx1 < hi and nx2 > lo:
                        n_hit += 1
    return n_hit


def _path_len(pts):
    """正交折线总曼哈顿长度"""
    return sum(abs(pts[k + 1][0] - pts[k][0]) + abs(pts[k + 1][1] - pts[k][1])
               for k in range(len(pts) - 1))


def route_edge(from_n, to_n, all_nodes, from_off=(0, 0), to_off=(0, 0)):
    """严格正交路由（候选集合 + 全段碰撞校验，按段数优先选最优）。
    from_off/to_off: 端口扇出偏移 (dx, dy)——dx 影响上下边界 x 位置，dy 影响左右边界 y 位置。
    策略：
    - 候选来源 1：16 种出口组合（from 4 边界中心 × to 4 边界中心），
      各生成「先垂直后水平」与「先水平后垂直」两条 L 形（同 x/同 y 退化为直线）→ 天然 2~3 段
    - 候选来源 2：走廊偏移候选（多 midx/midy，含端点本身走廊）→ 复杂遮挡时 4 段
    - 候选来源 3：_corridor_path 通用走廊兜底（极端情况）
    - 全部候选经 _path_ok 校验（非端点碰撞 + from/to 内部横穿），
      按（段数，总长度）排序，选最简洁合规路径
    返回点列表 [(x,y), ...]（相邻两点 x 相同或 y 相同，保证横平竖直）
    """
    fx1, fy1 = from_n["x"], from_n["y"]
    fx2, fy2 = from_n["x"] + from_n["w"], from_n["y"] + from_n["h"]
    tx1, ty1 = to_n["x"], to_n["y"]
    tx2, ty2 = to_n["x"] + to_n["w"], to_n["y"] + to_n["h"]
    fcx, fcy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
    tcx, tcy = (tx1 + tx2) / 2, (ty1 + ty2) / 2
    skip = {from_n["id"], to_n["id"]}
    dx, dy = tcx - fcx, tcy - fcy
    cands = []

    # 1) 出口组合 L 形（from 4 边界中心 × to 4 边界中心）
    #    端口扇出偏移：上下边界偏移 dx，左右边界偏移 dy
    from_exits = [(fcx + from_off[0], fy1), (fcx + from_off[0], fy2),
                  (fx1, fcy + from_off[1]), (fx2, fcy + from_off[1])]
    to_entries = [(tcx + to_off[0], ty1), (tcx + to_off[0], ty2),
                  (tx1, tcy + to_off[1]), (tx2, tcy + to_off[1])]
    for sx, sy in from_exits:
        for tx, ty in to_entries:
            # 变体 A：先垂直后水平（同 x 且中心对齐 → 垂直直线）
            if abs(sx - tx) <= 0.5:
                if abs(sx - fcx) <= 0.5 and abs(tx - tcx) <= 0.5 and abs(sy - ty) > 0.5:
                    cands.append([(sx, sy), (sx, ty)])
            else:
                cands.append([(sx, sy), (sx, ty), (tx, ty)])
            # 变体 B：先水平后垂直（同 y 且中心对齐 → 水平直线）
            if abs(sy - ty) <= 0.5:
                if abs(sy - fcy) <= 0.5 and abs(ty - tcy) <= 0.5 and abs(sx - tx) > 0.5:
                    cands.append([(sx, sy), (tx, sy)])
            elif abs(sx - tx) > 0.5:
                cands.append([(sx, sy), (tx, sy), (tx, ty)])

    # 2) 走廊偏移候选（复杂遮挡：多 midx/midy，含端点本身走廊 → 3 段）
    sx, tx = (fx2, tx1) if dx > 0 else (fx1, tx2)
    for midx in (round((sx + tx) / 2 / 20) * 20, sx + 40, tx - 40,
                 sx - 40, tx + 40, fcx, tcx, sx, tx):
        midx = _avoid_vertical(midx, fcy, tcy, all_nodes, skip)
        cands.append([(sx, fcy), (midx, fcy), (midx, tcy), (tx, tcy)])
    sy, ty = (fy2, ty1) if dy > 0 else (fy1, ty2)
    for midy in (round((sy + ty) / 2 / 20) * 20, sy - 40, ty + 40,
                 sy + 40, ty - 40, fcy, tcy, sy, ty):
        midy = _avoid_horizontal(midy, fcx, tcx, all_nodes, skip)
        cands.append([(fcx, sy), (fcx, midy), (tcx, midy), (tcx, ty)])

    # 去重 + 全段碰撞校验 + 贴边过滤（贴边横穿 ≥2 个节点边界视为视觉缺陷）
    seen = set()
    valid = []
    for pts in cands:
        key = tuple(pts)
        if key in seen:
            continue
        seen.add(key)
        if _path_ok(pts, all_nodes, skip, from_n, to_n) \
                and _edge_penalty(pts, all_nodes, skip) < 2:
            valid.append(pts)
    if not valid:  # 无低贴边路径 → 放宽（允许贴边，保底有解）
        for pts in cands:
            key = tuple(pts)
            if key in seen:
                continue
            seen.add(key)
            if _path_ok(pts, all_nodes, skip, from_n, to_n):
                valid.append(pts)
    if valid:
        valid.sort(key=lambda p: (len(p), _path_len(p)))
        return valid[0]

    # 3) 兜底：通用走廊绕行（按主方向选出口，辅方向补试；出发段不横穿端点节点）
    if abs(dy) >= abs(dx):
        sy, ty = (fy2, ty1) if dy > 0 else (fy1, ty2)
        det = _corridor_path(fcx, sy, tcx, ty, from_n, to_n, all_nodes, skip)
        if not det:
            sx, tx = (fx2, tx1) if dx > 0 else (fx1, tx2)
            det = _corridor_path(sx, fcy, tx, tcy, from_n, to_n, all_nodes, skip)
    else:
        sx, tx = (fx2, tx1) if dx > 0 else (fx1, tx2)
        det = _corridor_path(sx, fcy, tx, tcy, from_n, to_n, all_nodes, skip)
        if not det:
            sy, ty = (fy2, ty1) if dy > 0 else (fy1, ty2)
            det = _corridor_path(fcx, sy, tcx, ty, from_n, to_n, all_nodes, skip)
    if det:
        return det
    return cands[0]


def _avoid_vertical(x, y1, y2, nodes, skip_ids):
    """垂直走廊避障：如果 x 处的垂直线 [y1,y2] 撞上节点，偏移 x"""
    ymin, ymax = min(y1, y2), max(y1, y2)
    # 收集所有撞上的节点的 x 边界
    blockers = []
    for n in nodes:
        if n["id"] in skip_ids:
            continue
        nx1, nx2 = n["x"], n["x"] + n["w"]
        ny1, ny2 = n["y"], n["y"] + n["h"]
        if nx1 < x < nx2 and ny1 < ymax and ny2 > ymin:
            blockers.append((nx1, nx2))
    if not blockers:
        return x
    # 尝试候选 x：所有 blocker 的边界 ±10/±20/±30px（细粒度优先，走廊尽量贴边）
    candidates = [x]
    for nx1, nx2 in blockers:
        candidates.extend([nx1 - 10, nx1 - 20, nx1 - 30,
                           nx2 + 10, nx2 + 20, nx2 + 30])
    candidates = [round(c / 10) * 10 for c in candidates if 60 < c < 2000]
    # 选离原 x 最近的、不撞任何节点的
    candidates.sort(key=lambda c: abs(c - x))
    for c in candidates:
        ok = True
        for n in nodes:
            if n["id"] in skip_ids:
                continue
            nx1, nx2 = n["x"], n["x"] + n["w"]
            ny1, ny2 = n["y"], n["y"] + n["h"]
            if nx1 < c < nx2 and ny1 < ymax and ny2 > ymin:
                ok = False
                break
        if ok:
            return c
    return x


def _avoid_horizontal(y, x1, x2, nodes, skip_ids):
    """水平走廊避障（复用 _avoid_vertical 的逻辑，交换 x/y）"""
    rotated = [{"id": n["id"], "x": n["y"], "y": n["x"],
                "w": n["h"], "h": n["w"]} for n in nodes]
    return _avoid_vertical(y, x1, x2, rotated, skip_ids)


def place_edge_label(pts, nodes, label, used_boxes, W, H):
    """边标签避让放置（论文图规范：标注落在线上，且不盖任何节点/其他标签）
    1. 候选位置：每条段的中心 + 沿段方向 ±22px 步进偏移（受段长约束，不越过段端点）
    2. 段按长度降序（空间大优先）、偏移按距离升序 → 取第一个"不撞任何节点、
       不撞已放置标签、不超画布边界"的位置
    3. 兜底：全部位置都撞 → 选"盖节点总面积最小"处（视觉影响最轻）
    返回 (mx, my, box)
    """
    bg_w = max(50, int(_text_w(str(label), 10)) + 14)
    bg_h = 18
    cands = []  # (段长, |偏移|, mx, my)
    for k in range(len(pts) - 1):
        x1, y1 = pts[k]
        x2, y2 = pts[k + 1]
        L = abs(x2 - x1) + abs(y2 - y1)
        seg_len = abs(x2 - x1) if y1 == y2 else abs(y2 - y1)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        offsets = [0]
        off = 22
        while off < seg_len / 2 - 12:   # 偏移不超过段端点内侧 12px
            offsets.extend([-off, off])
            off += 22
        for o in offsets:
            if y1 == y2:
                cands.append((L, abs(o), (cx + o, cy)))
            else:
                cands.append((L, abs(o), (cx, cy + o)))
    cands.sort(key=lambda c: (-c[0], c[1]))

    def _box(mx, my):
        return {"x": mx - bg_w / 2, "y": my - bg_h / 2, "w": bg_w, "h": bg_h}

    for _, _, (mx, my) in cands:
        if not (bg_w / 2 + 5 <= mx <= W - bg_w / 2 - 5
                and bg_h / 2 + 5 <= my <= H - bg_h / 2 - 5):
            continue
        box = _box(mx, my)
        if not any(rects_overlap(box, n) for n in nodes) and \
                not any(rects_overlap(box, u) for u in used_boxes):
            return mx, my, box
    # 兜底：盖节点总面积最小
    def _cover(mx, my):
        box = _box(mx, my)
        area = 0
        for n in nodes:
            ox = min(box["x"] + box["w"], n["x"] + n["w"]) - max(box["x"], n["x"])
            oy = min(box["y"] + box["h"], n["y"] + n["h"]) - max(box["y"], n["y"])
            if ox > 0 and oy > 0:
                area += ox * oy
        return area
    mx, my = min(cands, key=lambda c: _cover(c[2][0], c[2][1]))[2]
    return mx, my, _box(mx, my)


# ============== SVG 渲染（论文白） ==============

def render_svg(data):
    canvas = data["canvas"]
    nodes = data["nodes"]
    edges = data.get("edges", [])
    W, H = canvas["width"], canvas["height"]
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    node_map = {n["id"]: n for n in nodes}

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="{FONT}">')

    # 背景（纯白 + 极淡网格，对标暗色版网格但用浅灰）
    # defs：网格 + 箭头 marker
    out.append('  <defs>')
    out.append(f'    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">')
    out.append(f'      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{LIGHT["grid"]}" stroke-width="0.5"/>')
    out.append('    </pattern>')
    out.append(f'    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
               f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">')
    out.append(f'      <path d="M 0 0 L 10 5 L 0 10 z" fill="{LIGHT["arrow"]}"/>')
    out.append('    </marker>')
    out.append('  </defs>')

    # 背景（纯白 + 极淡网格，对标暗色版网格但用浅灰）
    out.append(f'  <rect width="{W}" height="{H}" fill="{LIGHT["bg"]}"/>')
    out.append('  <rect width="100%" height="100%" fill="url(#grid)"/>')

    # 样式
    out.append('  <style>')
    out.append(f'    .title {{ font: 700 18px {FONT}; fill: {LIGHT["text"]}; }}')
    out.append(f'    .sub {{ font: 400 12px {FONT}; fill: {LIGHT["text_sec"]}; }}')
    out.append(f'    .label {{ font: 600 9px {FONT}; fill: {LIGHT["text_sec"]}; '
               f'letter-spacing: 0.05em; text-transform: uppercase; }}')
    out.append(f'    .en {{ font: 600 13px {FONT}; fill: {LIGHT["text"]}; }}')
    out.append(f'    .zh {{ font: 400 11px {FONT}; fill: {LIGHT["text_sec"]}; }}')
    out.append(f'    .item {{ font: 400 10px {FONT}; fill: {LIGHT["text_sec"]}; }}')
    out.append(f'    .elabel {{ font: 500 10px {FONT}; fill: {LIGHT["text_sec"]}; }}')
    out.append('  </style>')

    # 标题
    if title:
        out.append(f'  <text x="{W/2}" y="34" class="title" text-anchor="middle">{esc(title)}</text>')
    if subtitle:
        out.append(f'  <text x="{W/2}" y="54" class="sub" text-anchor="middle">{esc(subtitle)}</text>')

    # 边（在节点之下）
    # 端口扇出：多条边共享同一节点的同一侧时，端点对称错开（避免箭头堆叠）
    port_offsets = compute_port_offsets(edges, nodes, node_map)
    label_boxes = []  # 已放置的标签框（防止标签互相重叠）
    for ei, e in enumerate(edges):
        fn = node_map.get(e["from"])
        tn = node_map.get(e["to"])
        if not fn or not tn:
            continue
        from_off, to_off = port_offsets.get(ei, ((0, 0), (0, 0)))
        pts = route_edge(fn, tn, nodes, from_off=from_off, to_off=to_off)
        style = e.get("style", "solid")
        dash = "" if style == "solid" else 'stroke-dasharray="5,4"'
        sw = 1.5
        pts_str = " ".join(f"{x},{y}" for x, y in pts)
        out.append(f'  <polyline points="{pts_str}" fill="none" stroke="{LIGHT["arrow"]}" '
                   f'stroke-width="{sw}" {dash} marker-end="url(#arrow)"/>')
        # 边标签：标注落线且不盖任何节点/其他标签（引擎自动避让）
        label = e.get("label", "")
        if label:
            mx, my, box = place_edge_label(pts, nodes, label, label_boxes, W, H)
            out.append(f'  <rect x="{box["x"]}" y="{box["y"]}" width="{box["w"]}" height="{box["h"]}" rx="3" '
                       f'fill="{LIGHT["bg"]}" stroke="{LIGHT["border"]}" stroke-width="0.6"/>')
            out.append(f'  <text x="{mx}" y="{my+3}" class="elabel" text-anchor="middle">{esc(label)}</text>')
            label_boxes.append(box)

    # 节点
    for n in nodes:
        ntype = n.get("type", "backend")
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        stroke = LIGHT.get(ntype, LIGHT["backend"])
        fill = LIGHT_FILL.get(ntype, LIGHT_FILL["backend"])

        # 整圈语义色描边 + 淡色填充 + 大圆角（对标暗色版风格）
        out.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')

        # 类型徽章（左上角，固定小字号）
        out.append(f'  <text x="{x+12}" y="{y+16}" class="label">{esc(ntype)}</text>')

        # 英文名 + 中文名：fitted_font_size 按盒宽自适应缩字号（根治"卡片大文字空"和"文字溢出"）
        en = n.get("en", n.get("name", ""))
        zh = n.get("zh", "")
        # 英文：preferred=13, minimum=8
        en_fs = fitted_font_size(en, w, 13, 8) if (fitted_font_size and en) else 13
        if en:
            out.append(f'  <text x="{x+w/2}" y="{y+h/2-1}" class="en" '
                       f'style="font-size:{en_fs:.1f}px" text-anchor="middle">{esc(en)}</text>')
        # 中文：preferred=11, minimum=7
        zh_fs = fitted_font_size(zh, w, 11, 7) if (fitted_font_size and zh) else 11
        if zh:
            y_zh = y + h/2 + 15 if en else y + h/2 + 4
            out.append(f'  <text x="{x+w/2}" y="{y_zh}" class="zh" '
                       f'style="font-size:{zh_fs:.1f}px" text-anchor="middle">{esc(zh)}</text>')

        # 子项列表：每项也按盒宽自适应缩字号
        items = n.get("items", [])
        item_fs_base = 10
        for j, it in enumerate(items):
            iy = y + h - 6 - (len(items) - j - 1) * 13
            it_fs = fitted_font_size(it, w - 8, item_fs_base, 7) if fitted_font_size else item_fs_base
            out.append(f'  <text x="{x+w/2}" y="{iy}" class="item" '
                       f'style="font-size:{it_fs:.1f}px" text-anchor="middle">• {esc(it)}</text>')

    # 图例（底部）
    used_types = sorted(set(n.get("type", "backend") for n in nodes))
    if used_types:
        leg_y = H - 16
        lx = 40
        for t in used_types:
            c = LIGHT.get(t, LIGHT["backend"])
            f = LIGHT_FILL.get(t, LIGHT_FILL["backend"])
            out.append(f'  <rect x="{lx}" y="{leg_y-10}" width="14" height="14" rx="3" '
                       f'fill="{f}" stroke="{c}" stroke-width="1.2"/>')
            out.append(f'  <text x="{lx+20}" y="{leg_y-1}" class="elabel">{esc(t)}</text>')
            lx += 110

    out.append('</svg>')
    return "\n".join(out)


# ============== HTML 包装（自适应宽度，完整截图） ==============

def wrap_html(svg, title, subtitle):
    # SVG 自适应：max-width: 100%，不溢出
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:40]
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} · Diagram</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: {FONT};
      background: #F9FAFB;
      padding: 2rem;
      color: {LIGHT["text"]};
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    .diagram-wrap {{
      background: white;
      border: 1px solid {LIGHT["border"]};
      border-radius: 8px;
      padding: 1.5rem;
      overflow: hidden;
    }}
    .diagram-wrap svg {{
      display: block;
      width: 100%;
      height: auto;
      max-width: 1400px;
      margin: 0 auto;
    }}
    .footer {{
      margin-top: 1rem;
      color: {LIGHT["text_sec"]};
      font-size: 0.75rem;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="diagram-wrap">
{svg}
    </div>
    <p class="footer">{esc(title)} · super-diagram v2.1</p>
  </div>
</body>
</html>"""


# ============== 时序图（Sequence，type="sequence"） ==============

# 参与者类型 → token 色（亮/暗主题）
SEQ_TOKEN_LIGHT = {
    "user":     ("#fefce8", "#f59e0b"),
    "backend":  ("#eff6ff", "#3b82f6"),
    "db":       ("#f0fdf4", "#22c55e"),
    "gateway":  ("#f5f3ff", "#8b5cf6"),
    "external": ("#fef2f2", "#ef4444"),
    "default":  ("#f8fafc", "#64748b"),
}
SEQ_TOKEN_DARK = {
    "user":     ("rgba(120,53,15,0.35)", "#fbbf24"),
    "backend":  ("rgba(30,58,138,0.4)", "#60a5fa"),
    "db":       ("rgba(6,78,59,0.35)", "#34d399"),
    "gateway":  ("rgba(76,29,149,0.4)", "#a78bfa"),
    "external": ("rgba(136,19,55,0.4)", "#fb7185"),
    "default":  ("rgba(30,41,59,0.5)", "#94a3b8"),
}


def _seq_colors(theme):
    """时序图配色表（light/dark）"""
    if theme == "dark":
        return {
            "bg": "#020617", "border": "#1e293b", "text": "#f1f5f9",
            "text_sec": "#94a3b8", "main": "#22d3ee", "async": "#64748b",
            "box_fill": "#0f172a", "label_bg": "rgba(2,6,23,0.88)", "line": "#334155",
        }
    return {
        "bg": "#ffffff", "border": "#e5e7eb", "text": "#1e293b",
        "text_sec": "#64748b", "main": "#2563eb", "async": "#94a3b8",
        "box_fill": "#f8fafc", "label_bg": "rgba(255,255,255,0.95)", "line": "#d1d5db",
    }


def _text_w(s, size, cjk=1.0, ascii_w=0.6):
    """估算文本宽度（CJK≈size，ASCII≈0.6×size）"""
    w = 0.0
    for ch in str(s):
        o = ord(ch)
        if o > 0x2E80:
            w += size * cjk
        elif o == 0x20:
            w += size * 0.35
        else:
            w += size * ascii_w
    return w


def render_sequence_svg(data):
    """时序图渲染 — 防字体遮盖设计：
    1. 标签宽度按内容自适应（不固定宽度，长文本不溢出白底框）
    2. 行高自适应：双行(28px) vs 单行(18px)，行距取最大所需 + 固定间隙
    3. 时间标签错位到消息线下方空隙，不与相邻消息标签重叠
    4. 标签背景不盖生命线：只盖自身文本区域
    """
    canvas = data["canvas"]
    theme = canvas.get("theme", "light")
    C = _seq_colors(theme)
    tokens = SEQ_TOKEN_DARK if theme == "dark" else SEQ_TOKEN_LIGHT

    participants = data.get("participants", [])
    messages = data.get("messages", [])
    W = canvas["width"]
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    n = len(participants)
    if n == 0:
        return ""

    # ---- 布局常量 ----
    title_h = 30
    sub_h = 16 if subtitle else 0
    header_h = title_h + sub_h + 24            # 标题区高度（加 8px 上下边距，防止标题贴顶）
    ph, pw = 44, 132                            # 参与者框高宽
    gap = 168                                   # 相邻生命线间距
    margin_x = 50
    total_w = margin_x + n * gap + margin_x
    x0 = (W - min(total_w, W - margin_x * 2)) / 2
    xs = [x0 + margin_x + i * gap for i in range(n)]   # 各生命线 x
    pid = {p.get("id", p.get("en", p.get("label", ""))): i for i, p in enumerate(participants)}

    # ---- 消息行高：逐条计算，双行消息行距更大，杜绝相邻标签重叠 ----
    rows = []                                   # (from_x, to_x, my, en, zh, time, async, row_h)
    msg_top = header_h + ph + 30                # 首行消息完全落在参与者框下方（框底=header_h+ph，再留 30px）
    y = msg_top
    for m in messages:
        f_i = pid.get(m.get("from"), 0)
        t_i = pid.get(m.get("to"), 1 if n > 1 else 0)
        fx, tx = xs[f_i], xs[t_i]
        en = m.get("en", "")
        zh = m.get("zh", "")
        is_async = m.get("async", False)
        time = m.get("time", "")
        has_two = bool(zh)
        # 文本宽度（自适应标签框）
        w_en = _text_w(en, 12)
        w_zh = _text_w(zh, 11) if zh else 0
        w_txt = max(w_en, w_zh)
        # 可用宽度 = 消息跨度 - 两端箭头余量
        avail = max(60, abs(tx - fx) - 56)
        box_w = max(70, min(avail, int(w_txt + 28)))
        row_h = 52 if has_two else 40           # 双行行高大，保证标签间不重叠
        rows.append({"fx": fx, "tx": tx, "my": y, "en": en, "zh": zh,
                     "time": time, "async": is_async, "box_w": box_w, "has_two": has_two})
        y += row_h
    msg_bot = y + 16
    H = max(canvas["height"], msg_bot + 30)

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="{FONT}">')

    # defs：markers
    out.append('  <defs>')
    for mid, mcolor in [("am", C["main"]), ("aa", C["async"])]:
        out.append(f'    <marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
                   f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">')
        out.append(f'      <path d="M 0 0 L 10 5 L 0 10 z" fill="{mcolor}"/>')
        out.append('    </marker>')
    out.append('  </defs>')

    # 背景
    out.append(f'  <rect width="{W}" height="{H}" fill="{C["bg"]}"/>')

    # 样式
    out.append('  <style>')
    out.append(f'    .title {{ font: 700 20px {FONT}; fill: {C["text"]}; }}')
    out.append(f'    .sub {{ font: 400 12px {FONT}; fill: {C["text_sec"]}; }}')
    out.append(f'    .pen {{ font: 600 13px {FONT}; fill: {C["text"]}; }}')
    out.append(f'    .pen-zh {{ font: 400 10px {FONT}; fill: {C["text_sec"]}; }}')
    out.append(f'    .msg-en {{ font: 600 11.5px {FONT}; fill: {C["text"]}; }}')
    out.append(f'    .msg-zh {{ font: 400 10.5px {FONT}; fill: {C["text_sec"]}; }}')
    out.append(f'    .time {{ font: 400 9.5px {FONT}; fill: {C["text_sec"]}; }}')
    out.append('  </style>')

    # 标题
    if title:
        out.append(f'  <text x="{margin_x}" y="{title_h}" class="title">{esc(title)}</text>')
    if subtitle:
        out.append(f'  <text x="{margin_x}" y="{title_h + sub_h}" class="sub">{esc(subtitle)}</text>')

    # 生命线（在消息之下）
    ly_bot = msg_bot
    for i, p in enumerate(participants):
        cx = xs[i]
        out.append(f'  <line x1="{cx}" y1="{header_h + ph + 6}" x2="{cx}" y2="{ly_bot}" '
                   f'stroke="{C["line"]}" stroke-width="1" stroke-dasharray="5,5"/>')

    # 消息线 + 标签（标签宽度自适应，行高独立 → 不遮盖）
    for r in rows:
        my = r["my"]
        fx, tx = r["fx"], r["tx"]
        color = C["async"] if r["async"] else C["main"]
        marker = "aa" if r["async"] else "am"
        dash = ' stroke-dasharray="5,4"' if r["async"] else ""
        dir_right = tx >= fx
        s0 = fx + (10 if dir_right else -10)
        t0 = tx - (12 if dir_right else -12)
        out.append(f'  <line x1="{s0}" y1="{my}" x2="{t0}" y2="{my}" stroke="{color}" '
                   f'stroke-width="2.2" marker-end="url(#{marker})"{dash}/>')

        # 标签：白底框 + 双行/单行文本，宽度按内容自适应
        mx = (fx + tx) / 2
        bw = r["box_w"]
        if r["has_two"]:
            bh = 30
            out.append(f'  <rect x="{mx - bw/2}" y="{my - bh/2}" width="{bw}" height="{bh}" '
                       f'rx="5" fill="{C["label_bg"]}" stroke="{C["line"]}" stroke-width="0.6"/>')
            out.append(f'  <text x="{mx}" y="{my - 1}" class="msg-en" text-anchor="middle">{esc(r["en"])}</text>')
            out.append(f'  <text x="{mx}" y="{my + 12}" class="msg-zh" text-anchor="middle">{esc(r["zh"])}</text>')
        else:
            bh = 20
            out.append(f'  <rect x="{mx - bw/2}" y="{my - bh/2}" width="{bw}" height="{bh}" '
                       f'rx="5" fill="{C["label_bg"]}" stroke="{C["line"]}" stroke-width="0.6"/>')
            out.append(f'  <text x="{mx}" y="{my + 4}" class="msg-en" text-anchor="middle">{esc(r["en"])}</text>')

        # 时间标签：放在标签下方空隙（行高已保证不重叠）
        if r["time"]:
            ty = my + (bh / 2) + 13
            out.append(f'  <text x="{mx}" y="{ty}" class="time" text-anchor="middle">{esc(str(r["time"]))}</text>')

    # 参与者框（最后画，盖住生命线顶端）
    for i, p in enumerate(participants):
        cx = xs[i]
        px = cx - pw / 2
        py = header_h
        kind = p.get("kind", p.get("type", "default"))
        fill, stroke = tokens.get(kind, tokens["default"])
        out.append(f'  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        en = p.get("en", p.get("label", ""))
        zh = p.get("zh", "")
        if zh:
            out.append(f'  <text x="{cx}" y="{py + 17}" class="pen" text-anchor="middle">{esc(en)}</text>')
            out.append(f'  <text x="{cx}" y="{py + 31}" class="pen-zh" text-anchor="middle">{esc(zh)}</text>')
        else:
            out.append(f'  <text x="{cx}" y="{py + ph/2 + 4}" class="pen" text-anchor="middle">{esc(en)}</text>')

    # 底部图例
    leg_y = H - 18
    used = sorted(set(p.get("kind", p.get("type", "default")) for p in participants))
    lx = margin_x
    for k in used:
        fill, stroke = tokens.get(k, tokens["default"])
        out.append(f'  <rect x="{lx}" y="{leg_y - 9}" width="13" height="13" rx="3" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="1.1"/>')
        out.append(f'  <text x="{lx + 19}" y="{leg_y}" class="pen-zh">{esc(k)}</text>')
        lx += 90

    out.append('</svg>')
    return "\n".join(out)


# ============== PNG 导出（playwright） ==============

def export_png(svg_content, png_path, scale=2):
    """用 playwright 把 SVG 截图为 PNG。
    把 SVG 嵌入临时 HTML，用 CDP 截图 SVG 元素本身。
    scale: 缩放倍数（2 = 2x 高清）
    """
    from playwright.sync_api import sync_playwright
    import tempfile

    # 创建临时 HTML（只含 SVG，白色背景）
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:white;">
{svg_content}
</body></html>"""

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        f.write(html)
        tmp_html = f.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(device_scale_factor=scale)
            page = ctx.new_page()
            page.goto(f"file:///{tmp_html.replace(os.sep, '/')}")
            page.wait_for_load_state("networkidle")
            # 截图 SVG 元素本身（不截整个页面）
            svg_el = page.query_selector("svg")
            if svg_el:
                svg_el.screenshot(path=png_path, omit_background=False)
            else:
                page.screenshot(path=png_path, full_page=True)
            browser.close()
    finally:
        os.unlink(tmp_html)


# ============== CLI ==============

def main():
    ap = argparse.ArgumentParser(description="super-diagram v2.1 渲染引擎")
    ap.add_argument("input", help="JSON 文件路径")
    ap.add_argument("-o", "--out", required=True, help="输出路径（.png/.svg/.html）")
    ap.add_argument("--scale", type=float, default=2, help="PNG 缩放倍数（默认 2x）")
    ap.add_argument("--no-validate", action="store_true", help="跳过质量校验")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["canvas"].setdefault("theme", "light")

    if not args.no_validate:
        errors = validate(data)
        if errors:
            print("❌ 质量校验失败：", file=sys.stderr)
            # 支持 Problem 对象和字符串两种格式
            for e in errors:
                if hasattr(e, "code"):
                    print(e, file=sys.stderr)  # Problem.__str__
                else:
                    print(f"   - {e}", file=sys.stderr)
            sys.exit(1)
        print("✅ 质量校验通过", file=sys.stderr)

    # 路由：时序图（type=sequence）走 render_sequence_svg，其余走节点-边渲染
    if data.get("type") == "sequence":
        svg = render_sequence_svg(data)
    else:
        svg = render_svg(data)
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    out_path = Path(args.out)
    ext = out_path.suffix.lower()

    if ext == ".svg":
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"✅ SVG: {out_path}")

    elif ext == ".png":
        export_png(svg, str(out_path), scale=args.scale)
        print(f"✅ PNG ({args.scale}x): {out_path}")

    elif ext == ".html":
        html = wrap_html(svg, title, subtitle)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ HTML: {out_path}")

    else:
        print(f"❌ 不支持的格式: {ext}（支持 .png/.svg/.html）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
