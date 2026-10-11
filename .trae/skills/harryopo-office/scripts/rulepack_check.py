#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
rulepack_check — 规范包驱动的排版合规检查
==========================================

检查参数来自**规则包**（rules/ 目录下的 YAML，schema: harryopo-rulepack/1），
检查器本身与具体规范解耦：同一套代码可服务 GB/T 9704 公文、学校学位论文规范、
期刊格式要求等（自制方法见 rules/README.md）。

对 .docx（python-docx 读节属性/正文样式）或 .tex/.cls（解析 geometry/字号/行距）
做参数对照，输出偏差清单。纯本地检查，无网络依赖。

用法：
  python rulepack_check.py 文件.docx [--pack gbt9704-2012]
  python rulepack_check.py 文件.tex [--pack my-school-2026]   # 自动从 gov 选项下沉 cls 校验
  python rulepack_check.py --list-packs
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
RULES_DIR = SCRIPT_DIR.parent / 'rules'
DEFAULT_PACK = 'gbt9704-2012'


def _ok(flag: bool) -> str:
    return 'PASS' if flag else 'FAIL'


# ============ 规则包加载 ============

def list_packs() -> list:
    if not RULES_DIR.exists():
        return []
    return sorted(p.stem for p in RULES_DIR.glob('*.yaml'))


def load_pack(name: str) -> dict:
    """按名称或路径加载规则包。查找顺序：显式路径 → rules/<name>.yaml → 当前目录。"""
    import yaml
    cand = [Path(name)] if ('/' in name or '\\' in name or name.endswith('.yaml')) else []
    cand += [RULES_DIR / f'{name}.yaml', Path.cwd() / f'{name}.yaml']
    p = next((c for c in cand if c.exists()), None)
    if p is None:
        avail = ', '.join(list_packs()) or '(无)'
        raise FileNotFoundError(f'规则包不存在: {name}（可用: {avail}；自制方法见 rules/README.md）')
    pack = yaml.safe_load(p.read_text(encoding='utf-8'))
    if not isinstance(pack, dict) or pack.get('schema') != 'harryopo-rulepack/1':
        raise ValueError(f'规则包格式错误（缺 schema: harryopo-rulepack/1）: {p}')
    pack['_path'] = str(p)
    return pack


# ============ .docx 模式 ============

def check_docx(path: Path, pack: dict) -> dict:
    from docx import Document

    cfg = pack.get('docx') or {}
    d = Document(str(path))
    s = d.sections[0]
    items = []

    page = cfg.get('page')
    if page:
        page_w, page_h = s.page_width.mm, s.page_height.mm
        items.append((f"页面尺寸（{page['width_mm']:g}×{page['height_mm']:g}mm）",
                      f'{page_w:.1f}×{page_h:.1f}mm',
                      abs(page_w - page['width_mm']) <= page['tol_mm']
                      and abs(page_h - page['height_mm']) <= page['tol_mm'],
                      page.get('basis', '')))
    for key, label in (('top', '上'), ('bottom', '下'), ('left', '左'), ('right', '右')):
        spec = (cfg.get('margins') or {}).get(key)
        if not spec:
            continue
        got = getattr(s, f'{key}_margin').mm
        want = spec['mm']
        items.append((f'{label}边距 {want:g}mm', f'{got:.1f}mm',
                      abs(got - want) <= spec['tol_mm'], spec.get('basis', '')))

    # 正文样式：第一个 ≥30 字的非空段（跳过标题/目录区）
    body = None
    for p in d.paragraphs:
        t = p.text.strip()
        if len(t) >= 30 and '\t' not in t:
            body = p
            break
    body_cfg = cfg.get('body') or {}
    if body is None:
        items.append(('正文样式', '未找到正文段', False, '正文'))
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
        size_pt = body_cfg.get('size_pt')
        if size_pt:
            items.append((f'正文字号 {size_pt:g}pt',
                          f'{pt:.1f}pt' if pt else '未显式设置',
                          pt is not None and abs(pt - size_pt) <= body_cfg.get('tol_pt', 0.6),
                          body_cfg.get('size_basis', '')))
        keywords = body_cfg.get('font_keywords')
        if keywords:
            hit = bool(east and any(k.lower() in (east or '').lower() for k in keywords))
            items.append((f"正文字体（{'/'.join(map(str, keywords))}）",
                          east or '未显式设置', hit, body_cfg.get('font_basis', '')))
        line_cfg = cfg.get('line')
        if line_cfg:
            ls = body.paragraph_format.line_spacing
            if ls is None:
                items.append((f"正文行距 {line_cfg['pt']:g} 磅（固定值）",
                              '未显式设置（默认单倍）', False, line_cfg.get('basis', '')))
            elif isinstance(ls, float) and ls < 3:
                items.append((f"正文行距 {line_cfg['pt']:g} 磅（固定值）",
                              f'{ls} 倍行距', False,
                              line_cfg.get('basis', '') + '（应设固定值行距）'))
            else:
                got_pt = ls.pt if hasattr(ls, 'pt') else float(ls)
                items.append((f"正文行距 {line_cfg['pt']:g} 磅（固定值）",
                              f'{got_pt:.1f}磅',
                              abs(got_pt - line_cfg['pt']) <= line_cfg['tol_pt'],
                              line_cfg.get('basis', '')))

    return {'file': str(path), 'mode': 'docx', 'pack': pack['name'], 'items': items}


