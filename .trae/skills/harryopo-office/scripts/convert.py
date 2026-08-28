#!/usr/bin/env python3
"""
convert.py — harryopo-convert 转换引擎 (v1.0)
Markdown/DOCX → LaTeX (.tex) via harryopo 模板体系

用法：
  python convert.py <input> [options]
  python convert.py report.md --type paper --twocolumn
  python convert.py paper.docx --author "张三"

解析架构：三 Pass
  P1: 块级分割（段落/标题/代码围栏/表格/公式块/列表组）
  P2: 行内元素（粗体/斜体/行内代码/行内公式/链接）
  P3: 骨架组装（documentclass + metadata + body + bib）

依赖：Python 3.7+（零外部依赖，纯标准库正则解析）
DOCX 备选: pip install python-docx   或   pandoc CLI
"""

import re
import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# ============================================================
# 常量
# ============================================================

BLOCK_BIB = "bibliography"
BLOCK_CODE = "code"
BLOCK_FIGURE = "figure"
BLOCK_H1 = "h1"
BLOCK_H2 = "h2"
BLOCK_H3 = "h3"
BLOCK_H4 = "h4"
BLOCK_HR = "hr"
BLOCK_MATH_DISPLAY = "math_display"
BLOCK_OL = "ol"
BLOCK_QUOTE = "quote"
BLOCK_TABLE = "table"
BLOCK_TEXT = "text"
BLOCK_UL = "ul"
BLOCK_RAW_LATEX = "raw_latex"  # MinerU 清洗后的 LaTeX 代码（longtable/tabular 等）

LANG_MAP = {
    "py": "pystyle", "python": "pystyle",
    "sh": "bashstyle", "bash": "bashstyle", "zsh": "bashstyle",
    "plain": "plainstyle", "txt": "plainstyle", "text": "plainstyle",
}

# ============================================================
# Pass 1: 块级分割
# ============================================================

