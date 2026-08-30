#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tex2md.py — LaTeX → Markdown 中间态转换（harryopo 反向链路）

方案书 v2 §4：LaTeX → Word 统一走 MD 中间态（.tex → MD 清洗 → md_to_word 渲染）。

处理 harryopo convert.py 生成的 .tex 全部结构：
  - \\title/\\author/\\date 元数据  → # 主标题
  - \\section/\\subsection/\\subsubsection → # / ## / ###
  - {\\fzht ...}（黑体分组语法）   → **...**（md_to_word 会把 ** 还原为黑体，闭环）
  - \\begin{quote} 注释块           → > 注：/ > **表N：**/ > 式(N)：
  - \\begin{figure}                 → ![caption](path)（图片路径转绝对路径）
  - \\begin{tabularx}/tabular       → GFM 表格（| 分隔 + 分隔行）
  - \\begin{equation}               → $$ ... $$（LaTeX 公式原样，md_to_word 转 OMML）
  - \\begin{thebibliography}        → ## 参考文献 + [N] 条目

用法:
    python tex2md.py input.tex -o output.md
    python tex2md.py input.tex            # 默认输出到同目录同名 .md
"""

import argparse
import re
import sys
from pathlib import Path

# ============================================================
# 行内清洗
# ============================================================

# 行内 LaTeX 转义 → MD 字符
_INLINE_ESCAPES = [
    (r'\%', '%'),
    (r'\&', '&'),
    (r'\_', '_'),
    (r'\#', '#'),
    (r'~', ' '),      # 不换行空格 → 普通空格
    (r'---', '—'),    # 破折号
    (r'--', '–'),
]


def _strip_braced_cmd(text: str, opener: str, wrap=None) -> str:
    """按平衡花括号替换单个 LaTeX 格式命令（支持任意嵌套）。

    Args:
        opener: 命令起始串，如 '\\textbf{' 或 '{\\fzht'
        wrap: 替换包裹符 ('**','**')；None 表示仅提取纯文本（表格模式）
    """
    result = []
    i = 0
    is_group = opener.startswith('{')  # {\fzht ...} 分组形式
    while i < len(text):
        idx = text.find(opener, i)
        if idx == -1:
            result.append(text[i:])
            break
        result.append(text[i:idx])
        j = idx + len(opener)
        depth, k = 1, j
        while k < len(text) and depth > 0:
            if text[k] == '{':
                depth += 1
            elif text[k] == '}':
                depth -= 1
            k += 1
        if depth == 0:
            inner = text[j:k - 1]
            if is_group:
                inner = inner.strip()
            if wrap:
                result.append(wrap[0] + inner + wrap[1])
            else:
                result.append(inner)
            i = k
        else:
            # 花括号未闭合：保留原文继续扫描，不破坏结构
            result.append(text[idx])
            i = idx + 1
    return ''.join(result)


def _replace_format_cmds(text: str, table_mode: bool) -> str:
    """黑体/加粗/斜体命令 → MD 标记（迭代至不动点，嵌套内容逐层展开）"""
    while True:
        new = _strip_braced_cmd(text, '{\\fzht',
                                None if table_mode else ('**', '**'))
        new = _strip_braced_cmd(new, '\\textbf{',
                                None if table_mode else ('**', '**'))
        new = _strip_braced_cmd(new, '\\textit{',
                                None if table_mode else ('*', '*'))
        new = _strip_braced_cmd(new, '\\emph{',
                                None if table_mode else ('*', '*'))
        if new == text:
            return new
        text = new


def clean_inline(text: str, table_mode: bool = False) -> str:
    """行内 LaTeX → MD：去自定义宏、转义、保留数学

    table_mode: 表格单元格模式。Word 表格字体由模板样式控制，
                黑体分组 {\fzht X} 只提取纯文本，不转 **（否则星号原样显示）。
    """
    text = _replace_format_cmds(text, table_mode)
    # 5. 转义字符
    for pat, rep in _INLINE_ESCAPES:
        text = text.replace(pat, rep)
    # 6. 行内数学 $...$ 原样保留（md_to_word 不做行内 OMML，降级为文本）
    return text.strip()


# ============================================================
# 表格解析
# ============================================================

def parse_table_body(lines: list, start: int) -> tuple:
    """解析 tabular/tabularx 表格体，返回 (md_lines, next_idx, caption)。

    harryopo 表格结构：
        \\begin{tabularx}{\\textwidth}{>{\\raggedright\\arraybackslash}X ...}
          \\toprule
          表头 & 表头 & ... \\\\
          \\midrule
          数据 & 数据 & ... \\\\
          \\bottomrule
        \\end{tabularx}

    caption: 表格内的 \\caption{...} 标题（无则为 None；空 \\caption{} 丢弃）。
    """
    rows = []          # 收集原始数据行 [[cell, cell, ...]]
    caption = None     # \caption{...} 标题
    i = start
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if line.startswith('\\end{tabular'):
            break
        if line.startswith('\\begin{tabular'):
            # 列定义行：\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X ...}
            i += 1
            continue
        if line.startswith('\\caption'):
            # 表格内标题（harryopo 常放空 \caption{} 占位，须丢弃防残留）
            m = re.search(r'\\caption\{([^{}]*)\}', line)
            if m and m.group(1).strip():
                caption = clean_inline(m.group(1))
            i += 1
            continue
        if line.startswith('\\toprule') or line.startswith('\\bottomrule'):
            i += 1
            continue
        if line.startswith('\\midrule'):
            i += 1
            continue
        if line.startswith('%') or not line:
            i += 1
            continue
        # 数据行：a & b & c \\  （可能行尾换行）
        buf = line
        while buf.count('&') == 0 and not buf.endswith('\\\\') and '\\\\' not in buf:
            i += 1
            if i >= n:
                break
            buf += ' ' + lines[i].strip()
        cells = [clean_inline(c, table_mode=True) for c in buf.replace('\\\\', '').split('&')]
        rows.append(cells)
        i += 1

    md_lines = []
    for idx, cells in enumerate(rows):
        cells = [c.replace('|', '\\|') for c in cells]  # 防 GFM 竖线冲突
        md_lines.append('| ' + ' | '.join(cells) + ' |')
        if idx == 0:
            # 表头分隔行（列数与表头一致）
            md_lines.append('|' + '---|' * len(cells))
    return md_lines, i + 1, caption  # 跳过 \end{tabular...}


# ============================================================
# 主转换
# ============================================================

# 元数据
_TITLE_RE = re.compile(r'\\title\{([^{}]*)\}')
_AUTHOR_RE = re.compile(r'\\author\{([^{}]*)\}')
_DATE_RE = re.compile(r'\\date\{([^{}]*)\}')

# 章节映射（harryopo MD 约定：# 主标题 / ## 一级 / ### 二级）
_SECTION_MAP = [
    (r'\\chapter\*?\{([^{}]*)\}', '# '),
    (r'\\section\*?\{([^{}]*)\}', '# '),
    (r'\\subsection\*?\{([^{}]*)\}', '## '),
    (r'\\subsubsection\*?\{([^{}]*)\}', '### '),
]

# 引用/表格/公式/图片 caption 等 quote 内容 → > 注释
_QUOTE_PREFIX_HINTS = ('注', '表', '式', '图', '副标题', '作者')

# 参考文献条目
_BIBITEM_RE = re.compile(r'\\bibitem\{[^}]*\}\s*(.*)')


def tex_to_md(tex_path: str) -> str:
    """LaTeX 源文件 → Markdown 中间态文本"""
    tex = Path(tex_path)
    text = tex.read_text(encoding='utf-8')
    tex_dir = tex.parent.resolve()

    # ---- 元数据 ----
    title_m = _TITLE_RE.search(text)
    title = title_m.group(1).strip() if title_m else ''

    # ---- 截取正文（\begin{document} 之后）----
    doc_m = re.search(r'\\begin\{document\}(.*)\\end\{document\}', text, re.DOTALL)
    body = doc_m.group(1) if doc_m else text

    out = []
    if title:
        out.append(f'# {title}')
        out.append('')

    lines = body.split('\n')
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        stripped = line

        # ---- 环境开始 ----
        if stripped.startswith('\\begin{quote}'):
            # quote 块 → > 注释（合并内部多行）
            inner = []
            i += 1
            while i < n and not lines[i].strip().startswith('\\end{quote}'):
                inner.append(clean_inline(lines[i]))
                i += 1
            i += 1  # 跳过 \end{quote}
            if inner:
                for seg in inner:
                    if seg:
                        out.append(f'> {seg}')
                out.append('')
            continue

        if stripped.startswith('\\begin{figure}'):
            # figure 块 → ![caption](path)
            path, caption = '', ''
            i += 1
            while i < n and not lines[i].strip().startswith('\\end{figure}'):
                s = lines[i].strip()
                m = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}', s)
                if m:
                    path = m.group(1).strip()
                m = re.search(r'\\caption\{([^{}]*)\}', s)
                if m:
                    caption = clean_inline(m.group(1))
                i += 1
            i += 1  # 跳过 \end{figure}
            if path:
                # 图片路径转绝对路径（md_to_word 优先用存在的绝对路径）
                img = Path(path)
                if not img.is_absolute():
                    img = tex_dir / img
                out.append(f'![{caption or "图"}]({img.as_posix()})')
                out.append('')
            continue

        if stripped.startswith('\\begin{table'):
            # table 浮动体：跳过 \centering/\small，找到 tabular 表格体；
            # 表格后的 \caption{}（常为空占位）/ \label 等残留须一并消费，
            # 否则会作为裸文本残留到中间态。
            i += 1
            caption_block = None
            while i < n and not lines[i].strip().startswith('\\end{table'):
                s = lines[i].strip()
                if s.startswith('\\begin{tabular'):
                    table_lines, i, cap = parse_table_body(lines, i)
                    if cap:
                        caption_block = cap
                    if table_lines:
                        out.extend(table_lines)
                        out.append('')
                    continue  # 继续消费到 \end{table}
                if s.startswith('\\caption'):
                    m = re.search(r'\\caption\{([^{}]*)\}', s)
                    if m and m.group(1).strip():
                        caption_block = clean_inline(m.group(1))
                    i += 1
                    continue
                if s.startswith('\\label'):
                    i += 1
                    continue
                if s.startswith('\\end{'):
                    break
                i += 1
            i += 1  # 跳过 \end{table}
            if caption_block:
                out.append(f'> **{caption_block}**')
                out.append('')
            continue

        if stripped.startswith('\\begin{tabular') or stripped.startswith('\\begin{longtable'):
            # 表格体 → GFM 表格
            table_lines, i, caption = parse_table_body(lines, i)
            if table_lines:
                out.extend(table_lines)
                out.append('')
            if caption:
                out.append(f'> **{caption}**')
                out.append('')
            continue

        if stripped.startswith('\\begin{equation') or stripped.startswith('\\begin{align'):
            # 公式块 → $$ ... $$（合并多行，去掉 \label 等）
            env = 'equation' if 'equation' in stripped else 'align'
            formula = []
            i += 1
            while i < n and not lines[i].strip().startswith(f'\\end{{{env}'):
                s = lines[i].strip()
                if s and not s.startswith('\\label'):
                    formula.append(s)
                i += 1
            i += 1  # 跳过 \end{...}
            latex = ' '.join(formula)
            # 去掉 align 的换行标记
            latex = latex.replace('\\\\', ' ').replace('&', ' ')
            out.append(f'$$ {latex} $$')
            out.append('')
            continue

        if stripped.startswith('\\begin{thebibliography}'):
            # 参考文献区 → ## 参考文献 + [N] 条目
            out.append('## 参考文献')
            out.append('')
            i += 1
            while i < n and not lines[i].strip().startswith('\\end{thebibliography}'):
                s = lines[i].strip()
                m = _BIBITEM_RE.match(s)
                if m and m.group(1).strip():
                    out.append(clean_inline(m.group(1)))
                i += 1
            i += 1
            out.append('')
            continue

        # ---- 环境结束 / 控制命令 ----
        if stripped.startswith('\\end{'):
            i += 1
            continue
        if stripped in ('\\maketitle', '\\centering', '\\small', '\\noindent', '\\newpage', '\\clearpage'):
            i += 1
            continue
        if stripped.startswith('\\addcontentsline'):
            i += 1
            continue
        if stripped.startswith('\\label'):
            i += 1
            continue

        # ---- 章节标题 ----
        section_match = None
        for pat, prefix in _SECTION_MAP:
            m = re.match(pat, stripped)
            if m:
                section_match = prefix + clean_inline(m.group(1))
                break
        if section_match:
            out.append(section_match)
            out.append('')
            i += 1
            continue

        # ---- 普通正文行 ----
        if stripped.startswith('\\begin{'):
            # 其它环境（itemize/enumerate/abstract 等）简化为正文
            i += 1
            while i < n and not lines[i].strip().startswith('\\end{'):
                s = clean_inline(lines[i])
                if s:
                    out.append(s)
                i += 1
            i += 1
            out.append('')
            continue
        if stripped.startswith('\\item'):
            # 列表项 → 统一转 - 无序列表（md_to_word 按段落处理）
            out.append('- ' + clean_inline(stripped[5:]))
            i += 1
            continue

        cleaned = clean_inline(stripped)
        if cleaned:
            out.append(cleaned)
        i += 1

    # 去除连续空行（最多保留 1 个）
    result = []
    prev_blank = False
    for line in out:
        blank = not line.strip()
        if blank and prev_blank:
            continue
        result.append(line)
        prev_blank = blank

    return '\n'.join(result).strip() + '\n'


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='LaTeX → Markdown 中间态（harryopo 反向链路，供 md_to_word 渲染）')
    parser.add_argument('input', help='输入 .tex 文件')
    parser.add_argument('-o', '--output', help='输出 .md 路径（默认同目录同名）')
    args = parser.parse_args()

    tex_path = Path(args.input)
    if not tex_path.exists():
        print(f'[ERROR] 输入文件不存在：{tex_path}', file=sys.stderr)
        sys.exit(1)

    md_text = tex_to_md(str(tex_path))
    out_path = Path(args.output) if args.output else tex_path.with_suffix('.md')
    out_path.write_text(md_text, encoding='utf-8')
    print(f'[OK] {out_path} ({len(md_text)} chars)')


if __name__ == '__main__':
    main()
