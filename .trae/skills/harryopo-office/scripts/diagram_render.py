#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagram_render.py — 图表统一渲染器（mermaid）

将 MD 中的图表数据代码块渲染为 PNG，自动替换为图片引用：
  ```mermaid + 代码          → mmdc 引擎（Mermaid 流程图）
  ```super-diagram + JSON   → 已不支持（引擎 2026-09-02 移除）：报错提示改用 diagram-design

被 office.py 的 render 流程调用。渲染出的 PNG 落到 `output_dir/figures/`，
Word / paper / notes 双链路通过标准 `![alt](path)` 语法自动带图。

用法（CLI）:
    python diagram_render.py input.md --output-dir figures/
    python diagram_render.py input.md --replace > output.md

用法（API）:
    from diagram_render import preprocess_md
    new_text, replacements = preprocess_md('input.md', 'figures/')
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# 图表代码块正则（语言标签 = 引擎名）
SUPER_RE = re.compile(r'```super-diagram\s*\n(.*?)\n```', re.DOTALL)  # 仅用于拦截报错
MERMAID_RE = re.compile(r'```mermaid\s*\n(.*?)\n```', re.DOTALL)


def code_hash(code: str) -> str:
    """对图表数据做 hash，用于缓存文件名"""
    return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]


# ============================================================
# 统一提取 + 渲染
# ============================================================

def find_diagram_blocks(md_text: str):
    """提取 MD 中所有图表代码块，返回 [{engine, match, code, title}, ...]"""
    blocks = []
    for m in SUPER_RE.finditer(md_text):
        blocks.append({
            'engine': 'super-diagram',
            'match': m,
            'code': m.group(1).strip(),
            'title': '',
        })
    for m in MERMAID_RE.finditer(md_text):
        blocks.append({
            'engine': 'mermaid',
            'match': m,
            'code': m.group(1).strip(),
            'title': '',
        })
    return blocks


def render_one(engine: str, code: str, output_path) -> bool:
    """按引擎路由渲染单个图表"""
    if engine == 'super-diagram':
        # 引擎已于 2026-09-02 移除（收敛为 diagram-design + mermaid 双引擎）
        print('[WARN] super-diagram 引擎已移除，请改用 diagram-design（HTML→PNG）'
              '或 mermaid 流程图；架构/时序图参考 skills/diagram-design/', file=sys.stderr)
        return False
    if engine == 'mermaid':
        # 复用 mermaid_render.render_one（mmdc CLI）
        try:
            from mermaid_render import render_one as mm_render_one
            return mm_render_one(code, output_path, fmt='png')
        except ImportError:
            print('[WARN] mermaid_render 模块未找到', file=sys.stderr)
            return False
    return False


def extract_and_render(md_file, output_dir='figures'):
    """
    提取 MD 中所有图表代码块并渲染 PNG，返回替换映射。

    Returns:
        dict: {idx: {'match': match, 'engine': str, 'code': str, 'images': {fmt: path}}}
    """
    md_file = Path(md_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_text = md_file.read_text(encoding='utf-8')
    blocks = find_diagram_blocks(md_text)

    if not blocks:
        return {}

    print(f'[图表] 发现 {len(blocks)} 个图表块（'
          f'{sum(1 for b in blocks if b["engine"] == "super-diagram")} super-diagram / '
          f'{sum(1 for b in blocks if b["engine"] == "mermaid")} mermaid）')

    results = {}
    for idx, blk in enumerate(blocks):
        h = code_hash(blk['code'])
        engine = blk['engine']
        img_path = output_dir / f'{engine}-{idx:02d}-{h}.png'

        if img_path.exists() and img_path.stat().st_size > 100:
            print(f'  [缓存] {img_path.name}')
            images = {'png': img_path}
        elif render_one(engine, blk['code'], img_path):
            size_kb = img_path.stat().st_size // 1024 if img_path.exists() else 0
            print(f'  [渲染] {img_path.name} ({size_kb}KB)')
            images = {'png': img_path}
        else:
            print(f'  [失败] {engine}-{idx:02d}')
            images = {}

        results[idx] = {
            'match': blk['match'],
            'engine': engine,
            'code': blk['code'],
            'title': blk['title'],
            'images': images,
        }

    return results


def replace_in_md(md_text: str, replacements: dict, rel_prefix='figures'):
    """
    将 MD 中的图表代码块替换为图片引用 `![图注](figures/xxx.png)`。

    图注规则：
      - super-diagram：JSON 的 title（AI 写完整图注，如 `图3：总体架构`），缺省用 `图N`
      - mermaid：`流程图N`（与既有行为一致）
    """
    if not replacements:
        return md_text

    new_text = md_text
    for idx, info in replacements.items():
        match = info['match']
        images = info['images']
        if not images:
            continue  # 渲染失败，保留代码块便于排查

        img = images['png']
        rel_path = f'{rel_prefix}/{img.name}'

        if info['engine'] == 'super-diagram':
            alt = f'图{idx + 1}'  # 引擎已移除，仅保留兼容路径（实际渲染会失败）
        else:
            alt = f'流程图{idx + 1}'

        new_text = new_text.replace(match.group(0), f'![{alt}]({rel_path})')

    return new_text


def preprocess_md(md_file, output_dir='figures'):
    """
    一站式：提取 + 渲染 + 替换，返回处理后的 MD 文本。

    Returns:
        (new_md_text, replacements)
    """
    md_text = Path(md_file).read_text(encoding='utf-8')
    replacements = extract_and_render(md_file, output_dir)
    new_text = replace_in_md(md_text, replacements)
    return new_text, replacements


# ============================================================
# CLI 入口
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='图表统一渲染器（mermaid）')
    parser.add_argument('input', help='输入 MD 文件')
    parser.add_argument('-o', '--output-dir', default='figures', help='图片输出目录')
    parser.add_argument('--replace', action='store_true',
                        help='输出替换后的 MD 到 stdout')
    args = parser.parse_args()

    if args.replace:
        new_text, _ = preprocess_md(args.input, args.output_dir)
        print(new_text)
    else:
        extract_and_render(args.input, args.output_dir)


if __name__ == '__main__':
    main()
