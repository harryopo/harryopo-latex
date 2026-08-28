#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接测试 super-diagram validate 函数"""
import sys, json
sys.path.insert(0, "c:/Users/Lenovo/.trae-cn/skills/super-diagram/scripts")
sys.path.insert(0, "d:/ai/latex/shared")

# 手动加载模块（绕过 __file__ 路径推断）
import importlib.util
spec = importlib.util.spec_from_file_location("render_v2", "c:/Users/Lenovo/.trae-cn/skills/super-diagram/scripts/render_v2.py")
render_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render_v2)

data = {
    "canvas": {"width": 400, "height": 200, "theme": "light"},
    "title": "边穿节点测试",
    "nodes": [
        {"id": "A", "x": 30, "y": 80, "w": 80, "h": 50, "type": "backend", "label": "Alpha"},
        {"id": "B", "x": 170, "y": 80, "w": 80, "h": 50, "type": "db", "label": "Blocker"},
        {"id": "C", "x": 310, "y": 80, "w": 80, "h": 50, "type": "backend", "label": "Gamma"}
    ],
    "edges": [
        {"from": "A", "to": "C", "label": "穿过B"}
    ]
}

problems = render_v2.validate(data)
print(f"共 {len(problems)} 个问题:")
for p in problems:
    if hasattr(p, "code"):
        print(f"  [{p.code}] {p.message}")
    else:
        print(f"  {p}")
