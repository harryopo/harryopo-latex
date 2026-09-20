#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
style_profile.py — 模板样式档案提取与保真校验（方案书 v3 P2 模板注册表 v2）

思路（brand-docs Profile 抽取的对标实现）：把 docx 的"样式指纹"抽成 JSON 档案
（页边距 / Normal 正文 字体字号行距 / Heading1-3 标题字体字号），
再用档案校验任意产物 docx 是否保真——注册表模板从此有机器可比的样式真值。

用法：
    python style_profile.py extract 模板.docx -o profile.json
    python style_profile.py check   产物.docx --profile profile.json [--json]

退出码：0 全部一致；1 存在偏差；2 文件/参数错误。
容差：字号 ±0.5pt、边距 ±0.05cm、行距倍率 ±0.15；字体名精确匹配。
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TOL_SIZE = 0.5      # pt
TOL_MARGIN = 0.05   # cm
TOL_LINE = 0.15


def _cm(emu):
    return round(emu / 360000.0, 2) if emu is not None else None


def _pt(size_obj):
    return round(size_obj.pt, 1) if size_obj else None


def extract(docx_path):
    from docx import Document
    from docx.enum.style import WD_STYLE_TYPE
    doc = Document(str(docx_path))
    sec = doc.sections[0]
    profile = {
        'schema': 'style-profile-v1',
        'source': str(docx_path),
        'margins': {'top_cm': _cm(sec.top_margin), 'bottom_cm': _cm(sec.bottom_margin),
                    'left_cm': _cm(sec.left_margin), 'right_cm': _cm(sec.right_margin)},
        'styles': {},
    }

    def _read_style(st):
        from docx.enum.text import WD_LINE_SPACING
        from docx.shared import Length
        f = st.font
        pf = st.paragraph_format
        from docx.oxml.ns import qn
        east = None
        rPr = st.element.find('.//' + qn('w:rPr'))
        if rPr is not None:
            rf = rPr.find(qn('w:rFonts'))
            if rf is not None:
                east = rf.get(qn('w:eastAsia'))
        ls = pf.line_spacing
        line = None
        if ls is not None:
            if isinstance(ls, Length) or pf.line_spacing_rule in (
                    WD_LINE_SPACING.EXACTLY, WD_LINE_SPACING.AT_LEAST):
                line = {'rule': 'exact' if pf.line_spacing_rule == WD_LINE_SPACING.EXACTLY
                        else 'at_least', 'pt': round(float(ls.pt), 1)}
            else:
                line = {'rule': 'multiple', 'value': round(float(ls), 2)}
        return {'east_asia': east, 'ascii': f.name, 'size_pt': _pt(f.size),
                'bold': f.bold, 'line': line}

    want = {'Normal': 'body'}
    for idx in (1, 2, 3):
        want[f'Heading {idx}'] = f'h{idx}'
    for st in doc.styles:
        if st.type == WD_STYLE_TYPE.PARAGRAPH and st.name in want:
            profile['styles'][want[st.name]] = _read_style(st)
    return profile


def check(docx_path, profile):
    actual = extract(docx_path)
    diffs = []

    def _cmp(path, a, b, kind='exact'):
        if a is None and b is None:
            return
        if a is None:
            diffs.append(f'{path}: 模板={b!r} 产物未定义')
            return
        if b is None:
            diffs.append(f'{path}: 模板未定义 产物={a!r}')
            return
        if kind == 'pt' and abs(a - b) <= TOL_SIZE:
            return
        if kind == 'cm' and abs(a - b) <= TOL_MARGIN:
            return
        if kind == 'line':
            if a.get('rule') != b.get('rule'):
                diffs.append(f'{path}: 模板={b!r} 产物={a!r}')
                return
            av, bv = a.get('pt', a.get('value')), b.get('pt', b.get('value'))
            if av is not None and bv is not None and abs(av - bv) <= (
                    TOL_SIZE if 'pt' in a else TOL_LINE):
                return
            diffs.append(f'{path}: 模板={b!r} 产物={a!r}')
            return
        if a != b:
            diffs.append(f'{path}: 模板={b!r} 产物={a!r}')

    for k, v in profile.get('margins', {}).items():
        _cmp(f'margins.{k}', actual['margins'].get(k), v, kind='cm')
    for role, exp in profile.get('styles', {}).items():
        act = actual['styles'].get(role)
        if act is None:
            diffs.append(f'styles.{role}: 产物无此样式')
            continue
        for attr in ('east_asia', 'ascii', 'bold'):
            _cmp(f'styles.{role}.{attr}', act.get(attr), exp.get(attr))
        _cmp(f'styles.{role}.size_pt', act.get('size_pt'), exp.get('size_pt'), kind='pt')
        _cmp(f'styles.{role}.line', act.get('line'), exp.get('line'), kind='line')
    return actual, diffs


def main():
    ap = argparse.ArgumentParser(description='docx 样式档案：extract 提取 / check 保真校验')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p_e = sub.add_parser('extract')
    p_e.add_argument('docx')
    p_e.add_argument('-o', '--output', required=True)
    p_c = sub.add_parser('check')
    p_c.add_argument('docx')
    p_c.add_argument('--profile', required=True, help='profile.json 路径')
    p_c.add_argument('--json', action='store_true', help='输出 JSON（供 AI 消费）')
    args = ap.parse_args()

    if args.cmd == 'extract':
        docx = Path(args.docx)
        if not docx.exists():
            print(f'[ERROR] 不存在: {docx}', file=sys.stderr)
            return 2
        prof = extract(docx)
        Path(args.output).write_text(
            json.dumps(prof, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'[OK] 样式档案 → {args.output}（{len(prof["styles"])} 个样式角色）')
        return 0

    docx = Path(args.docx)
    prof_path = Path(args.profile)
    if not docx.exists() or not prof_path.exists():
        print('[ERROR] docx 或 profile 不存在', file=sys.stderr)
        return 2
    profile = json.loads(prof_path.read_text(encoding='utf-8'))
    _, diffs = check(docx, profile)
    if args.json:
        print(json.dumps({'pass': not diffs, 'diffs': diffs}, ensure_ascii=False, indent=2))
    else:
        if diffs:
            print(f'[✗ 偏差] {len(diffs)} 项：')
            for d in diffs:
                print(f'   - {d}')
        else:
            print('[✓ 保真] 产物样式与模板档案全部一致')
    return 0 if not diffs else 1


if __name__ == '__main__':
    sys.exit(main())
