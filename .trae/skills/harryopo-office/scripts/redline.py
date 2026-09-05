#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
redline.py — Word 修订审阅（红线稿）生成
=========================================

用途：两份 .docx（原始版 vs 修改版）→ 一份带原生 Word 修订标记（w:ins/w:del）
的红线稿，供用户在 Word 里逐条接受/拒绝。不依赖本机 MS Word（内嵌 .NET
Docxodus 引擎），是"AI 生成初稿 → 用户修改 → AI 理解差异"改稿循环的入口。

用法：
  python redline.py original.docx modified.docx -o redlined.docx [--author "AI Review"]

引擎：python-redlines 0.3.0（MIT）+ Docxodus（内嵌 .NET 二进制，Windows/macOS/Linux
预编译 wheel）。默认算法 wmlcomparer；--engine docxdiff 尝试 0.3.0 新增的结构感知
对比（不可用时自动回退并提示）。
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


def _make_engine(engine: str):
    """构造 Docxodus 引擎；docxdiff 为可选算法，构造参数名按版本探测。"""
    from python_redlines import DocxodusEngine

    if engine != 'docxdiff':
        return DocxodusEngine()
    for kwargs in ({'algorithm': 'docxdiff'}, {'engine': 'docxdiff'}):
        try:
            return DocxodusEngine(**kwargs)
        except TypeError:
            continue
    print('[WARN] 当前 python-redlines 版本不支持 docxdiff，回退默认 wmlcomparer',
          file=sys.stderr)
    return DocxodusEngine()


def make_redline(original: Path, modified: Path, output: Path,
                 author: str = 'AI Review', engine: str = 'wmlcomparer') -> Path:
    """生成红线稿，返回输出路径。失败抛异常。"""
    from python_redlines import DocxodusEngine

    eng = DocxodusEngine() if engine == 'wmlcomparer' else _make_engine(engine)
    original_bytes = original.read_bytes()
    modified_bytes = modified.read_bytes()
    result = eng.run_redline(author, original_bytes, modified_bytes)
    # 0.3.0 返回 (bytes, stdout, stderr)；兼容直接返回 bytes 的旧版
    redline_bytes = result[0] if isinstance(result, tuple) else result
    if not redline_bytes:
        raise RuntimeError('红线稿生成失败：引擎返回空内容')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(redline_bytes)
    return output


def verify_redline(path: Path) -> dict:
    """校验红线稿含原生修订标记，返回统计（供 AI/用户确认生成质量）。"""
    counts = {'ins': 0, 'del': 0, 'comments': 0}
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    counts['ins'] = xml.count('<w:ins ')
    counts['del'] = xml.count('<w:del ')
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(
        description='两份 docx → 原生 Word 修订红线稿（不依赖本机 Word）',
        epilog='示例: python redline.py 初稿.docx 用户改.docx -o 红线稿.docx')
    ap.add_argument('original', help='原始版 docx（AI 生成初稿）')
    ap.add_argument('modified', help='修改版 docx（用户改动后）')
    ap.add_argument('-o', '--output', required=True, help='输出红线稿路径')
    ap.add_argument('--author', default='AI Review', help='修订记录显示的作者名')
    ap.add_argument('--engine', default='wmlcomparer', choices=['wmlcomparer', 'docxdiff'],
                    help='对比算法（docxdiff 为结构感知引擎，0.3.0 可选）')
    args = ap.parse_args()

    original, modified, output = (Path(args.original), Path(args.modified),
                                  Path(args.output))
    for p in (original, modified):
        if not p.exists():
            print(f'[FATAL] 文件不存在: {p}', file=sys.stderr)
            return 1
    if original.resolve() == modified.resolve():
        print('[FATAL] 两份文件路径相同，无差异可对比', file=sys.stderr)
        return 1

    try:
        out = make_redline(original, modified, output, args.author, args.engine)
    except Exception as exc:
        print(f'[FATAL] 红线稿生成失败: {exc}', file=sys.stderr)
        return 1

    counts = verify_redline(out)
    if counts['ins'] == 0 and counts['del'] == 0:
        print('[WARN] 输出不含 w:ins/w:del 修订标记——两份文件可能无实质差异')
    size_kb = out.stat().st_size // 1024
    print(f'[OK] 红线稿: {out} ({size_kb}KB) '
          f'插入 {counts["ins"]} 处 / 删除 {counts["del"]} 处（作者: {args.author}）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
