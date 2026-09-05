#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gb9704_check — GB/T 9704-2012《党政机关公文格式》合规检查
=========================================================

对 .docx（python-docx 读节属性/正文样式）或 .tex/.cls（解析 geometry/字号/行距）
做国标参数对照，输出偏差清单。纯本地检查，无网络依赖。

用法：
  python gb9704_check.py 文件.docx
  python gb9704_check.py 文件.tex [--gov]      # --gov：按 gov 选项声明后的参数期望检查

国标核心参数（GB/T 9704-2012，公开标准）：
  页面        A4（210×297mm）
  页边距      上 37mm  下 35mm  左 28mm  右 26mm（版心 156×225mm）
  正文        三号仿宋（16pt），每面 22 行、每行 28 字（≈28 磅行距）
  标题层级    一、黑体 ｜（一）楷体 ｜ 1. 仿宋加粗 ｜ （1）仿宋
  公文标题    二号小标宋
  页码        四号宋体阿拉伯数字，"—1—"形式
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# GB/T 9704-2012 国标参数
GB = {
    'page': (210.0, 297.0),
    'margins_mm': {'top': 37.0, 'bottom': 35.0, 'left': 28.0, 'right': 26.0},
    'body_pt': 16.0,            # 三号
    'body_font': '仿宋',         # 仿宋_GB2312 / FangZheng FangSong
    'line_pt': 28.0,            # 28 磅行距（≈每面 22 行）
    'tol_mm': 1.0,              # 页边距容差
    'tol_pt': 0.6,              # 字号/行距容差
}


def _ok(flag: bool) -> str:
    return 'PASS' if flag else 'FAIL'


# ============ .docx 模式 ============