def split_blocks(text: str) -> List[Tuple[str, str]]:
    """将 Markdown 文本分割为 (类型, 内容) 块列表"""
    blocks: List[Tuple[str, str]] = []
    pos = 0
    while pos < len(text):
        # 跳过块之间的空白行
        while pos < len(text) and text[pos] in '\n\r':
            pos += 1
        if pos >= len(text):
            break

        m = None

        # --- LaTeX 原始代码块（MinerU 清洗后的 longtable/tabular 等） ---
        # 先收集 \newlength/\setlength/\newcommand 等 preamble 行
        preamble = ""
        preamble_match = re.match(r'((?:\\newlength\{[^}]+\}|\\setlength\{[^}]+\}\{[^}]+\}|\\newcommand\{[^}]+\}\{[^}]+\}|\\renewcommand\{[^}]+\}\{[^}]+\})\s*\n?)+', text[pos:])
        if preamble_match:
            preamble = preamble_match.group(0)
            pos += preamble_match.end()
            # 跳过空行
            while pos < len(text) and text[pos] in '\n\r':
                pos += 1

        # 匹配 \begin{env}...\end{env}
        m = re.match(r'(\\begin\{(longtable|tabular|tabularx|table|gather|align)\}.*?\\end\{\2\})', text[pos:], re.DOTALL)
        if m:
            blocks.append((BLOCK_RAW_LATEX, preamble + m.group(1)))
            pos += m.end()
            continue
        elif preamble:
            # 有 preamble 但没有 longtable，把 preamble 作为文本输出
            blocks.append((BLOCK_RAW_LATEX, preamble.rstrip()))
            continue

        # --- 代码围栏 ---
        m = re.match(r'```(\w*)\n(.*?)\n```\s*(?:\n|$)', text[pos:], re.DOTALL)
        if m:
            lang = m.group(1).strip().lower() or "plain"
            code = m.group(2)
            blocks.append((BLOCK_CODE, f"{lang}\n{code}"))
            pos += m.end()
            continue

        # --- 标题 ---
        m = re.match(r'####\s+(.*?)$', text[pos:], re.MULTILINE)
        if m:
            blocks.append((BLOCK_H4, m.group(1).strip()))
            pos += m.end()
            continue
        m = re.match(r'###\s+(.*?)$', text[pos:], re.MULTILINE)
        if m:
            blocks.append((BLOCK_H3, m.group(1).strip()))
            pos += m.end()
            continue

        # --- 参考文献区域（必须在 H2 之前检测） ---
        m = re.match(r'(##\s+参考文献|##\s+References|##\s+参考)\s*\n((?:\[.+?\].+\n?)+)', text[pos:])
        if m:
            blocks.append((BLOCK_BIB, m.group(2).strip()))
            pos += m.end()
            continue

        m = re.match(r'##\s+(.*?)$', text[pos:], re.MULTILINE)
        if m:
            blocks.append((BLOCK_H2, m.group(1).strip()))
            pos += m.end()
            continue
        m = re.match(r'#\s+(.*?)$', text[pos:], re.MULTILINE)
        if m:
            blocks.append((BLOCK_H1, m.group(1).strip()))
            pos += m.end()
            continue

        # --- 水平线 ---
        m = re.match(r'(---|\*\*\*|___)\s*$', text[pos:], re.MULTILINE)
        if m:
            blocks.append((BLOCK_HR, ""))
            pos += m.end()
            continue

        # --- 独立行图片 ![alt](path) ---
        m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)\s*(?:\n|$)', text[pos:])
        if m:
            alt = m.group(1)
            src = m.group(2)
            blocks.append((BLOCK_FIGURE, f"{alt}\n{src}"))
            pos += m.end()
            continue

        # --- 表格 ---
        m = re.match(r'(\|.+\|)\n(\|[-:\s|]+\|)\n((?:\|.+\|\n?)+)', text[pos:])
        if m:
            header = m.group(1)
            align  = m.group(2)
            rows   = m.group(3)
            blocks.append((BLOCK_TABLE, f"{header}\n{align}\n{rows.rstrip()}"))
            pos += m.end()
            continue

        # --- 有序列表 ---
        m = re.match(r'((?:\d+\.\s+.*\n?)+)', text[pos:])
        if m:
            raw = m.group(1).strip()
            items = re.findall(r'^\d+\.\s+(.*)$', raw, re.MULTILINE)
            blocks.append((BLOCK_OL, "\n".join(items)))
            pos += m.end()
            continue

        # --- 无序列表 ---
        m = re.match(r'((?:[\-\*\+]\s+.*\n?)+)', text[pos:])
        if m:
            raw = m.group(1).strip()
            items = re.findall(r'^[\-\*\+]\s+(.*)$', raw, re.MULTILINE)
            blocks.append((BLOCK_UL, "\n".join(items)))
            pos += m.end()
            continue

        # --- 引用 ---
        m = re.match(r'((?:>\s?.*\n?)+)', text[pos:])
        if m:
            raw = m.group(1).strip()
            lines = [re.sub(r'^>\s?', '', ln) for ln in raw.split('\n')]
            blocks.append((BLOCK_QUOTE, "\n".join(lines)))
            pos += m.end()
            continue

        # --- 展示公式 ---
        m = re.match(r'\$\$\s*([\s\S]*?)\s*\$\$', text[pos:], re.DOTALL)
        if m:
            blocks.append((BLOCK_MATH_DISPLAY, m.group(1).strip()))
            pos += m.end()
            continue

        # --- 普通段落：匹配直到遇到下一个块标记或文本结束 ---
        # 块标记: 行首的 #, ```, 数字., -, *, +, |, $$, >, ![]()
        # 允许多个换行作为段落边界（处理 \n\n## 模式）
        # 注意：加入 \\begin{ 和 \\end{ 负前瞻，避免在 LaTeX 环境内切割
        # 表格行（\n+|...| 竖线开头）必须终止段落，否则 `表N：` 标题+表格会被
        # 整体吞进 BLOCK_TEXT，导致 _ 触发数学模式、中文进 XITSMath 产生乱码
        m2 = re.match(r'((?:(?!\n+#{1,4}\s|\n+```|\n+\d+\.\s|\n+[\-\*\+]\s|\n+\|[^\n]*\||\n+\$\$|\n+>|\n+(?:##\s+参考)|\n+!\[[^\]]*\]\(|\n+\\begin\{|\n+\\end\{).)+)', text[pos:], re.DOTALL)
        if m2:
            para = m2.group(1).strip()
            if para:
                blocks.append((BLOCK_TEXT, para))
            pos += m2.end()
            continue

        # --- 尾部残余 ---
        rest = text[pos:].strip()
        if rest:
            blocks.append((BLOCK_TEXT, rest))
        break

    return blocks


# ============================================================
# Pass 2: 行内元素解析
# ============================================================

def _escape_latex(text: str) -> str:
    """转义 LaTeX 特殊字符（在普通文本中）"""
    # 在数学公式内不转义
    escape_map = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\^{}",
    }
    for ch, repl in escape_map.items():
        text = text.replace(ch, repl)
    return text


