#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docx_clean.py — Pandoc DOCX→MD 输出清洗层

Pandoc 的 markdown 输出对 harryopo 转换链路不友好，存在以下问题，
本模块逐项清洗，保证 convert.py 能正确解析：

1. Word TOC 域 → 嵌套锚点链接（[一、引言 [2](#一引言)](#一引言)），直接进 LaTeX 会乱码
2. 方括号被转义为 [ 和 ]（LaTeX 显示数学命令），文本中出现会报 Missing $
3. 表格输出为无管道 simple table，convert.py 的管道表格正则无法识别
4. 公式/文本中的 Unicode 上下标（₀ ᵢ ⁻ˣ ŷ）XITSMath 无字形 → Missing character
5. 大标题（非 Heading 样式）pandoc 不输出 `#` 标记 → \title 错位
6. 图片占位区文本 `[图片占位区]` 显示为裸文本

用法：
    from docx_clean import clean_pandoc_md
    md_text = clean_pandoc_md(raw_pandoc_md)
"""

import re

# ============================================================
# 1. 删除文档头部的 TOC 区
# ============================================================

def _strip_toc(text: str) -> str:
    """删除 pandoc/anydoc 从 Word TOC 域转出的目录导航区"""
    lines = text.split('\n')
    i = 0
    # 跳过开头空行
    while i < len(lines) and not lines[i].strip():
        i += 1
    # TOC 区从 '目 录'/'目录'/'目   录'（任意空格）行开始
    if i < len(lines) and re.match(r'^目\s*录$', lines[i].strip()):
        i += 1
        while i < len(lines):
            ln = lines[i].strip()
            if not ln or ln == '>':
                # 空行 / 空引用行（TOC 缩进层级间的占位）
                i += 1
            elif '](#' in ln:
                # 锚点链接行（含跨行 TOC 的续行）
                i += 1
            elif ln.startswith('>') or ln.startswith('['):
                # > 前缀的 TOC 层级行 / 可能的跨行 TOC 起始
                i += 1
            else:
                break
    return '\n'.join(lines[i:])


# ============================================================
# 2. Pandoc 特殊字符反转义
# ============================================================
# 注意：只有 `\[ \] \< \> \"` 需要反转义。
# `\_ \# \& \% \$ \{ \}` 在 LaTeX 中本身就是正确显示形式，绝不能反转义
# （`_` 会触发数学下标、`#`/`%` 是注释、`&` 是表格列分隔、`{` 会缺右括号）。

def _unescape_pandoc(text: str) -> str:
    """反转义 pandoc markdown 转义字符"""
    for esc, raw in (
        (r'\[', '['),
        (r'\]', ']'),
        (r'\<', '<'),
        (r'\>', '>'),
        (r'\"', '"'),
        (r'\*', '*'),
    ):
        text = text.replace(esc, raw)
    return text


# ============================================================
# 3. 大标题识别（pandoc 对非 Heading 样式不输出 #）
# ============================================================

def _fix_big_title(text: str) -> str:
    """将 `标题\n\n------副标题` 结构合并为 `# 标题——副标题`"""
    lines = text.split('\n')
    # 找第一个非空行
    idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if idx is None:
        return text
    title_line = lines[idx].strip()
    if title_line.startswith('#') or len(title_line) > 60:
        return text
    # 找下一个非空行（应为分隔线/副标题行）
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines):
        return text
    m = re.match(r'^(?:-{3,}|—{1,2})\s*(.*)$', lines[j].strip())
    if not m:
        return text
    subtitle = m.group(1).strip()
    new_title = title_line
    if subtitle:
        new_title += '——' + subtitle
    # 用 # 标题替换原标题行，删除副标题行
    new_lines = lines[:idx] + [f'# {new_title}', ''] + lines[j + 1:]
    return '\n'.join(new_lines)


# ============================================================
# 4. 图片占位区合并为图片引用
# ============================================================

def _fix_image_placeholders(text: str) -> str:
    """[图片占位区]（含反斜杠转义形式）+ 后随 图N：xxx → ![图N：xxx](figures/placeholder.png)

    兼容两种转义风格：pandoc 对称转义 `\\[...\\]`、anydoc 仅转义 `\\[...]`。
    """
    # 带图标题的占位：占位文本 + 空行 + 图N：xxx
    pat1 = re.compile(
        r'\\?\[?图片占位区\\?\]?\s*\n+\s*(图\s*\d+\s*[：:][^\n]+)'
    )
    text = pat1.sub(
        lambda m: f'![{m.group(1).strip()}](figures/placeholder.png)', text)
    # 无图标题的孤立占位
    pat2 = re.compile(r'\\?\[?图片占位区\\?\]?')
    text = pat2.sub('![图片占位区](figures/placeholder.png)', text)
    return text


# ============================================================
# 5. Simple table 处理
# ============================================================
# pandoc 的 simple table 按 CJK 双宽计算列位置，单字符位置切分必然错位，
# 因此：直接删除 pandoc 表格块，改用 python-docx 提取的准确表格回填。

def _is_horizontal_rule(line: str) -> bool:
    """顶线/底线：整行缩进 + 10 个以上连续 '-'（单 run）"""
    s = line.strip()
    return len(s) >= 10 and bool(re.fullmatch(r'-{10,}', s))


def _remove_simple_tables(text: str):
    """删除 pandoc simple table 块，返回 (清洗后文本, 删除的表格数)"""
    lines = text.split('\n')
    out = []
    i = 0
    n = 0
    while i < len(lines):
        if _is_horizontal_rule(lines[i]):
            j = i + 1
            while j < len(lines) and not _is_horizontal_rule(lines[j]):
                j += 1
            if j < len(lines) and j - i > 2:
                n += 1
                i = j + 1
                continue
        out.append(lines[i])
        i += 1
    return '\n'.join(out), n


def extract_docx_tables(docx_path: str) -> list:
    """用 python-docx 按文档流顺序提取表格（list[list[list[str]]]）

    python-docx 缺失时抛 ImportError——调用方（pandoc 链路）必须硬失败，
    静默返回空表会导致表格丢失且无提示。
    """
    import docx
    from docx.table import Table
    from docx.oxml.ns import qn
    doc = docx.Document(docx_path)
    tables = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn('w:tbl'):
            tbl = Table(child, doc)
            rows = []
            for row in tbl.rows:
                cells = []
                for c in row.cells:
                    # 单元格内换行合并为空格；竖线换成全角避免破坏管道表
                    t = c.text.strip().replace('\n', ' ').replace('|', '｜')
                    cells.append(t)
                rows.append(cells)
            tables.append(rows)
    return tables


def insert_tables_after_captions(md_text: str, tables: list) -> str:
    """把 python-docx 表格按序插到对应 `表N：` 标题之后"""
    if not tables:
        return md_text
    cap_re = re.compile(r'^(表\s*\d+\s*[：:][^\n]*)$', re.MULTILINE)
    matches = list(cap_re.finditer(md_text))
    if not matches:
        return md_text
    chunks = []
    last = 0
    for idx, m in enumerate(matches):
        chunks.append(md_text[last:m.end()])
        if idx < len(tables):
            rows = tables[idx]
            if rows:
                header = '| ' + ' | '.join(rows[0]) + ' |'
                sep = '|' + '|'.join(['---'] * len(rows[0])) + '|'
                body = '\n'.join(
                    '| ' + ' | '.join(r) + ' |' for r in rows[1:] if r)
                chunks.append('\n\n' + header + '\n' + sep +
                              ('\n' + body if body else '') + '\n')
        last = m.end()
    chunks.append(md_text[last:])
    return ''.join(chunks)


# ============================================================
# 6. Unicode 数学字符映射
# ============================================================

_SUB_CHARS = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    'ᵢ': 'i', 'ⱼ': 'j', 'ₓ': 'x',
}
_SUP_CHARS = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁻': '-', 'ˣ': 'x', 'ⁿ': 'n',
}
_SUB_RE = re.compile('[' + ''.join(_SUB_CHARS.keys()) + ']')
_SUP_RE = re.compile('[' + ''.join(_SUP_CHARS.keys()) + ']')

# 数学符号 → LaTeX 命令（公式内与文本内通用）
_SYM_MAP = {
    'Σ': r'\Sigma',
    '∏': r'\prod',
    '∈': r'\in',
    '∉': r'\notin',
    '≤': r'\leq',
    '≥': r'\geq',
    '×': r'\times',
    '÷': r'\div',
    '·': r'\cdot',
    '√': r'\sqrt',
    '∞': r'\infty',
    '→': r'\rightarrow',
    '←': r'\leftarrow',
    '⇒': r'\Rightarrow',
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
    'θ': r'\theta', 'λ': r'\lambda', 'μ': r'\mu', 'π': r'\pi',
    'σ': r'\sigma', 'τ': r'\tau', 'φ': r'\phi', 'ω': r'\omega',
    'Δ': r'\Delta', 'Λ': r'\Lambda', 'Θ': r'\Theta',
}


def _sub_suffix(chars: str) -> str:
    return ''.join(_SUB_CHARS[c] for c in chars)


def _sup_suffix(chars: str) -> str:
    return ''.join(_SUP_CHARS[c] for c in chars)


def _fix_math_region(m: re.Match) -> str:
    """$$...$$ 公式块内的 Unicode 修复（数学模式语法）"""
    s = m.group(1)
    # ŷ → \hat{y}（优先处理，避免残留 Unicode）
    s = s.replace('ŷ', r'\hat{y}').replace('Ŷ', r'\hat{Y}')
    # 上标序列：e⁻ˣ → e^{-x}
    s = re.sub(r'([A-Za-z)])((?:[⁰¹²³⁴⁵⁶⁷⁸⁹⁻ˣⁿ])+)',
               lambda m2: m2.group(1) + '^{' + _sup_suffix(m2.group(2)) + '}', s)
    # 下标序列：wᵢ → w_i
    s = re.sub(r'([A-Za-z)])((?:[₀₁₂₃₄₅₆₇₈₉ᵢⱼₓ])+)',
               lambda m2: m2.group(1) + '_' + _sub_suffix(m2.group(2)), s)
    # 数学符号
    for ch, latex in _SYM_MAP.items():
        s = s.replace(ch, latex)
    return '$$' + s + '$$'


def _fix_text_unicode(text: str) -> str:
    """普通文本中的 Unicode 修复（行内数学包裹）"""
    # ŷ 组合下标：ŷᵢ → $\hat{y}_{i}$
    text = re.sub(r'ŷ((?:[₀₁₂₃₄₅₆₇₈₉ᵢⱼₓ])+)',
                  lambda m: r'$\hat{y}_{' + _sub_suffix(m.group(1)) + '}$', text)
    text = text.replace('ŷ', r'$\hat{y}$').replace('Ŷ', r'$\hat{Y}$')
    # 下标：C₀ → C$_{0}$
    text = re.sub(r'([A-Za-z)])((?:[₀₁₂₃₄₅₆₇₈₉ᵢⱼₓ])+)',
                  lambda m: m.group(1) + '$_{' + _sub_suffix(m.group(2)) + '}$', text)
    # 数学符号 → 文本模式保持原字符（XITS 英文字体支持 α σ ∈ 等）
    return text


def _fix_unicode_math(text: str) -> str:
    """先修公式块，再修普通文本"""
    text = re.sub(r'\$\$([\s\S]*?)\$\$', _fix_math_region, text)
    text = _fix_text_unicode(text)
    return text


# ============================================================
# 主编排
# ============================================================

def clean_pandoc_md(text: str, docx_tables: list = None) -> str:
    """Pandoc DOCX→MD 全量清洗入口

    docx_tables: python-docx 提取的表格列表（list[list[list[str]]]），
                 用于回填被删除的 pandoc simple table。
    """
    text = _strip_toc(text)               # 1. 删 TOC 导航
    text = _fix_big_title(text)           # 2. 大标题 → # 标题
    text = _fix_image_placeholders(text)  # 3. 图片占位合并（在反转义前，保持 \[ 原样）
    text = _unescape_pandoc(text)         # 4. 反转义 \[ \] \< \> \" \*
    text, n_tables = _remove_simple_tables(text)  # 5. 删除 pandoc simple table
    text = insert_tables_after_captions(text, docx_tables)  # 5.5 回填准确表格
    text = _fix_unicode_math(text)        # 6. Unicode 数学映射
    return text


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法: python docx_clean.py <pandoc_md> [output_md]')
        sys.exit(1)
    src = sys.argv[1]
    raw = open(src, encoding='utf-8').read()
    cleaned = clean_pandoc_md(raw)
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f'[OK] 清洗完成: {dst}')