def check_docx(path: Path) -> dict:
    from docx import Document

    d = Document(str(path))
    s = d.sections[0]
    items = []
    page_w, page_h = s.page_width.mm, s.page_height.mm
    items.append(('页面尺寸 A4（210×297mm）',
                  f'{page_w:.1f}×{page_h:.1f}mm',
                  abs(page_w - 210) <= 1.5 and abs(page_h - 297) <= 1.5,
                  '2.1 页面'))
    for key, label in (('top', '上'), ('bottom', '下'), ('left', '左'), ('right', '右')):
        got = getattr(s, f'{key}_margin').mm
        want = GB['margins_mm'][key]
        items.append((f'{label}边距 {want}mm', f'{got:.1f}mm',
                      abs(got - want) <= GB['tol_mm'], '2.2 页边距'))

    # 正文样式：第一个 ≥30 字的非空段（跳过标题/目录区）
    body = None
    for p in d.paragraphs:
        t = p.text.strip()
        if len(t) >= 30 and '\t' not in t:
            body = p
            break
    if body is None:
        items.append(('正文样式（三号仿宋/28磅行距）', '未找到正文段', False, '9 正文'))
    else:
        r = body.runs[0] if body.runs else None
        pt = r.font.size.pt if r is not None and r.font.size else None
        east = None
        if r is not None:
            rPr = getattr(r._element, 'rPr', None)
            if rPr is not None:
                rf = rPr.find(
                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
                if rf is not None:
                    east = (rf.get(
                        '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia')
                        or rf.get(
                        '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii'))
        items.append((f'正文字号 {GB["body_pt"]}pt（三号）',
                      f'{pt:.1f}pt' if pt else '未显式设置',
                      pt is not None and abs(pt - GB['body_pt']) <= GB['tol_pt'], '9.2 字体字号'))
        is_fs = bool(east and ('仿宋' in east or 'FangSong' in east.lower() or 'FZFS' in east.upper()))
        items.append(('正文字体 仿宋', east or '未显式设置', is_fs, '9.2 字体字号'))
        ls = body.paragraph_format.line_spacing
        if ls is None:
            items.append(('正文行距 28 磅（固定值）', '未显式设置（默认单倍）', False, '9.3 行距'))
        elif isinstance(ls, float) and ls < 3:
            items.append(('正文行距 28 磅（固定值）', f'{ls} 倍行距', False,
                          '9.3 行距（应设固定值 28 磅，或 LaTeX linespread 1.46）'))
        else:
            got_pt = ls.pt if hasattr(ls, 'pt') else float(ls)
            items.append(('正文行距 28 磅（固定值）', f'{got_pt:.1f}磅',
                          abs(got_pt - GB['line_pt']) <= GB['tol_pt'] + 0.5, '9.3 行距'))

    return {'file': str(path), 'mode': 'docx', 'items': items}


# ============ .tex / .cls 模式 ============

def check_tex(path: Path) -> dict:
    text = path.read_text(encoding='utf-8', errors='replace')
    items = []
    suffix = path.suffix.lower()
    is_doc = suffix == '.tex'
    gov_on = bool(re.search(r'\\documentclass\[[^\]]*gov[^\]]*\]', text)) \
        if is_doc else ('\\if@govmode' in text)

    if is_doc:
        # 生成的 .tex：公文参数在 cls 里——先验证 gov 选项，再定位 cls 检查参数
        if not gov_on:
            items.append(('\\documentclass 含 gov 选项', '无 gov',
                          False, 'gov 公文模式未启用（convert.py --gov）'))
            return {'file': str(path), 'mode': 'tex', 'items': items}
        items.append(('\\documentclass 含 gov 选项', '有 gov', True, 'gov 模式启用'))
        # 定位 harryopo-paper.cls：同目录 → 项目根 templates/cls → skill 内嵌
        cand = [path.parent / 'harryopo-paper.cls',
                path.parent.parent / 'templates' / 'cls' / 'harryopo-paper.cls',
                Path('templates/cls/harryopo-paper.cls'),
                Path('.trae/skills/harryopo-office/templates/cls/harryopo-paper.cls')]
        cls_file = next((c for c in cand if c.exists()), None)
        if cls_file is None:
            items.append(('定位 harryopo-paper.cls', '未找到', False, 'TEXINPUTS 路径'))
            return {'file': str(path), 'mode': 'tex', 'items': items}
        cls_result = check_tex(cls_file)
        items.extend(cls_result['items'])
        return {'file': f'{path} (via {cls_file.name})', 'mode': 'tex', 'items': items}

    # .cls / .sty：直接解析参数（gov 分支 + 全局 geometry）
    # 锚定行首的 \if@govmode（排除 \newif\if@govmode 声明行），非贪婪到分支结束 \fi
    gov_branch = re.search(r'(?m)^\\if@govmode\n([\s\S]*?)\\fi', text)
    target = gov_branch.group(1) if gov_branch else text

    geom = re.search(r'\\geometry\{([^}]*)\}', target) or re.search(r'\\geometry\{([^}]*)\}', text)
    if geom:
        spec = geom.group(1)
        for key, label in (('top', '上'), ('bottom', '下'), ('left', '左'), ('right', '右')):
            m = re.search(key + r'\s*=\s*([\d.]+)\s*(cm|mm)?', spec)
            if not m:
                continue
            val = float(m.group(1)) * (10 if (m.group(2) or 'cm') == 'cm' else 1)
            want = GB['margins_mm'][key]
            items.append((f'{label}边距 {want}mm', f'{val:.1f}mm',
                          abs(val - want) <= GB['tol_mm'], '2.2 页边距'))
    else:
        items.append(('页边距（geometry）', '未找到 \\geometry', False, '2.2 页边距'))

    if gov_branch or gov_on:
        has_zihao3 = re.search(r'\\zihao\{3\}', text) is not None
        items.append(('正文三号（\\zihao{3}）', '有' if has_zihao3 else '无',
                      has_zihao3, '9.2 字体字号'))
        ls = re.search(r'\\linespread\{([\d.]+)\}', text)
        val = float(ls.group(1)) if ls else None
        ok = val is not None and abs(val - 1.46) <= 0.05
        items.append(('行距 28 磅（linespread 1.46）',
                      f'{val}' if val else '未设置', ok, '9.3 行距'))
        for pat, label in ((r'\\fzht\}', '一级标题黑体（\\fzht）'),
                           (r'\\fzkt\}', '二级标题楷体（\\fzkt）'),
                           (r'\\fzfs\}', '三级标题仿宋（\\fzfs）')):
            hit = bool(re.search(pat, target))
            items.append((label, '有' if hit else '无', hit, '9.2 层级字体'))
    else:
        items.append(('公文参数区（gov 模式）', '未声明 gov 选项/分支',
                      False, '检查 --gov 模式或 gov 分支'))

    return {'file': str(path), 'mode': 'tex', 'items': items}


# ============ 输出 ============

def report(result: dict) -> int:
    print(f"=== GB/T 9704-2012 公文格式检查: {Path(result['file']).name} "
          f"({result['mode']}) ===")
    fails = 0
    for label, got, ok, basis in result['items']:
        mark = '✓' if ok else '✗'
        if not ok:
            fails += 1
        print(f'  {mark} {label:<32} 实际: {got}   [{basis}]')
    n = len(result['items'])
    print(f'--- {n - fails}/{n} 项通过，{fails} 项偏差 ---')
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description='GB/T 9704-2012 公文格式合规检查（.docx / .tex / .cls）')
    ap.add_argument('file', help='待检查文件（.docx 或 .tex/.cls）')
    ap.add_argument('--json', action='store_true', help='输出 JSON（供 AI 消费）')
    args = ap.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f'[FATAL] 文件不存在: {path}', file=sys.stderr)
        return 2

    if path.suffix.lower() == '.docx':
        result = check_docx(path)
    elif path.suffix.lower() in ('.tex', '.cls', '.sty'):
        result = check_tex(path)
    else:
        print('[FATAL] 仅支持 .docx / .tex / .cls / .sty', file=sys.stderr)
        return 2

    if args.json:
        items = [{'item': a, 'actual': b, 'pass': c, 'basis': d}
                 for a, b, c, d in result['items']]
        print(json.dumps({'file': result['file'], 'mode': result['mode'],
                          'items': items}, ensure_ascii=False, indent=2))
    else:
        return report(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