# ============ .tex / .cls 模式 ============

def check_tex(path: Path, pack: dict) -> dict:
    text = path.read_text(encoding='utf-8', errors='replace')
    items = []
    cfg = pack.get('tex') or {}
    suffix = path.suffix.lower()
    is_doc = suffix == '.tex'
    gov_on = bool(re.search(r'\\documentclass\[[^\]]*gov[^\]]*\]', text)) \
        if is_doc else ('\\if@govmode' in text)

    if is_doc:
        # 生成的 .tex：公文参数在 cls 里——先验证 gov 选项，再定位 cls 检查参数
        if not gov_on:
            items.append(('\\documentclass 含 gov 选项', '无 gov',
                          False, 'gov 公文模式未启用（convert.py --gov）'))
            return {'file': str(path), 'mode': 'tex', 'pack': pack['name'], 'items': items}
        items.append(('\\documentclass 含 gov 选项', '有 gov', True, 'gov 模式启用'))
        # 定位 harryopo-paper.cls：同目录 → 项目根 templates/cls → skill 内嵌
        cand = [path.parent / 'harryopo-paper.cls',
                path.parent.parent / 'templates' / 'cls' / 'harryopo-paper.cls',
                Path('templates/cls/harryopo-paper.cls'),
                Path('.trae/skills/harryopo-office/templates/cls/harryopo-paper.cls')]
        cls_file = next((c for c in cand if c.exists()), None)
        if cls_file is None:
            items.append(('定位 harryopo-paper.cls', '未找到', False, 'TEXINPUTS 路径'))
            return {'file': str(path), 'mode': 'tex', 'pack': pack['name'], 'items': items}
        cls_result = check_tex(cls_file, pack)
        items.extend(cls_result['items'])
        return {'file': f'{path} (via {cls_file.name})', 'mode': 'tex',
                'pack': pack['name'], 'items': items}

    # .cls / .sty：直接解析参数（gov 分支 + 全局 geometry）
    # 锚定行首的 \if@govmode（排除 \newif\if@govmode 声明行），非贪婪到分支结束 \fi
    gov_branch = re.search(r'(?m)^\\if@govmode\n([\s\S]*?)\\fi', text)
    target = gov_branch.group(1) if gov_branch else text

    margins = cfg.get('margins') or {}
    geom = re.search(r'\\geometry\{([^}]*)\}', target) or re.search(r'\\geometry\{([^}]*)\}', text)
    if geom:
        spec = geom.group(1)
        for key, label in (('top', '上'), ('bottom', '下'), ('left', '左'), ('right', '右')):
            mspec = margins.get(key)
            if not mspec:
                continue
            m = re.search(key + r'\s*=\s*([\d.]+)\s*(cm|mm)?', spec)
            if not m:
                continue
            val = float(m.group(1)) * (10 if (m.group(2) or 'cm') == 'cm' else 1)
            want = mspec['mm']
            items.append((f'{label}边距 {want:g}mm', f'{val:.1f}mm',
                          abs(val - want) <= mspec['tol_mm'], mspec.get('basis', '')))
    elif margins:
        items.append(('页边距（geometry）', '未找到 \\geometry', False, '2.2 页边距'))

    zh = cfg.get('body_zihao')
    ls_cfg = cfg.get('linespread')
    if gov_branch or gov_on:
        if zh:
            has = re.search(r'\\zihao\{' + re.escape(str(zh['value'])) + r'\}', text) is not None
            items.append((f"正文 \\zihao{{{zh['value']}}}", '有' if has else '无',
                          has, zh.get('basis', '')))
        if ls_cfg:
            ls = re.search(r'\\linespread\{([\d.]+)\}', text)
            val = float(ls.group(1)) if ls else None
            ok = val is not None and abs(val - ls_cfg['value']) <= ls_cfg.get('tol', 0.05)
            pt_label = ls_cfg.get('pt_label')
            label = f"行距 {pt_label} 磅（linespread {ls_cfg['value']}）" if pt_label \
                else f"行距（linespread {ls_cfg['value']}）"
            items.append((label, f'{val}' if val else '未设置', ok, ls_cfg.get('basis', '')))
        for hf in cfg.get('heading_fonts') or []:
            hit = bool(re.search(r'\\' + re.escape(hf['macro']) + r'\}', target))
            items.append((hf['label'], '有' if hit else '无', hit, hf.get('basis', '')))
    elif zh or ls_cfg or cfg.get('heading_fonts'):
        items.append(('公文参数区（gov 模式）', '未声明 gov 选项/分支',
                      False, '检查 --gov 模式或 gov 分支'))

    return {'file': str(path), 'mode': 'tex', 'pack': pack['name'], 'items': items}


