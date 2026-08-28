#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diagram_geometry 快速验证"""
import sys
sys.path.insert(0, "d:/ai/latex/shared")
from diagram_geometry import *

# Windows GBK 终端兼容：强制 UTF-8 输出（Problem.__str__ 含 emoji）
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 测试 1: 矩形重叠
a = Rect(0, 0, 100, 50)
b = Rect(80, 0, 100, 50)
c = Rect(200, 0, 100, 50)
print("=== 矩形重叠 ===")
print("a-b (gap=8):", rects_overlap(a, b, 8))   # True
print("a-c (gap=8):", rects_overlap(a, c, 8))   # False

# 测试 2: 线段穿矩形
print("\n=== 线段穿矩形 ===")
print("seg穿过b:", segment_intersects_rect((0, 25), (300, 25), b))  # True
print("seg不穿a:", segment_intersects_rect((200, 25), (350, 25), a))  # False

# 测试 3: 文本测量
print("\n=== 文本测量 ===")
print("CJK '你好':", text_units("你好"))     # 4.0
print("ASCII 'AB':", text_units("AB"))       # 2.0
print("混合 'Hi你好':", text_units("Hi你好"))  # 6.0 (1+1+2+2)

# 测试 4: 缩字号
print("\n=== 缩字号 ===")
fs = fitted_font_size("Hello World", 80, 15, 6)
print("'Hello World' @80px:", fs, "px")  # < 15
fs2 = fitted_font_size("Hi", 80, 15, 6)
print("'Hi' @80px:", fs2, "px")  # = 15

# 测试 5: 端口扇出
print("\n=== 端口扇出 ===")
rels = [
    {"id": "e1", "component_id": "A", "peer_cx": 300, "peer_cy": 10},
    {"id": "e2", "component_id": "A", "peer_cx": 300, "peer_cy": 50},
    {"id": "e3", "component_id": "A", "peer_cx": 300, "peer_cy": 90},
    {"id": "e4", "component_id": "B", "peer_cx": 500, "peer_cy": 30},
]
spread = automatic_port_spread(rels, "right", 100)
print("spread:", spread)  # e1/e2/e3 有偏移, e4 不在结果

# 测试 6: Problem 格式
print("\n=== 重叠检测 ===")
probs = clean_overlap_problems([("a", a), ("b", b)], gap=8)
for p in probs:
    print(p)

# 测试 7: 边穿节点
print("\n=== 边穿节点 ===")
nodes = [
    {"id": "N1", "x": 0, "y": 0, "w": 60, "h": 40},
    {"id": "N2", "x": 200, "y": 0, "w": 60, "h": 40},
    {"id": "BLOCK", "x": 80, "y": 10, "w": 60, "h": 40},
]
edges = [{"from": "N1", "to": "N2"}]  # N1->N2 直线会穿过 BLOCK
flow_probs = clean_flow_problems(edges, nodes)
for p in flow_probs:
    print(p)

# 测试 8: 出界检测
print("\n=== 出界检测 ===")
oob_probs = clean_out_of_bounds([("big", Rect(-5, 0, 300, 50))], 280, 200)
for p in oob_probs:
    print(p)

# 测试 9: 文本超宽
print("\n=== 文本超宽 ===")
tx_probs = clean_text_overflow([
    {"id": "card1", "text": "这是一个非常非常长的中文标签", "width": 50, "minimum_fontsize": 6}
])
for p in tx_probs:
    print(p)

print("\n✅ 全部测试完成")