def parse_inline(text: str) -> str:
    """将行内 Markdown 转换为 LaTeX"""
    # 保护数学公式区域（行内）
    math_placeholders: List[str] = []

    def _save_math(m: re.Match) -> str:
        math_placeholders.append(m.group(1))
        return f"\x00MATH{len(math_placeholders)-1}\x00"

    text = re.sub(r'\$([^$]+?)\$', _save_math, text)
    text = re.sub(r'\\\((.*?)\\\)', _save_math, text)

    # 链接 [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  lambda m: f'\\href{{{m.group(2)}}}{{{m.group(1)}}}', text)

    # 行内代码
    text = re.sub(r'`([^`]+)`', r'\\inlinecode{\1}', text)

    # 粗斜体 *** → 黑体（中文无斜体概念，统一用黑体；英文场景可用 \emph）
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'{\\fzht \1}', text)
    # 粗体 ** → 黑体（中文排版规范：强调用黑体而非加粗，避免中文字体加粗后笔画糊）
    text = re.sub(r'\*\*(.+?)\*\*', r'{\\fzht \1}', text)
    # 斜体 * （英文场景保留斜体）
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)

    # 恢复数学公式
    for i, math in enumerate(math_placeholders):
        text = text.replace(f"\x00MATH{i}\x00", f"${math}$")

    return text


def format_author(author_str: str) -> str:
    """规范化中文作者名：用顿号分隔（避免 \\and 在 twocolumn[] 中冲突）"""
    parts = re.split(r'[,，;；]+', author_str)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        return author_str.strip()
    return "、".join(parts)


# ============================================================
# Pass 3: 骨架组装
# ============================================================

def _clean_title(title: str) -> str:
    """清理标题中的多余空格"""
    return title.strip()


