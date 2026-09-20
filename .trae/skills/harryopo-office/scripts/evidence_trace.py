#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
evidence_trace.py — 提取证据回溯验证层（方案书 v3 P2 "Citra 证据回溯" 自研实现）

背景：调研核实 GitHub 并无方案书所述 Citra 工具（同名项目为 3DS 模拟器，2026-09-20
WebSearch 验证），其描述系立项时信息幻觉。所需能力自研：把提取/转换产出的文本
逐段回溯到源 PDF 的页码与坐标，用于 ① MinerU/markitdown 提取质检（内容是否丢/编）
② 论文引用页级溯源。

原理：pymupdf page.search_for 按句检索（长段落先按中英标点切句），
命中即记 {页码, bbox, 命中句数/总句数}；整段未命中 = 疑似丢失或幻觉。

用法：
    python evidence_trace.py 源.pdf --md 提取结果.md -o 证据账本.json
    python evidence_trace.py 源.pdf --claim "某句话" [--claim "另一句"...]
    python office.py trace 源.pdf --md 提取结果.md

退出码：0 全部段落命中；1 存在未命中段落（账本列出）；2 参数/文件错误。
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 句读：中英句读 + 换行；'.' 仅在不夹数字时作边界（保护 3.0 / 1.5 类小数）
_SENT_SPLIT = re.compile(r'(?<=[。！？；])\s*|(?<=[^0-9])[.!?](?![0-9])\s*|(?<=[^0-9])\.(?=[^0-9])\s*|\n+')
_KEEP = re.compile(r'[^一-鿿\w]', re.UNICODE)
_INLINE_MATH = re.compile(r'\$\$(.+?)\$\$|\$([^$]+)\$')
_META_LINE = re.compile(r'^\s*(>\s*)?(副标题|作者|单位|学校|日期)\s*[：:]')
_MATH_BLOCK = re.compile(r'^\s*\$\$')


def _norm(s):
    """NFKC 归一（数学斜体 𝑘→k、全角→半角）+ 只留汉字/字母/数字——
    抹平弯直引号、破折号、全半角括号等排版差异"""
    return _KEEP.sub('', unicodedata.normalize('NFKC', s))


def _defuse_math(p):
    """行内公式剥壳不剥字：$k$→k、$(k+m)/k$→(k+m)/k、\\le 等命令词删除——
    PDF 提取文本里数学字母照常存在，剥掉反而失配"""
    def repl(m):
        body = m.group(1) or m.group(2) or ''
        body = re.sub(r'\\[a-zA-Z]+', '', body)
        return re.sub(r'[\\{}$]', '', body)
    return _INLINE_MATH.sub(repl, p)


def _sentences(paragraph, max_len=60):
    """段落切句：公式剥壳 → 规范化 → 过长句截前缀"""
    paragraph = _defuse_math(paragraph)
    out = []
    for sent in _SENT_SPLIT.split(paragraph):
        n = _norm(sent)
        if len(n) >= 4:
            out.append(n[:max_len])
    return out


def _search_all(doc, needle):
    """全文档检索，返回 (页码(1-based), bbox) 或 None；search_for 对
    跨行文本会失配，故失败时退化为逐页 get_text 包含判断"""
    import pymupdf
    for pno in range(len(doc)):
        hits = doc[pno].search_for(needle)
        if hits:
            return pno + 1, [round(v, 1) for v in hits[0]]
    for pno in range(len(doc)):
        if needle in _norm(doc[pno].get_text()):
            return pno + 1, None
    return None


def trace(paragraphs, pdf_path):
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    ledger = []
    for i, para in enumerate(paragraphs, 1):
        sents = _sentences(para)
        if not sents:
            continue
        pages, matched = [], 0
        for s in sents:
            r = _search_all(doc, s)
            if r:
                matched += 1
                if r[0] not in pages:
                    pages.append(r[0])
        ledger.append({
            'id': i,
            'text': para.strip()[:60],
            'sentences': len(sents),
            'matched': matched,
            'ratio': round(matched / len(sents), 2),
            'pages': pages,
            'status': 'ok' if matched == len(sents)
                      else ('partial' if matched else 'MISS'),
        })
    doc.close()
    return ledger


def _md_paragraphs(md_text):
    """MD → 有效段落（剥标题/引用标记/表格线/图片行，跳代码块）"""
    paras, buf, in_fence = [], [], False
    for line in md_text.split('\n'):
        if line.strip().startswith(('```', '~~~')):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _META_LINE.match(line) or _MATH_BLOCK.match(line):
            continue  # 元信息行/独立公式块不参与回溯（渲染形态不同，非丢失）
        t = re.sub(r'^\s*(#{1,6}\s+|>\s?|[-*+]\s+|\d{1,3}[.)]\s+)', '', line)
        t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', t)
        t = re.sub(r'\*{1,2}|`', '', t).strip()
        if not t or set(t) <= set('|-: '):
            if buf:
                paras.append(' '.join(buf)); buf = []
            continue
        buf.append(t)
    if buf:
        paras.append(' '.join(buf))
    return paras


def main():
    ap = argparse.ArgumentParser(description='提取证据回溯：文本段落 → 源 PDF 页码坐标')
    ap.add_argument('pdf', help='源 PDF')
    ap.add_argument('--md', help='提取结果 Markdown（逐段回溯）')
    ap.add_argument('--claim', action='append', default=[],
                    help='单条论断文本，可多次传入（与 --md 可并用）')
    ap.add_argument('-o', '--output', help='证据账本 JSON 输出路径')
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f'[ERROR] PDF 不存在: {pdf}', file=sys.stderr)
        return 2
    paragraphs = []
    if args.md:
        md = Path(args.md)
        if not md.exists():
            print(f'[ERROR] MD 不存在: {md}', file=sys.stderr)
            return 2
        paragraphs += _md_paragraphs(md.read_text(encoding='utf-8'))
    paragraphs += args.claim
    if not paragraphs:
        print('[ERROR] 需至少提供 --md 或一个 --claim', file=sys.stderr)
        return 2

    ledger = trace(paragraphs, pdf)
    n_ok = sum(1 for e in ledger if e['status'] == 'ok')
    n_part = sum(1 for e in ledger if e['status'] == 'partial')
    n_miss = sum(1 for e in ledger if e['status'] == 'MISS')
    print(f'[账本] 段落 {len(ledger)}：完整命中 {n_ok} | 部分 {n_part} | 未命中 {n_miss}')
    for e in ledger:
        if e['status'] != 'ok':
            mark = 'MISS' if e['status'] == 'MISS' else '部分'
            print(f"  [{mark}] {e['matched']}/{e['sentences']} 句 | {e['text']!r}")
    if args.output:
        Path(args.output).write_text(
            json.dumps({'source': str(pdf), 'entries': ledger}, ensure_ascii=False, indent=2),
            encoding='utf-8')
        print(f'[输出] 证据账本 → {args.output}')
    return 0 if n_miss == 0 and n_part == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
