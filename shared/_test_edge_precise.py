#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精确测试边穿节点检测"""
import sys
sys.path.insert(0, "d:/ai/latex/shared")
from diagram_geometry import *

# 模拟实际场景：A(30,80,80,50) B(170,80,80,50) C(310,80,80,50)
# route_edge 输出的路径：(70,80) → (310,80) → (310,105)
B = Rect(170, 80, 80, 50)
points = [(70.0, 80), (310, 80), (310, 105.0)]

print("B rect:", B.to_dict())
print("Path points:", points)
print("segment (70,80)->(310,80) intersects B (clearance=2):",
      segment_intersects_rect((70, 80), (310, 80), B, clearance=2))
print("segment (70,80)->(310,80) intersects B (clearance=0):",
      segment_intersects_rect((70, 80), (310, 80), B, clearance=0))

# y=80 正好是 B 的顶边，线段在 B 上边界
# Liang-Barsky: 线段 y=80 恒定，B 的 y 范围 [80-2, 130+2] = [78, 132]
# dy=0, p=-dy=0, q=y1-ry1=80-78=2 > 0 → 平行不相交？不对
# 当 dy=0 时，检查 -dy 和 dy 两条裁剪边：
#   p=-0=0, q=80-(80-2)=2 → p=0, q=2>0 → OK（不淘汰）
#   p=0, q=(130+2)-80=52 → p=0, q=52>0 → OK
# 所以 y 维度不淘汰。但 x 维度：
#   p=-dx=-(310-70)=-240, q=70-(170-2)=70-168=-98 → p<0, t=q/p=-98/-240=0.408
#   t_enter=0.408
#   p=dx=240, q=(250+2)-70=182 → p>0, t=182/240=0.758
#   t_exit=0.758
# t_enter(0.408) <= t_exit(0.758) → 相交！

print("\n--- 手动 Liang-Barsky ---")
x1, y1, x2, y2 = 70, 80, 310, 80
rx1, ry1, rx2, ry2 = 170-2, 80-2, 250+2, 130+2
dx, dy = x2-x1, y2-y1
print(f"dx={dx}, dy={dy}")
print(f"rect expanded: [{rx1},{ry1}] to [{rx2},{ry2}]")

for p, q, label in [(-dx, x1-rx1, "left"), (dx, rx2-x1, "right"), (-dy, y1-ry1, "bottom"), (dy, ry2-y1, "top")]:
    if abs(p) < 1e-12:
        print(f"  {label}: p≈0, q={q} → {'OK' if q >= 0 else 'REJECT'}")
    else:
        t = q / p
        print(f"  {label}: p={p}, q={q}, t={t:.3f}")
