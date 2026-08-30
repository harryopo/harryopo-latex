#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagram_render.py — 图表统一渲染器（super-diagram + mermaid）

将 MD 中的图表数据代码块渲染为 PNG，自动替换为图片引用：
  ```super-diagram + JSON   → super-diagram 引擎（架构图/时序图，AI 算坐标）
  ```mermaid + 代码          → mmdc 引擎（Mermaid 流程图，保留既有能力）

被 office.py 的 render 流程调用。渲染出的 PNG 落到 `output_dir/figures/`，
Word / paper / notes 三条链路通过标准 `![alt](path)` 语法自动带图。

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

# super-diagram 渲染脚本（全局 skill，可用环境变量 SUPER_DIAGRAM_SCRIPT 覆盖）
# 注意：不得硬编码用户名（不同机器的用户目录不同，硬编码会导致渲染静默失败）。
# 自动探测顺序：环境变量 → 当前用户 .trae-cn/skills。
SUPER_DIAGRAM_CANDIDATES = (
    os.environ.get('SUPER_DIAGRAM_SCRIPT', ''),
    os.path.join(os.path.expanduser('~'), '.trae-cn', 'skills',
                 'super-diagram', 'scripts', 'render_v2.py'),
)

# 图表代码块正则（语言标签 = 引擎名）
SUPER_RE = re.compile(r'```super-diagram\s*\n(.*?)\n```', re.DOTALL)
MERMAID_RE = re.compile(r'```mermaid\s*\n(.*?)\n```', re.DOTALL)


def code_hash(code: str) -> str:
    """对图表数据做 hash，用于缓存文件名"""
    return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]


# ============================================================
# super-diagram 引擎
# ============================================================

def _find_super_script():
    """定位 super-diagram 渲染脚本，返回 Path 或 None"""
    for cand in SUPER_DIAGRAM_CANDIDATES:
        p = Path(cand) if cand else None
        if p and p.exists():
            return p
    return None


def render_super_diagram(json_text: str, output_path) -> bool:
    """
    用 super-diagram 渲染单个 JSON 数据为 PNG。

    Args:
        json_text: super-diagram 契约 JSON（architecture: nodes+edges / sequence: participants+messages）
        output_path: 输出 PNG 路径

    Returns:
        True 如果成功，False 如果失败
    """
    script = _find_super_script()
    if not script:
        print('[WARN] super-diagram 脚本不存在。请安装 super-diagram skill 或设置 '
              'SUPER_DIAGRAM_SCRIPT 环境变量', file=sys.stderr)
        return False

    # 先校验 JSON 合法性（render_v2.py 也会校验，这里提前给出友好报错）
    try:
        json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f'[WARN] super-diagram JSON 解析失败: {e}', file=sys.stderr)
        return False

    # 写临时 JSON 文件（render_v2.py 从文件读取）
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False,
                                     encoding='utf-8') as f:
        f.write(json_text)
        tmp_json = f.name

    try:
        cmd = [sys.executable, str(script), tmp_json,
               '-o', str(output_path), '--scale', '2']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                                encoding='utf-8', errors='replace')
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            print(f'[WARN] super-diagram 渲染失败: {err[-200:]}', file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print('[WARN] super-diagram 渲染超时（120s）', file=sys.stderr)
        return False
    except Exception as e:
        print(f'[WARN] super-diagram 异常: {e}', file=sys.stderr)
        return False
    finally:
        os.unlink(tmp_json)


def _extract_title(json_text: str) -> str:
    """从 JSON 中提取图注（title 优先，subtitle 兜底），用于图片 alt"""
    try:
        data = json.loads(json_text)
        return (data.get('title') or data.get('subtitle') or '').strip()
    except Exception:
        return ''


# ============================================================
# 统一提取 + 渲染
# ============================================================

def find_diagram_blocks(md_text: str):
    """提取 MD 中所有图表代码块，返回 [{engine, match, code, title}, ...]"""
    blocks = []
    for m in SUPER_RE.finditer(md_text):
        code = m.group(1).strip()
        blocks.append({
            'engine': 'super-diagram',
            'match': m,
            'code': code,
            'title': _extract_title(code),
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
        return render_super_diagram(code, output_path)
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
            alt = info['title'] or f'图{idx + 1}'
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
    parser = argparse.ArgumentParser(description='图表统一渲染器（super-diagram + mermaid）')
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