def assemble_paper(blocks: List[Tuple[str, str]], title: str, author: str,
                   date: str, abstract: str, keywords: str,
                   dark: bool, twocolumn: bool, nomath: bool = False) -> str:
    """组装 harryopo-paper .tex"""
    docopts = []
    if twocolumn:
        docopts.append("twocolumn")
    if dark:
        docopts.append("dark")
    if nomath:
        docopts.append("nomath")
    optstr = ",".join(docopts)

    lines = []
    lines.append(r"\documentclass[" + optstr + r"]{harryopo-paper}" if optstr else r"\documentclass{harryopo-paper}")
    lines.append("")
    lines.append(r"\title{" + _clean_title(title) + "}")
    lines.append(r"\author{" + format_author(author) + "}")
    lines.append(r"\date{" + date + "}")
    lines.append("")
    if twocolumn:
        lines.append(r"\abstractcontent{" + abstract + "}")
        lines.append(r"\keywordscontent{" + keywords + "}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append("")

    if twocolumn:
        lines.append(r"\maketitlewithabstract")
    else:
        lines.append(r"\maketitle")
        if abstract:
            lines.append(r"\begin{abstract}")
            lines.append(abstract)
            lines.append(r"\end{abstract}")
        if keywords:
            lines.append(r"\keywords{" + keywords + "}")
        lines.append("")

    bib_lines: List[str] = []
    first_h1 = True
    # 支持 harryopo MD 约定的 `**摘要：**` 加粗前缀
    meta_re = re.compile(r'^\*{0,2}(作者|摘要|关键词)\*{0,2}[：:]')
    keywords_in_text_re = re.compile(r'(?m)^\*{0,2}关键词[：:].+$')
    pending_caption: Optional[str] = None

    for i, (btype, content) in enumerate(blocks):
        if btype == BLOCK_BIB:
            for bib in content.strip().split('\n'):
                bib = bib.strip()
                if bib:
                    bib_lines.append(bib)
            continue
        if btype == BLOCK_H1:
            if first_h1:
                first_h1 = False
                continue  # 标题已在 \title{} 中
            # # → \section*（隐藏自动编号 0.1/0.2/...）
            lines.append(r"\section*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{section}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_TEXT and meta_re.match(content):
            continue  # 跳过作者/摘要/关键词元数据行
        elif btype == BLOCK_TEXT and keywords_in_text_re.search(content):
            # 段落中嵌入 "关键词：..." → 删除该行（已在 \keywords{} 中）
            cleaned = keywords_in_text_re.sub('', content).strip()
            if cleaned:
                lines.append(parse_inline(cleaned))
                lines.append("")
            continue
        elif btype == BLOCK_H2:
            # ## → \subsection*（映射到 paper.cls 的 subsection 层级：黑体）
            lines.append(r"\subsection*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{subsection}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_H3:
            # ### → \subsubsection*（映射到 paper.cls 的 subsubsection 层级：楷体）
            lines.append(r"\subsubsection*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{subsubsection}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_H4:
            # #### → \paragraph*（黑体行内标题，对应公文四级 ①）
            lines.append(r"\paragraph*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{paragraph}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_TEXT:
            # 表格标题：`表N：xxx` 独立成段且下一块是表格 → 暂存为 caption
            cap_m = re.match(r'^(表\s*\d+\s*[：:].+)$', content.strip(), re.DOTALL)
            if cap_m and i + 1 < len(blocks) and blocks[i + 1][0] == BLOCK_TABLE:
                pending_caption = content.strip()
                continue
            lines.append(parse_inline(content))
            lines.append("")
        elif btype == BLOCK_UL:
            lines.append(r"\begin{itemize}")
            for item in content.strip().split('\n'):
                if item.strip():
                    lines.append(r"  \item " + parse_inline(item.strip()))
            lines.append(r"\end{itemize}")
            lines.append("")
        elif btype == BLOCK_OL:
            lines.append(r"\begin{enumerate}")
            for item in content.strip().split('\n'):
                if item.strip():
                    lines.append(r"  \item " + parse_inline(item.strip()))
            lines.append(r"\end{enumerate}")
            lines.append("")
        elif btype == BLOCK_QUOTE:
            lines.append(r"\begin{quote}")
            lines.append(parse_inline(content))
            lines.append(r"\end{quote}")
            lines.append("")
        elif btype == BLOCK_CODE:
            parts = content.split('\n', 1)
            lang = parts[0].strip()
            code = parts[1] if len(parts) > 1 else ""
            style = LANG_MAP.get(lang, "plainstyle")
            # 转义 LaTeX 特殊字符
            code_escaped = code.replace("\\", r"\textbackslash{}")
            code_escaped = code_escaped.replace("{", r"\{").replace("}", r"\}")
            code_escaped = code_escaped.replace("_", r"\_")
            code_escaped = code_escaped.replace("&", r"\&")
            code_escaped = code_escaped.replace("%", r"\%")
            code_escaped = code_escaped.replace("$", r"\$")
            code_escaped = code_escaped.replace("#", r"\#")
            code_escaped = code_escaped.replace("^", r"\^{}")
            code_escaped = code_escaped.replace("~", r"\textasciitilde{}")
            if style == "pystyle":
                lines.append(f"\\begin{{lstlisting}}[style=pystyle,caption={{}}]")
            else:
                lines.append(f"\\begin{{lstlisting}}[style={style},caption={{}}]")
            lines.append(code)
            lines.append(r"\end{lstlisting}")
            lines.append("")
        elif btype == BLOCK_MATH_DISPLAY:
            lines.append(r"\begin{equation}")
            lines.append(content)
            lines.append(r"\end{equation}")
            lines.append("")
        elif btype == BLOCK_TABLE:
            lines.extend(_parse_table_to_latex(content, pending_caption))
            pending_caption = None
        elif btype == BLOCK_RAW_LATEX:
            # MinerU 清洗后的 LaTeX 代码（longtable/tabular 等）直接透传
            lines.append(content)
            lines.append("")
        elif btype == BLOCK_FIGURE:
            parts = content.split('\n', 1)
            alt = parts[0].strip()
            src = parts[1].strip() if len(parts) > 1 else ""
            # caption 放在 \includegraphics 之后（图下方）
            lines.append(r"\begin{figure}[htbp]")
            lines.append(r"  \centering")
            lines.append(r"  \includegraphics[width=0.85\textwidth]{" + src + "}")
            if alt:
                lines.append(r"  \caption{" + alt + "}")
            lines.append(r"\end{figure}")
            lines.append("")
        elif btype == BLOCK_HR:
            lines.append(r"\medskip\hrule\medskip")
            lines.append("")

    # 参考文献
    if bib_lines:
        lines.append(r"\begin{thebibliography}{99}")
        for i, bib in enumerate(bib_lines, 1):
            lines.append(r"\bibitem{ref" + str(i) + "} " + bib)
        lines.append(r"\end{thebibliography}")
        lines.append("")

    lines.append(r"\end{document}")
    return "\n".join(lines)


def _parse_table_to_latex(raw: str, caption: str = "") -> List[str]:
    """将 Markdown 表格转为 booktabs 三线表（tabularx 自适应宽度 + 标题在表格下方）"""
    rows = raw.strip().split('\n')
    if len(rows) < 2:
        return [r"% empty table"]

    header = rows[0]
    cols = [c.strip() for c in header.split('|')[1:-1]]
    ncols = len(cols)
    if ncols == 0:
        return [r"% empty table"]

    # 对齐方式
    aligns = []
    if len(rows) > 1 and '|' in rows[1]:
        align_row = rows[1]
        align_cells = [c.strip() for c in align_row.split('|')[1:-1]]
        for ac in align_cells:
            if ac.startswith(':') and ac.endswith(':'):
                aligns.append('c')
            elif ac.endswith(':'):
                aligns.append('r')
            else:
                aligns.append('l')
        if len(aligns) < ncols:
            aligns = ['l'] * ncols
    else:
        aligns = ['l'] * ncols

    # 用 tabularx 列说明：每列 X，并加 >{\raggedright\arraybackslash} 避免过宽
    col_spec = ' '.join('>{\\raggedright\\arraybackslash}X' for _ in range(ncols))
    data_rows = rows[2:] if len(rows) > 2 else []

    # 转义表头/单元格（防止 &、% 等被误解）
    def _esc(cell: str) -> str:
        out = cell
        out = out.replace("\\", r"\textbackslash{}")
        out = out.replace("{", r"\{").replace("}", r"\}")
        out = out.replace("_", r"\_")
        out = out.replace("&", r"\&")
        out = out.replace("%", r"\%")
        out = out.replace("$", r"\$")
        out = out.replace("#", r"\#")
        out = out.replace("^", r"\^{}")
        out = out.replace("~", r"\textasciitilde{}")
        return out

    header_cells = [_esc(c) for c in cols]
    # 第一列加黑体作为表头（中文用黑体 {\fzht ...} 分组调用而非 \textbf，避免笔画糊）
    header_line = " & ".join(r"{\fzht " + h + "}" for h in header_cells) + r" \\"

    # 表格单元格内的行内格式解析（加粗→黑体、斜体保留）
    # 注意：必须在 _esc 之后执行，因为 _esc 不转义 *，所以顺序安全
    def _cell_inline(s: str) -> str:
        s = re.sub(r'\*\*\*(.+?)\*\*\*', r'{\\fzht \1}', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'{\\fzht \1}', s)
        s = re.sub(r'\*(.+?)\*', r'\\textit{\1}', s)
        return s

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"  \centering")
    lines.append(r"  \small")
    lines.append(r"  \begin{tabularx}{\textwidth}{" + col_spec + r"}")
    lines.append(r"    \toprule")
    lines.append("    " + header_line)
    lines.append(r"    \midrule")
    for row in data_rows:
        cells = [c.strip() for c in row.split('|')[1:-1]]
        while len(cells) < ncols:
            cells.append("")
        cells = cells[:ncols]
        cells = [_cell_inline(_esc(c)) for c in cells]
        lines.append("    " + " & ".join(cells) + r" \\")
    lines.append(r"    \bottomrule")
    lines.append(r"  \end{tabularx}")
    if caption:
        lines.append(r"  \caption{" + caption + "}")
    lines.append(r"\end{table}")
    lines.append("")
    return lines


def assemble_report(blocks: List[Tuple[str, str]], title: str, author: str,
                    date: str, subtitle: str, institute: str,
                    abstract: str, dark: bool, nomath: bool = False) -> str:
    """组装 harryopo-report .tex"""
    docopts = []
    if dark:
        docopts.append("dark")
    if nomath:
        docopts.append("nomath")
    optstr = ",".join(docopts)

    lines = []
    lines.append(r"\documentclass[" + optstr + r"]{harryopo-report}" if optstr else r"\documentclass{harryopo-report}")
    lines.append("")
    lines.append(r"\title{" + _clean_title(title) + "}")
    if subtitle:
        lines.append(r"\subtitle{" + subtitle + "}")
    lines.append(r"\author{" + format_author(author) + "}")
    if institute:
        lines.append(r"\institute{" + institute + "}")
    lines.append(r"\date{" + date + "}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append("")
    lines.append(r"\maketitle")
    lines.append("")

    if abstract:
        lines.append(r"\begin{abstract}")
        lines.append(parse_inline(abstract))
        lines.append(r"\end{abstract}")
        lines.append("")

    lines.append(r"\tableofcontents")
    lines.append("")

    bib_lines: List[str] = []
    in_intro = True
    first_h1 = True
    # 支持 harryopo MD 约定的 `**摘要：**` 加粗前缀
    meta_re = re.compile(r'^\*{0,2}(作者|摘要|关键词)\*{0,2}[：:]')
    pending_caption: Optional[str] = None

    for i, (btype, content) in enumerate(blocks):
        if btype == BLOCK_BIB:
            for bib in content.strip().split('\n'):
                bib = bib.strip()
                if bib:
                    bib_lines.append(bib)
            continue
        if btype == BLOCK_H1:
            in_intro = False
            if first_h1:
                first_h1 = False
                continue  # 标题已在 \title{} 中
            # # → \chapter*（隐藏自动编号 0.1/0.2/...）
            lines.append(r"\chapter*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{chapter}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_TEXT and meta_re.match(content):
            continue  # 跳过作者/摘要/关键词元数据行
        elif btype == BLOCK_H2:
            in_intro = False
            # ## → \section*（隐藏自动编号）
            lines.append(r"\section*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{section}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_H3:
            in_intro = False
            # ### → \subsection*
            lines.append(r"\subsection*{" + _clean_title(content) + "}")
            lines.append(r"\addcontentsline{toc}{subsection}{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_H4:
            in_intro = False
            lines.append(r"\subhead{" + _clean_title(content) + "}")
            lines.append("")
        elif btype == BLOCK_TEXT:
            # 表格标题：`表N：xxx` 独立成段且下一块是表格 → 暂存为 caption
            cap_m = re.match(r'^(表\s*\d+\s*[：:].+)$', content.strip(), re.DOTALL)
            if cap_m and i + 1 < len(blocks) and blocks[i + 1][0] == BLOCK_TABLE:
                pending_caption = content.strip()
                continue
            lines.append(parse_inline(content))
            lines.append("")
        elif btype == BLOCK_UL:
            lines.append(r"\begin{itemize}")
            for item in content.strip().split('\n'):
                if item.strip():
                    lines.append(r"  \item " + parse_inline(item.strip()))
            lines.append(r"\end{itemize}")
            lines.append("")
        elif btype == BLOCK_OL:
            lines.append(r"\begin{enumerate}")
            for item in content.strip().split('\n'):
                if item.strip():
                    lines.append(r"  \item " + parse_inline(item.strip()))
            lines.append(r"\end{enumerate}")
            lines.append("")
        elif btype == BLOCK_QUOTE:
            lines.append(r"\begin{quote}")
            lines.append(parse_inline(content))
            lines.append(r"\end{quote}")
            lines.append("")
        elif btype == BLOCK_CODE:
            parts = content.split('\n', 1)
            lang = parts[0].strip()
            code = parts[1] if len(parts) > 1 else ""
            style = LANG_MAP.get(lang, "plainstyle")
            code_escaped = code.replace("\\", r"\textbackslash{}")
            code_escaped = code_escaped.replace("{", r"\{").replace("}", r"\}")
            code_escaped = code_escaped.replace("_", r"\_")
            code_escaped = code_escaped.replace("&", r"\&")
            code_escaped = code_escaped.replace("%", r"\%")
            code_escaped = code_escaped.replace("$", r"\$")
            code_escaped = code_escaped.replace("#", r"\#")
            code_escaped = code_escaped.replace("^", r"\^{}")
            code_escaped = code_escaped.replace("~", r"\textasciitilde{}")
            if style == "pystyle":
                lines.append(f"\\begin{{lstlisting}}[style=pystyle,caption={{}}]")
            else:
                lines.append(f"\\begin{{lstlisting}}[style={style},caption={{}}]")
            lines.append(code)
            lines.append(r"\end{lstlisting}")
            lines.append("")
        elif btype == BLOCK_MATH_DISPLAY:
            lines.append(r"\begin{equation}")
            lines.append(content)
            lines.append(r"\end{equation}")
            lines.append("")
        elif btype == BLOCK_TABLE:
            lines.extend(_parse_table_to_latex(content, pending_caption))
            pending_caption = None
        elif btype == BLOCK_RAW_LATEX:
            lines.append(content)
            lines.append("")
        elif btype == BLOCK_FIGURE:
            parts = content.split('\n', 1)
            alt = parts[0].strip()
            src = parts[1].strip() if len(parts) > 1 else ""
            # caption 放在 \includegraphics 之后（图下方）
            lines.append(r"\begin{figure}[htbp]")
            lines.append(r"  \centering")
            lines.append(r"  \includegraphics[width=0.85\textwidth]{" + src + "}")
            if alt:
                lines.append(r"  \caption{" + alt + "}")
            lines.append(r"\end{figure}")
            lines.append("")
        elif btype == BLOCK_HR:
            lines.append(r"\medskip\hrule\medskip")
            lines.append("")

    if bib_lines:
        lines.append(r"\begin{thebibliography}{99}")
        for i, bib in enumerate(bib_lines, 1):
            lines.append(r"\bibitem{ref" + str(i) + "} " + bib)
        lines.append(r"\end{thebibliography}")
        lines.append("")

    lines.append(r"\end{document}")
    return "\n".join(lines)


# ============================================================
# DOCX 转换（备选，依赖外部工具）
# ============================================================

def convert_docx_via_pandoc(docx_path: str, md_path: str) -> bool:
    """使用 pandoc CLI 将 DOCX → Markdown"""
    try:
        subprocess.run(
            ["pandoc", docx_path, "-f", "docx", "-t", "markdown", "-o", md_path],
            check=True, capture_output=True, text=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_docx_via_python(docx_path: str) -> Optional[str]:
    """使用 python-docx 提取文本"""
    try:
        import docx
    except ImportError:
        return None

    doc = docx.Document(docx_path)
    markdown_lines = []
    for para in doc.paragraphs:
        style = para.style.name if para.style else ""
        text = para.text.strip()
        if not text:
            markdown_lines.append("")
            continue
        if "Heading 1" in style or style == "Heading 1":
            markdown_lines.append(f"# {text}")
        elif "Heading 2" in style or style == "Heading 2":
            markdown_lines.append(f"## {text}")
        elif "Heading 3" in style or style == "Heading 3":
            markdown_lines.append(f"### {text}")
        elif "Heading 4" in style or style == "Heading 4":
            markdown_lines.append(f"#### {text}")
        else:
            # 处理 run 级别的粗体/斜体（DOCX 加粗转 MD ** 后由 parse_inline 统一转 \fzht 黑体）
            runs_latex = []
            for run in para.runs:
                t = run.text
                if run.bold and run.italic:
                    t = f"**{t}**"  # 粗斜体统一走加粗分支（中文无斜体概念）
                elif run.bold:
                    t = f"**{t}**"
                elif run.italic:
                    t = f"*{t}*"
                runs_latex.append(t)
            markdown_lines.append(" ".join(runs_latex))

    return "\n\n".join(markdown_lines)


# ============================================================
# 主编排函数
# ============================================================

def convert_md_to_tex(
    md_path: str,
    tex_path: str,
    doc_type: str,
    title: str = "",
    author: str = "",
    date: str = "",
    subtitle: str = "",
    institute: str = "",
    abstract: str = "",
    keywords: str = "",
    dark: bool = False,
    twocolumn: bool = False,
    nomath: bool = False,
) -> str:
    """主编排：MD → LaTeX .tex"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 尝试从源文件提取元数据（标题/摘要/关键词）
    if not title:
        m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
    author_src = None  # 记录"标题后第一段式"作者原文，用于从正文中剔除
    if not author:
        m = re.search(r'(?i)^作者[：:]\s*(.+)$', text, re.MULTILINE)
        if m:
            author = m.group(1).strip()
        else:
            # 回退：标题(# 标题)后的第一段作为作者（如 `张三 计算机学院 2025000101`）
            m2 = re.search(r'^#\s+.+?\n+(.+?)$', text, re.MULTILINE)
            if m2:
                candidate = m2.group(1).strip()
                # 排除标题后直接是摘要/加粗内容/过长段落的情况
                if (candidate and not candidate.startswith('**')
                        and not re.match(r'^(摘要|关键词|作者)', candidate)
                        and len(candidate) < 60):
                    author = candidate
                    author_src = candidate
    if author_src:
        # 从 text 中删除作者行（保留标题行），避免其与摘要段粘连成一个 BLOCK_TEXT
        # \n[ \t\n]* 需要跨过标题与作者之间的空行（仅一个 \n 不够）
        text = re.sub(r'(^#\s+.+?)\n[ \t\n]*' + re.escape(author_src) + r'[ \t]*\n',
                      r'\1\n', text, flags=re.MULTILINE)
    # 摘要/关键词支持 harryopo MD 约定的 `**摘要：**` 加粗前缀
    if not abstract:
        m = re.search(r'(?ims)^\*{0,2}摘要[：:]?\*{0,2}\s*\n?(.+?)(?=\n(?:\*{0,2}关键词[：:]|#|##))', text)
        if m:
            abstract = m.group(1).strip()
    if not keywords:
        m = re.search(r'(?im)^\*{0,2}关键词[：:]\*{0,2}\s*(.+)$', text, re.MULTILINE)
        if m:
            keywords = m.group(1).strip()

    blocks = split_blocks(text)

    if doc_type in ("report", "报告"):
        tex = assemble_report(blocks, title, author, date,
                             subtitle, institute, abstract, dark, nomath)
    else:
        tex = assemble_paper(blocks, title, author, date,
                            abstract, keywords, dark, twocolumn, nomath)

    out_dir = os.path.dirname(tex_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)

    return tex_path


def convert_docx_to_tex(
    docx_path: str,
    tex_path: str,
    doc_type: str,
    title: str = "",
    author: str = "",
    date: str = "",
    subtitle: str = "",
    institute: str = "",
    abstract: str = "",
    keywords: str = "",
    dark: bool = False,
    twocolumn: bool = False,
    nomath: bool = False,
) -> Optional[str]:
    """DOCX → Markdown → LaTeX"""
    md_path = docx_path.rsplit(".", 1)[0] + "_converted.md"

    # 方案 1：python-docx
    md_text = convert_docx_via_python(docx_path)
    if md_text is None:
        # 方案 2：pandoc
        ok = convert_docx_via_pandoc(docx_path, md_path)
        if not ok:
            print("[ERROR] 无法转换 DOCX。请安装 pandoc 或 python-docx。", file=sys.stderr)
            print("  pip install python-docx", file=sys.stderr)
            print("  或下载 pandoc: https://pandoc.org", file=sys.stderr)
            return None
    else:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

    return convert_md_to_tex(md_path, tex_path, doc_type, title, author, date,
                             subtitle, institute, abstract, keywords, dark, twocolumn, nomath)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="harryopo-convert — MD/DOCX → LaTeX (.tex) 转换引擎",
        epilog="示例: python convert.py report.md --type paper --twocolumn"
    )
    parser.add_argument("input", help="输入文件路径 (.md / .docx)")
    parser.add_argument("--type", choices=["paper", "report"], default="paper",
                        help="目标文档类型（默认 paper）")
    parser.add_argument("--title", default="", help="文档标题")
    parser.add_argument("--author", default="", help="作者（多作者用逗号分隔）")
    parser.add_argument("--date", default="", help="日期（默认今天）")
    parser.add_argument("--subtitle", default="", help="副标题（仅 report）")
    parser.add_argument("--institute", default="", help="机构（仅 report）")
    parser.add_argument("--abstract", default="", help="摘要内容（覆盖自动提取）")
    parser.add_argument("--keywords", default="", help="关键词（覆盖自动提取）")
    parser.add_argument("--dark", action="store_true", help="深紫主题")
    parser.add_argument("--twocolumn", action="store_true", help="双栏（仅 paper）")
    parser.add_argument("--no-math", action="store_true", dest="nomath",
                        help="禁用 unicode-math（无数学文档/读书笔记用）")
    parser.add_argument("--output", "-o", default="", help="输出 .tex 路径")
    args = parser.parse_args()

    if not args.date:
        from datetime import date as dt
        args.date = dt.today().strftime("%Y年%m月%d日")

    # 输出路径
    input_path = args.input
    ext = os.path.splitext(input_path)[1].lower()
    base = os.path.splitext(os.path.basename(input_path))[0]

    if args.output:
        tex_path = args.output
    else:
        # 放入同 skill 的 templates/ 对应目录
        skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_dir = os.path.join(skill_root, "templates",
                              "paper" if args.type == "paper" else "report")
        tex_path = os.path.join(out_dir, f"{base}.tex")

    print(f"[INFO] Input:  {input_path}")
    print(f"[INFO] Output: {tex_path}")
    print(f"[INFO] Type:   {args.type}")
    print(f"[INFO] Title:  {args.title or '(auto)'}")
    print(f"[INFO] Author: {args.author or '(auto)'}")
    print(f"[INFO] Date:   {args.date}")

    if ext == ".md":
        convert_md_to_tex(
            input_path, tex_path, args.type,
            args.title, args.author, args.date,
            args.subtitle, args.institute,
            args.abstract, args.keywords,
            args.dark, args.twocolumn, args.nomath
        )
    elif ext in (".docx", ".doc"):
        result = convert_docx_to_tex(
            input_path, tex_path, args.type,
            args.title, args.author, args.date,
            args.subtitle, args.institute,
            args.abstract, args.keywords,
            args.dark, args.twocolumn, args.nomath
        )
        if result is None:
            sys.exit(1)
    else:
        print(f"[ERROR] Unsupported file type: {ext}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] Generated: {tex_path}")


if __name__ == "__main__":
    main()
