#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mermaid_render.py — Mermaid 代码块渲染工具

将 MD 中的 ```mermaid 代码块提取并渲染为 PNG / PDF 图片。
三条链路（Word / paper / math-notes）共享此工具。

用法（CLI）:
    python mermaid_render.py input.md --output-dir figures/
    python mermaid_render.py input.md --format png,pdf

用法（API）:
    from mermaid_render import extract_and_render
    replacements = extract_and_render('input.md', output_dir='figures/')
    # replacements = {'mermaid-block-0': 'figures/mermaid-0.png', ...}
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# Mermaid 代码块正则
MERMAID_RE = re.compile(
    r'```mermaid\s*\n(.*?)\n```',
    re.DOTALL
)


def find_mermaid_blocks(md_text):
    """提取 MD 中所有 mermaid 代码块，返回 [(match_obj, code), ...]"""
    blocks = []
    for m in MERMAID_RE.finditer(md_text):
        code = m.group(1).strip()
        blocks.append((m, code))
    return blocks


def code_hash(code):
    """对 mermaid 代码做 hash，用于缓存文件名"""
    return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]


def _ensure_puppeteer_path():
    """自动设置 PUPPETEER_EXECUTABLE_PATH（用系统 Edge/Chrome 替代下载 Chromium）"""
    if os.environ.get('PUPPETEER_EXECUTABLE_PATH'):
        return  # 已设置
    candidates = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    ]
    for path in candidates:
        if os.path.exists(path):
            os.environ['PUPPETEER_EXECUTABLE_PATH'] = path
            return


def render_one(code, output_path, fmt='png'):
    """
    用 mmdc 渲染单个 mermaid 代码块为图片。

    Args:
        code: mermaid 代码字符串
        output_path: 输出图片路径（.png 或 .pdf）
        fmt: 'png' 或 'pdf'

    Returns:
        True 如果成功，False 如果失败
    """
    _ensure_puppeteer_path()

    mmdc = shutil.which('mmdc');
    if not mmdc:
        print('[ERROR] mmdc 未安装。请运行: npm install -g @mermaid-js/mermaid-cli',
              file=sys.stderr)
        return False

    # 写临时 .mmd 文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False,
                                     encoding='utf-8') as f:
        f.write(code)
        temp_mmd = f.name

    try:
        cmd = [
            mmdc,
            '-i', temp_mmd,
            '-o', str(output_path),
            '-t', 'default',      # 主题
            '-b', 'transparent',   # 透明背景
            '-w', '1200',          # 宽度
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                encoding='utf-8', errors='replace')
        if result.returncode != 0:
            print(f'[WARN] mmdc 渲染失败: {result.stderr.strip()[:200]}',
                  file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print('[WARN] mmdc 渲染超时（30s）', file=sys.stderr)
        return False
    except Exception as e:
        print(f'[WARN] mmdc 异常: {e}', file=sys.stderr)
        return False
    finally:
        os.unlink(temp_mmd)


def extract_and_render(md_file, output_dir='figures', formats=None):
    """
    提取 MD 中所有 mermaid 代码块，渲染为图片，返回替换映射。

    Args:
        md_file: MD 文件路径
        output_dir: 图片输出目录
        formats: 要渲染的格式列表，默认 ['png']

    Returns:
        dict: {原mermaid代码块的match对象: {fmt: 图片路径}}
              以及 {mermaid全文文本: 替换后的MD图片引用}
    """
    if formats is None:
        formats = ['png']

    md_file = Path(md_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_text = md_file.read_text(encoding='utf-8')
    blocks = find_mermaid_blocks(md_text)

    if not blocks:
        return {}

    print(f'[Mermaid] 发现 {len(blocks)} 个代码块')

    results = {}
    for idx, (match, code) in enumerate(blocks):
        h = code_hash(code)
        block_result = {}

        for fmt in formats:
            ext = fmt
            img_path = output_dir / f'mermaid-{idx:02d}-{h}.{ext}'

            # 缓存：如果图片已存在则跳过
            if img_path.exists() and img_path.stat().st_size > 100:
                print(f'  [缓存] {img_path.name}')
                block_result[fmt] = img_path
                continue

            if render_one(code, img_path, fmt):
                size_kb = img_path.stat().st_size // 1024 if img_path.exists() else 0
                print(f'  [渲染] {img_path.name} ({size_kb}KB)')
                block_result[fmt] = img_path
            else:
                print(f'  [失败] mermaid-{idx:02d}')

        results[idx] = {
            'match': match,
            'code': code,
            'images': block_result,
        }

    return results


def replace_mermaid_in_md(md_text, replacements, img_format='png', rel_prefix=''):
    r"""
    将 MD 中的 mermaid 代码块替换为图片引用。

    Args:
        md_text: 原始 MD 文本
        replacements: extract_and_render 的返回值
        img_format: 使用哪种格式的图片（'png' 或 'pdf'）
        rel_prefix: 图片路径前缀（用于 LaTeX \includegraphics 或 MD ![]()）

    Returns:
        替换后的 MD 文本
    """
    if not replacements:
        return md_text

    new_text = md_text
    for idx, info in replacements.items():
        match = info['match']
        images = info['images']

        if img_format in images:
            img_path = images[img_format]
            rel_path = str(img_path)
            if rel_prefix:
                rel_path = rel_prefix + '/' + img_path.name

            # 替换为标准 MD 图片语法
            replacement = f'![流程图{idx+1}]({rel_path})'
            new_text = new_text.replace(match.group(0), replacement)
        elif not images:
            # 渲染失败，保留为代码块
            pass
        else:
            # 请求的格式不可用，用已有格式
            any_img = list(images.values())[0]
            rel_path = str(any_img)
            if rel_prefix:
                rel_path = rel_prefix + '/' + any_img.name
            replacement = f'![流程图{idx+1}]({rel_path})'
            new_text = new_text.replace(match.group(0), replacement)

    return new_text


def preprocess_md(md_file, output_dir='figures', formats=None, img_format='png'):
    """
    一站式：提取+渲染+替换，返回处理后的 MD 文本。

    Args:
        md_file: 输入 MD 文件
        output_dir: 图片输出目录
        formats: 要渲染的格式列表
        img_format: 替换后 MD 中引用的图片格式

    Returns:
        (new_md_text, replacements)
    """
    if formats is None:
        formats = [img_format]

    md_text = Path(md_file).read_text(encoding='utf-8')
    replacements = extract_and_render(md_file, output_dir, formats)
    new_md_text = replace_mermaid_in_md(md_text, replacements, img_format)

    return new_md_text, replacements


# ============================================================
# CLI 入口
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Mermaid 代码块渲染工具')
    parser.add_argument('input', help='输入 MD 文件')
    parser.add_argument('-o', '--output-dir', default='figures', help='图片输出目录')
    parser.add_argument('-f', '--formats', default='png,pdf',
                        help='渲染格式，逗号分隔（默认 png,pdf）')
    parser.add_argument('--replace', action='store_true',
                        help='输出替换后的 MD 到 stdout')
    args = parser.parse_args()

    formats = args.formats.split(',')

    if args.replace:
        md_text, _ = preprocess_md(args.input, args.output_dir, formats, formats[0])
        print(md_text)
    else:
        extract_and_render(args.input, args.output_dir, formats)


if __name__ == '__main__':
    main()
