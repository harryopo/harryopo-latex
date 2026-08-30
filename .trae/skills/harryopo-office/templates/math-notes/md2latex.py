#!/usr/bin/env python3
# ============================================================
#  harryopo-mathnotes  MD -> LaTeX Converter
#  Pure Python, no external dependencies
#  Features:
#    - Headings (#/##/###) -> \section/\subsection/\subsubsection
#    - Bold (**text**) -> \textbf{text}
#    - Italic (*text*) -> \emph{text}
#    - Inline code (`code`) -> \texttt{code}
#    - Code blocks (```) -> \begin{verbatim}...\end{verbatim}
#    - Tables -> tabularx with auto-wrapping
#    - Math ($...$, $$...$$) preserved as-is
#    - Lists (ordered/unordered) -> enumerate/itemize
#    - Blockquotes (>) -> quote environment
#    - Links -> \href{url}{text}
#    - YAML frontmatter -> \title/\author/\date
# ============================================================

import re
import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path


class MD2LaTeX:
    """Markdown to LaTeX converter using harryopo-mathnotes class."""

    def __init__(self, input_file, output_file=None):
        self.input_file = Path(input_file)
        self.output_file = output_file or self.input_file.with_suffix('.tex')
        self.frontmatter = {}
        self.has_table = False
        self.in_list = None       # 'ul' or 'ol'
        self.list_depth = 0
        self.in_code_block = False
        self.code_block_lang = ''
        self.code_lines = []

    def convert(self):
        """Main conversion pipeline."""
        text = self.input_file.read_text(encoding='utf-8')

        # 1. Extract YAML frontmatter
        text = self._parse_frontmatter(text)

        # 2. Split into blocks (paragraphs separated by blank lines)
        blocks = text.split('\n\n')

        # 3. Convert each block
        output_blocks = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            converted = self._convert_block(block)
            if converted:
                output_blocks.append(converted)

        # 4. Assemble document
        self._write_output(output_blocks)

    def _parse_frontmatter(self, text):
        """Extract YAML frontmatter."""
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            for line in fm_text.strip().split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.frontmatter[key.strip()] = value.strip().strip('"').strip("'")
            text = text[fm_match.end():]
        return text

    def _convert_block(self, block):
        """Convert a single block of Markdown to LaTeX."""
        lines = block.split('\n')

        # Code block (```)
        if lines[0].startswith('```'):
            return self._convert_code_block(lines)
        if self.in_code_block:
            return self._continue_code_block(lines)

        # Table (starts with |---| or contains | on every line)
        if self._is_table(lines):
            return self._convert_table(lines)

        # Heading (# ...)
        first_line = lines[0]
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', first_line)
        if heading_match and len(lines) == 1:
            return self._convert_heading(heading_match)

        # Unordered list
        if re.match(r'^[-*+]\s+.+', first_line):
            return self._convert_list(lines, ordered=False)

        # Ordered list
        if re.match(r'^\d+[.)]\s+.+', first_line):
            return self._convert_list(lines, ordered=True)

        # Blockquote
        if first_line.startswith('> '):
            return self._convert_blockquote(lines)

        # Horizontal rule
        if re.match(r'^[-*_]{3,}$', first_line.strip()):
            return '\\medskip\\hrule\\medskip'

        # Regular paragraph
        return self._convert_inline(block)

    # ==================== Code Blocks ====================

    def _is_table(self, lines):
        """Detect if a block is a Markdown table."""
        if len(lines) < 2:
            return False
        pipe_count = sum(1 for l in lines if '|' in l)
        if pipe_count < 2:
            return False
        # Check for separator line: e.g. |---|---| or |:---|:---:|
        for line in lines:
            # Protect $...$ math before checking (math may contain |)
            cleaned = re.sub(r'\$[^$]+\$', 'MATH', line)
            if re.match(r'^\|?[\s:\-]+\|[\s|\-:]+\|?$', cleaned):
                return True
        return False

    def _convert_code_block(self, lines):
        """Start a code block."""
        self.in_code_block = True
        self.code_block_lang = lines[0][3:].strip()
        self.code_lines = []
        return None  # Will accumulate lines

    def _continue_code_block(self, lines):
        """Continue or end a code block."""
        for line in lines:
            if line.startswith('```'):
                # End of code block
                code_text = '\n'.join(self.code_lines)
                self.in_code_block = False
                self.code_lines = []

                # Escape special LaTeX chars in code
                code_text = code_text.replace('\\', '\\textbackslash{}')
                code_text = code_text.replace('{', '\\{')
                code_text = code_text.replace('}', '\\}')
                code_text = code_text.replace('$', '\\$')
                code_text = code_text.replace('&', '\\&')
                code_text = code_text.replace('#', '\\#')
                code_text = code_text.replace('%', '\\%')
                code_text = code_text.replace('_', '\\_')
                code_text = code_text.replace('^', '\\^{}')

                return (
                    '\\begin{verbatim}\n' +
                    code_text + '\n' +
                    '\\end{verbatim}'
                )
            else:
                self.code_lines.append(line)
        return None

    # ==================== Headings ====================

    def _convert_heading(self, match):
        """Convert Markdown heading to LaTeX section."""
        level = len(match.group(1))
        title = self._convert_inline(match.group(2))
        levels = {1: 'section', 2: 'subsection', 3: 'subsubsection'}
        cmd = levels.get(level, 'paragraph')
        return f'\\{cmd}{{{title}}}'

    # ==================== Tables ====================

    def _convert_table(self, lines):
        """Convert Markdown table to LaTeX tabularx with smart column widths.

        Uses proportional X columns: each column's width ratio is calculated
        from content length then mapped to \\hsize=Xratio\\hsize for tabularx.
        This avoids Overfull hbox by properly accounting for \\tabcolsep gaps.
        """
        self.has_table = True

        # Protect $...$ math from |/pipe splitting
        math_map = {}
        mc = [0]

        def protect(m):
            mc[0] += 1
            k = f'<<<MATH{mc[0]}>>>'
            math_map[k] = m.group(0)
            return k

        def restore(text):
            for k, v in math_map.items():
                text = text.replace(k, v)
            return text

        # Parse rows
        rows = []
        separator_idx = -1
        for i, raw_line in enumerate(lines):
            # Protect math before any pipe splitting
            line = re.sub(r'\$[^$]+\$', protect, raw_line)
            # Strip leading/trailing | then split
            line = line.strip().strip('|')
            cells = [c.strip() for c in line.split('|')]
            # Restore math
            cells = [restore(c) for c in cells]

            # Check if separator row (also protect math first)
            cleaned = re.sub(r'\$[^$]+\$', 'MATH', raw_line)
            cleaned_cells = [c.strip() for c in cleaned.strip().strip('|').split('|')]
            if re.match(r'^[\s:\-]+$', '|'.join(cleaned_cells)):
                separator_idx = i
                continue
            rows.append(cells)

        if not rows:
            return ''

        ncols = max(len(r) for r in rows)
        if ncols == 0:
            return ''

        # Calculate column widths based on content
        max_lens = [0.0] * ncols
        for row in rows:
            for i, cell in enumerate(row):
                if i >= ncols:
                    break
                # Rough width: Chinese chars = 2, ASCII = 1
                w = sum(2 if ord(c) > 127 else 1 for c in cell)
                max_lens[i] = max(max_lens[i], float(w))

        total = sum(max_lens)
        if total == 0:
            max_lens = [1.0] * ncols
            total = float(ncols)

        # Build proportional X column spec for tabularx
        # Rule: sum of \\hsize across X columns must equal ncols
        colspec_parts = []
        for i in range(ncols):
            ratio = max_lens[i] / total if max_lens[i] > 0 else 1.0 / ncols
            hfactor = ratio * ncols
            colspec_parts.append(
                f'>{{\\hsize={hfactor:.3f}\\hsize\\linewidth=\\hsize}}X'
            )
        colspec = ''.join(colspec_parts)

        # Build LaTeX
        latex = ['\\begin{table}[htbp]', '\\centering']
        latex.append(f'\\begin{{tabularx}}{{\\textwidth}}{{{colspec}}}')
        latex.append('\\toprule')

        # First row = header, data starts after it
        header = rows[0]
        data_start = 1

        # Header row
        hcells = []
        for i in range(ncols):
            c = self._convert_inline(header[i]) if i < len(header) else ''
            hcells.append(f'\\textbf{{{c}}}' if c else '')
        latex.append(' & '.join(hcells) + ' \\\\')
        latex.append('\\midrule')

        # Data rows
        for row in rows[data_start:]:
            dcells = []
            for i in range(ncols):
                c = self._convert_inline(row[i]) if i < len(row) else ''
                dcells.append(c)
            latex.append(' & '.join(dcells) + ' \\\\')

        latex.append('\\bottomrule')
        latex.append('\\end{tabularx}')
        latex.append('\\end{table}')

        return '\n'.join(latex)

    # ==================== Lists ====================

    def _convert_list(self, lines, ordered=False):
        """Convert Markdown list to LaTeX itemize/enumerate."""
        env = 'enumerate' if ordered else 'itemize'
        items = []

        for line in lines:
            if ordered:
                item_match = re.match(r'^\d+[.)]\s+(.+)', line)
            else:
                item_match = re.match(r'^[-*+]\s+(.+)', line)

            if item_match:
                content = self._convert_inline(item_match.group(1))
                items.append(f'  \\item {content}')

        if not items:
            return ''

        return f'\\begin{{{env}}}\n' + '\n'.join(items) + f'\n\\end{{{env}}}'

    # ==================== Blockquote ====================

    def _convert_blockquote(self, lines):
        """Convert Markdown blockquote to LaTeX quote environment."""
        content_lines = []
        for line in lines:
            if line.startswith('> '):
                content_lines.append(line[2:])
            elif line.startswith('>'):
                content_lines.append(line[1:])

        content = '\n'.join(content_lines)
        content = self._convert_inline(content)

        return f'\\begin{{quote}}\n{content}\n\\end{{quote}}'

    # ==================== Inline Formatting ====================

    def _convert_inline(self, text):
        """Convert inline Markdown formatting to LaTeX."""
        # Math must be preserved (don't touch $...$)
        # Use placeholder technique

        # Protect math
        math_placeholders = {}
        math_count = [0]

        def protect_display_math(m):
            math_count[0] += 1
            key = f'<<<DISPLAYMATH{math_count[0]}>>>'
            math_placeholders[key] = f'$${m.group(1)}$$'
            return key

        def protect_inline_math(m):
            math_count[0] += 1
            key = f'<<<INLINEMATH{math_count[0]}>>>'
            math_placeholders[key] = f'${m.group(1)}$'
            return key

        text = re.sub(r'\$\$(.+?)\$\$', protect_display_math, text, flags=re.DOTALL)
        text = re.sub(r'\$(.+?)\$', protect_inline_math, text)

        # Inline code `code`
        text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)

        # Bold + Italic ***text***
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\emph{\1}}', text)

        # Bold **text**
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)

        # Italic *text* (but not **)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\emph{\1}', text)

        # Links [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)

        # Restore math
        for key, value in math_placeholders.items():
            text = text.replace(key, value)

        return text

    # ==================== Output ====================

    def _write_output(self, blocks):
        """Write the final LaTeX document."""
        title = self.frontmatter.get('title', 'Untitled')
        author = self.frontmatter.get('author', '')
        date = self.frontmatter.get('date', '\\today')
        has_toc = self.frontmatter.get('toc', '').lower() in ('true', 'yes', '1')

        parts = []
        parts.append(r'\documentclass{harryopo-mathnotes}')
        parts.append('')
        parts.append(r'\renewcommand{\mathtitle}{' + title + '}')
        if author:
            parts.append(r'\renewcommand{\mathauthor}{' + author + '}')
        parts.append(r'\date{' + date + '}')
        parts.append('')
        parts.append(r'\begin{document}')
        parts.append('')

        # Cover page
        parts.append(r'\newgeometry{top=3cm,bottom=2.5cm,left=4cm,right=4cm}')
        parts.append(r'\maketitle')
        parts.append(r'\thispagestyle{empty}')
        parts.append(r'\cleardoublepage')
        parts.append('')

        # Table of contents
        if has_toc:
            parts.append(r'\setcounter{tocdepth}{2}')
            parts.append(r'\tableofcontents')
            parts.append(r'\cleardoublepage')
            parts.append('')

        # Body
        parts.append(r'\strictpagecheck')
        parts.append(r'\setcounter{page}{1}')
        parts.append(r'\restoregeometry')
        parts.append(r'\onehalfspacing')
        parts.append('')

        # Filter out None blocks (unfinished code blocks)
        body_blocks = [b for b in blocks if b is not None]
        parts.append('\n\n'.join(body_blocks))
        parts.append('')
        parts.append(r'\end{document}')

        output = '\n'.join(parts)
        output += '\n'

        self.output_file.write_text(output, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description='harryopo-mathnotes Markdown to LaTeX Converter'
    )
    parser.add_argument('input', help='Input Markdown file (.md)')
    parser.add_argument('-o', '--output', help='Output LaTeX file (.tex)')
    parser.add_argument('--engine', choices=['python', 'pandoc'], default='pandoc',
                        help='Conversion engine: pandoc (default, recommended) or python (pure Python fallback)')
    parser.add_argument('--tex-only', action='store_true',
                        help='Only generate .tex, do not compile PDF')
    parser.add_argument('--clean', action='store_true',
                        help='Remove temp files after compilation')

    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        print(f'[ERROR] File not found: {input_file}', file=sys.stderr)
        sys.exit(1)

    script_dir = Path(__file__).parent
    output_file = args.output or input_file.with_suffix('.tex')
    output_file = Path(output_file)
    base = input_file.stem

    if args.engine == 'pandoc':
        # ---- Pandoc engine ----
        pandoc_exe = shutil.which('pandoc')
        if not pandoc_exe:
            print('[WARN] Pandoc not found, falling back to Python engine', file=sys.stderr)
            args.engine = 'python'
        else:
            print('[1/3] Pandoc -> LaTeX ...')
            template = script_dir / 'pandoc' / 'mathnotes-template.latex'
            lua_filter = script_dir / 'pandoc' / 'mathnotes-table.lua'

            cmd = [
                pandoc_exe,
                str(input_file),
                '--template=' + str(template),
                '--lua-filter=' + str(lua_filter),
                '--standalone',
                '-o', str(output_file),
            ]
            result = subprocess.run(cmd, cwd=str(script_dir),
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print(f'[FAIL] Pandoc error:\n{result.stderr}', file=sys.stderr)
                sys.exit(1)
            print(f'  [OK] {output_file}')

    if args.engine == 'python':
        # ---- Pure Python engine ----
        print('[1/3] Python Markdown -> LaTeX ...')
        converter = MD2LaTeX(input_file, output_file)
        converter.convert()
        print(f'  [OK] {output_file}')

    if args.tex_only:
        print(f'\nDone. LaTeX source: {output_file}')
        return

    # Step 2: LaTeX -> PDF
    print(f'\n[2/3] LaTeX -> PDF (xelatex x3) ...')

    for i in range(1, 4):
        print(f'  Pass {i} ...')
        subprocess.run(
            ['xelatex', '-interaction=nonstopmode',
             '-output-directory=' + str(script_dir),
             str(output_file.name)],
            cwd=str(script_dir),
            capture_output=True,
            text=True
        )

    pdf_file = script_dir / f'{base}.pdf'
    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        print(f'  [OK] {base}.pdf ({size_kb:.1f} KB)')
    else:
        print(f'  [FAIL] PDF build failed. Check {base}.log', file=sys.stderr)
        sys.exit(1)

    # Step 3: Clean
    print(f'\n[3/3] Clean temp files ...')

    if args.clean:
        for ext in ['aux', 'log', 'out', 'toc', 'lot', 'lof', 'bbl', 'blg']:
            tmp = script_dir / f'{base}.{ext}'
            if tmp.exists():
                tmp.unlink()
        print('  [OK] Temp files removed')
    else:
        print(f'  [INFO] Temp files kept ({base}.tex/.log/.aux/.toc)')

    print(f'\n{"=" * 60}')
    print(f'  Conversion complete!')
    print(f'    PDF: {pdf_file}')
    print(f'    TEX: {output_file}')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    main()