# ============ 输出 ============

def report(result: dict) -> int:
    print(f"=== {result['pack']} 合规检查: {Path(result['file']).name} "
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
        description='规范包驱动的排版合规检查（.docx / .tex / .cls；内置 GB/T 9704-2012）')
    ap.add_argument('file', nargs='?', help='待检查文件（.docx 或 .tex/.cls/.sty）')
    ap.add_argument('--pack', default=DEFAULT_PACK,
                    help=f'规则包名或 YAML 路径（默认 {DEFAULT_PACK}）')
    ap.add_argument('--list-packs', action='store_true', help='列出内置规则包')
    ap.add_argument('--json', action='store_true', help='输出 JSON（供 AI 消费）')
    args = ap.parse_args()

    if args.list_packs:
        for p in list_packs():
            print(p)
        return 0
    if not args.file:
        ap.print_help()
        return 0
    path = Path(args.file)
    if not path.exists():
        print(f'[FATAL] 文件不存在: {path}', file=sys.stderr)
        return 2

    try:
        pack = load_pack(args.pack)
    except (FileNotFoundError, ValueError) as exc:
        print(f'[FATAL] {exc}', file=sys.stderr)
        return 2

    if path.suffix.lower() == '.docx':
        result = check_docx(path, pack)
    elif path.suffix.lower() in ('.tex', '.cls', '.sty'):
        result = check_tex(path, pack)
    else:
        print('[FATAL] 仅支持 .docx / .tex / .cls / .sty', file=sys.stderr)
        return 2

    if args.json:
        items = [{'item': a, 'actual': b, 'pass': c, 'basis': d}
                 for a, b, c, d in result['items']]
        print(json.dumps({'file': result['file'], 'mode': result['mode'],
                          'pack': result['pack'], 'items': items},
                         ensure_ascii=False, indent=2))
    else:
        return report(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
