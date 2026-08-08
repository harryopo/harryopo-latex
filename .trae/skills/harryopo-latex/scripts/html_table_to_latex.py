"""
html_table_to_latex.py — MinerU HTML 表格 → LaTeX 转换器

处理 MinerU 输出的 HTML 表格格式：
  <table><tr><td>内容</td><td colspan="2">合并</td></tr>
         <tr><td rowspan="2">合并</td><td>数据</td></tr>...</table>

转换规则：
  - 简单表 → tabularx + booktabs 三线表
  - colspan → \\multicolumn{N}{c}{内容}
  - rowspan → \\multirow{N}{*}{内容}（后续行留空）
  - 行数 > 20 → longtable（跨页）
  - 加粗完全依赖原文 ** 标记，不做自动推断

依赖：仅 Python 标准库（re, html）
"""

import re
import html as html_module
from typing import List, Optional, Tuple
from dataclasses import dataclass, field


# ───────────────────────── 数据结构 ─────────────────────────

@dataclass
class Cell:
    """表格单元格"""
    content: str = ""
    rowspan: int = 1
    colspan: int = 1
    is_rowspan_cover: bool = False   # 被上方 rowspan 覆盖（保留位置，输出空）
    is_colspan_cover: bool = False   # 被 colspan 覆盖（完全跳过，不输出）


@dataclass
class ParsedTable:
    """解析后的表格"""
    rows: List[List[Cell]] = field(default_factory=list)
    ncols: int = 0  # 实际列数（展开 colspan 后）

    @property
    def nrows(self) -> int:
        return len(self.rows)

    @property
    def has_merge(self) -> bool:
        """是否含合并单元格"""
        for row in self.rows:
            for cell in row:
                if cell.rowspan > 1 or cell.colspan > 1:
                    return True
        return False

    @property
    def is_longtable(self) -> bool:
        """是否应该用 longtable（行数 > 20 或行数 > 0 且估算高度可能超页）"""
        return self.nrows > 20


# ───────────────────────── HTML 解析 ─────────────────────────

def parse_html_table(html_str: str) -> ParsedTable:
    """解析 HTML 表格字符串为 ParsedTable

    支持 MinerU 格式：<table><tr><td>..</td><td colspan="2">..</td></tr>...</table>
    """
    # 提取所有行
    tr_pattern = r'<tr[^>]*>(.*?)</tr>'
    tr_matches = re.findall(tr_pattern, html_str, re.DOTALL)

    if not tr_matches:
        return ParsedTable()

    # 提取每行的单元格
    td_pattern = r'<td([^>]*)>(.*?)</td>'
    th_pattern = r'<th([^>]*)>(.*?)</th>'

    raw_rows: List[List[Cell]] = []

    for tr_content in tr_matches:
        # 匹配 td 和 th（th 也当作 td 处理，内容加粗）
        cells_raw = []
        for attrs, content in re.findall(td_pattern, tr_content, re.DOTALL):
            cells_raw.append(_parse_cell_attrs(attrs, content))
        # th（表头单元格）
        for attrs, content in re.findall(th_pattern, tr_content, re.DOTALL):
            cell = _parse_cell_attrs(attrs, content)
            cell.content = f"**{cell.content}**"  # 标记为加粗
            cells_raw.append(cell)

        if cells_raw:
            raw_rows.append(cells_raw)

    if not raw_rows:
        return ParsedTable()

    # 构建网格（处理 rowspan 占用）
    return _build_grid(raw_rows)


def _parse_cell_attrs(attrs: str, raw_content: str) -> Cell:
    """解析 td/th 的属性和内容"""
    rowspan = 1
    colspan = 1

    # colspan="2" 或 colspan=2
    colspan_match = re.search(r'colspan\s*=\s*["\']?(\d+)', attrs)
    if colspan_match:
        colspan = int(colspan_match.group(1))

    rowspan_match = re.search(r'rowspan\s*=\s*["\']?(\d+)', attrs)
    if rowspan_match:
        rowspan = int(rowspan_match.group(1))

    # 清理内容：去 <p></p> 包裹、保留加粗标记、HTML 实体、多余空白
    content = raw_content.strip()
    # 去掉 <p>...</p> 包裹
    content = re.sub(r'</?p>', '', content)
    # <strong>...</strong> 和 <b>...</b> → **加粗**（必须在去标签之前处理）
    content = re.sub(r'<(?:strong|b)>(.*?)</(?:strong|b)>', r'**\1**', content, flags=re.DOTALL)
    # <em>...</em> 和 <i>...</i> → *斜体*
    content = re.sub(r'<(?:em|i)>(.*?)</(?:em|i)>', r'*\1*', content, flags=re.DOTALL)
    # 有序列表 <ol><li>...</li></ol> → 1. ... 2. ...
    li_items = re.findall(r'<li>(.*?)</li>', content, re.DOTALL)
    if li_items and '<ol>' in content:
        content = '\n'.join(f'{i+1}. {re.sub(r"<[^>]+>", "", item).strip()}' for i, item in enumerate(li_items))
    elif li_items and '<ul>' in content:
        content = '\n'.join(f'- {re.sub(r"<[^>]+>", "", item).strip()}' for item in li_items)
    # 去掉其他 HTML 标签
    content = re.sub(r'<[^>]+>', '', content)
    # HTML 实体解码
    content = html_module.unescape(content)
    # 压缩空白（但保留换行，列表项需要换行）
    content = re.sub(r'[ \t]+', ' ', content).strip()

    return Cell(content=content, rowspan=rowspan, colspan=colspan)


def _build_grid(raw_rows: List[List[Cell]]) -> ParsedTable:
    """将原始行数据构建为规则网格，正确处理 rowspan 占位

    算法：
    - 维护 occupied 字典 {(row, col): remaining_rowspan}
    - 遍历每行每个单元格，跳过被占用的列
    - rowspan > 1 时，在后续行的对应列标记占用
    """
    table = ParsedTable()
    # 先确定最大列数（考虑 colspan）
    max_cols = 0
    occupied: dict = {}  # (row_idx, col_idx) -> remaining_rowspan

    for row_idx, raw_cells in enumerate(raw_rows):
        grid_row: List[Cell] = []
        col_idx = 0
        cell_iter = iter(raw_cells)

        while col_idx < max_cols or len(grid_row) < _count_needed_cols(raw_cells, occupied, row_idx):
            # 检查这个位置是否被上方的 rowspan 占用
            if (row_idx, col_idx) in occupied:
                # 这是一个 rowspan 的延续位置
                grid_row.append(Cell(is_rowspan_cover=True))
                # 减少 remaining rowspan
                remaining = occupied[(row_idx, col_idx)]
                if remaining > 1:
                    occupied[(row_idx + 1, col_idx)] = remaining - 1
                del occupied[(row_idx, col_idx)]
                col_idx += 1
                continue

            # 放置下一个单元格
            try:
                cell = next(cell_iter)
            except StopIteration:
                break

            # 处理 colspan：占多列，后续列标记 is_colspan_cover（生成时跳过）
            for c in range(cell.colspan):
                actual_col = col_idx + c
                if c == 0:
                    grid_row.append(cell)
                else:
                    grid_row.append(Cell(is_colspan_cover=True))

                # 处理 rowspan
                if cell.rowspan > 1:
                    occupied[(row_idx + 1, actual_col)] = cell.rowspan - 1

            col_idx += cell.colspan

        # 更新最大列数
        actual_cols = sum(c.colspan if not c.is_rowspan_cover else 1 for c in grid_row)
        # 更精确：grid_row 的长度就是展开后的列数（含占位）
        max_cols = max(max_cols, len(grid_row))

        table.rows.append(grid_row)

    table.ncols = max_cols
    return table


def _count_needed_cols(raw_cells: List[Cell], occupied: dict, row_idx: int) -> int:
    """计算这行需要的列数（含 colspan 展开 + 占位）"""
    total = 0
    for cell in raw_cells:
        total += cell.colspan
    # 加上占位数（这行起始时仍被占用的列）
    for (r, c), _ in occupied.items():
        if r == row_idx:
            total += 1
    return total


# ───────────────────────── LaTeX 生成 ─────────────────────────

def _latex_escape(text: str) -> str:
    """LaTeX 特殊字符转义"""
    out = text
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


def _apply_inline_format(text: str) -> str:
    """应用行内格式：加粗→黑体、斜体保留、换行→LaTeX换行"""
    # 先转义
    text = _latex_escape(text)
    # 加粗内含换行时，先把 ** 之间的换行处理掉
    # \fzht{} 不能跨行，把 \fzht{...换行...} 拆为多段 \fzht{}
    # 策略：先匹配 **...** ，如果有换行，把每行分别 \fzht{}
    def _bold_replacer(m):
        inner = m.group(1)
        if '\n' in inner:
            # 多行加粗：每行分别 \fzht{}，用 \\ 连接
            lines = inner.split('\n')
            return ' '.join(f'\\fzht{{{l.strip()}}}' for l in lines if l.strip())
        return f'\\fzht{{{inner}}}'
    text = re.sub(r'\*\*\*(.+?)\*\*\*', _bold_replacer, text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.+?)\*\*', _bold_replacer, text, flags=re.DOTALL)
    # 斜体 * → \textit{}
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    # 单元格内的编号列表（来自 <ol><li>）→ 用换行连接的纯文本
    # 避免在 multicolumn 花括号内产生 enumerate 环境
    # 匹配 "N. text" 开头的行（编号列表）
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        # 匹配编号列表项 "1. xxx" 或 "2. xxx"
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            formatted_lines.append(stripped)  # 保留原始编号文本
        else:
            formatted_lines.append(line)
    text = '\n'.join(formatted_lines)
    return text


def generate_latex(table: ParsedTable, caption: str = "") -> List[str]:
    """根据 ParsedTable 生成 LaTeX 表格代码

    规则：
    - 无合并 + 行少 → tabularx + booktabs
    - 有合并 → tabular 固定列宽 + multirow/multicolumn
    - 行多（>20） → longtable 跨页
    """
    if table.ncols == 0 or table.nrows == 0:
        return [r"% empty table"]

    lines: List[str] = []

    # 判断表格类型
    use_longtable = table.is_longtable
    has_merge = table.has_merge

    # 列格式
    if use_longtable:
        return _generate_longtable(table, caption)
    elif has_merge:
        return _generate_merged_table(table, caption)
    else:
        return _generate_simple_table(table, caption)


def _col_spec(ncols: int, has_borders: bool = False) -> str:
    """生成不会溢出页边距的列规格

    用嵌套 \\dimexpr 精确计算列宽：
      可用总宽 = \\textwidth - 2×(ncols+1)×\\tabcolsep - (ncols+1)×\\arrayrulewidth
      每列宽 = 可用总宽 / ncols

    有边框时（|p{}|...|）LaTeX 在表格左右边缘各加一个 \\tabcolsep 和竖线，
    所以总共 (ncols+1) 个竖线 + 2×(ncols+1) 个 tabcolsep。

    Args:
        ncols: 列数
        has_borders: 是否有竖线边框
    """
    if has_borders:
        # 嵌套 dimexpr：先算总可用宽度，再除以列数
        total_sep = 2 * (ncols + 1)  # tabcolsep 个数
        total_rule = ncols + 1       # 竖线个数
        # -1pt 安全余量抵消 dimexpr 整数截断
        col = rf"p{{\dimexpr\dimexpr\textwidth-{total_sep}\tabcolsep-{total_rule}\arrayrulewidth-1pt\relax/{ncols}\relax}}"
        return '|' + '|'.join([col] * ncols) + '|'
    else:
        col = rf"p{{\dimexpr\dimexpr\textwidth-{2*ncols}\tabcolsep\relax/{ncols}\relax}}"
        return ' '.join([col] * ncols)


def _generate_simple_table(table: ParsedTable, caption: str) -> List[str]:
    """简单表：tabularx + booktabs 三线表"""
    ncols = table.ncols
    col_spec = ' '.join(r'>{\raggedright\arraybackslash}X' for _ in range(ncols))

    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \small",
        r"  \begin{tabularx}{\textwidth}{" + col_spec + r"}",
        r"    \toprule",
    ]

    for row_idx, row in enumerate(table.rows):
        cells = []
        for cell in row:
            if cell.is_colspan_cover:
                continue  # colspan 后续列完全跳过
            if cell.is_rowspan_cover:
                cells.append("")  # rowspan 延续保留位置
            else:
                formatted = _apply_inline_format(cell.content)
                cells.append(formatted)

        lines.append("    " + " & ".join(cells) + r" \\")

        if row_idx == 0:
            lines.append(r"    \midrule")

    lines.append(r"    \bottomrule")
    lines.append(r"  \end{tabularx}")
    if caption:
        lines.append(r"  \caption{" + _latex_escape(caption) + r"}")
    lines.append(r"\end{table}")
    lines.append("")
    return lines


def _generate_merged_table(table: ParsedTable, caption: str) -> List[str]:
    """含合并单元格的表：tabular 固定列宽 + multirow/multicolumn

    注意：multirow 与 tabularx 冲突，必须用固定列宽 tabular
    """
    ncols = table.ncols
    # 用 dimexpr 精确计算列宽，避免溢出
    col_spec = _col_spec(ncols, has_borders=False)

    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \small",
        r"  \begin{tabular}{" + col_spec + r"}",
        r"    \toprule",
    ]

    for row_idx, row in enumerate(table.rows):
        cells = []

        for cell in row:
            if cell.is_colspan_cover:
                continue  # colspan 后续列完全跳过

            if cell.is_rowspan_cover:
                # rowspan 占位：输出空（multirow 会自动覆盖这个位置）
                cells.append("")
                continue

            formatted = _apply_inline_format(cell.content)

            # 处理 colspan
            if cell.colspan > 1:
                # 用 p{width} 避免 c 对长内容不换行导致溢出
                width_frac = cell.colspan / table.ncols * 0.98
                cells.append(f"\\multicolumn{{{cell.colspan}}}{{p{{{width_frac:.3f}\\textwidth}}}}{{{formatted}}}")
            elif cell.rowspan > 1:
                # \multirow{N}{*}{内容}
                cells.append(f"\\multirow{{{cell.rowspan}}}{{*}}{{{formatted}}}")
            else:
                cells.append(formatted)

        lines.append("    " + " & ".join(cells) + r" \\")

        if row_idx == 0:
            lines.append(r"    \midrule")

    lines.append(r"    \bottomrule")
    lines.append(r"  \end{tabular}")
    if caption:
        lines.append(r"  \caption{" + _latex_escape(caption) + r"}")
    lines.append(r"\end{table}")
    lines.append("")
    return lines


def _generate_longtable(table: ParsedTable, caption: str) -> List[str]:
    """跨页长表：longtable + \\endhead/\\endfoot

    用预定义的 \\cellw 长度保证列宽和 multicolumn 宽度精确匹配。
    """
    ncols = table.ncols

    # 用 dimexpr 精确计算列宽，带边框
    total_sep = 2 * (ncols + 1)
    total_rule = ncols + 1
    col_w_expr = rf"\dimexpr\dimexpr\textwidth-{total_sep}\tabcolsep-{total_rule}\arrayrulewidth-1pt\relax/{ncols}\relax"
    col = rf"p{{{col_w_expr}}}"
    col_spec = '|' + '|'.join([col] * ncols) + '|'

    lines = [
        # 预定义列宽为真实长度，用于 multicolumn 精确计算
        rf"\newlength{{\cellw}}",
        rf"\setlength{{\cellw}}{{{col_w_expr}}}",
        r"\begin{longtable}{" + col_spec + r"}",
        r"\hline",
        r"\endfirsthead",
        r"\hline",
        r"\endhead",
        r"\hline",
        r"\endfoot",
        r"\hline",
        r"\endlastfoot",
    ]

    # 所有行作为数据输出（表头作为第一行）
    for row_idx, row in enumerate(table.rows):
        cells = []
        for cell in row:
            if cell.is_colspan_cover:
                continue
            if cell.is_rowspan_cover:
                cells.append("")
            else:
                formatted = _apply_inline_format(cell.content)
                if cell.colspan > 1:
                    # 精确计算：K列合并宽度 = K×单列宽 + (K-1)×(竖线+2×tabcolsep)
                    k = cell.colspan
                    mc_w = rf"\dimexpr{k}\cellw+{k-1}\arrayrulewidth+{2*(k-1)}\tabcolsep\relax"
                    cells.append(f"\\multicolumn{{{cell.colspan}}}{{|p{{{mc_w}}}|}}{{{formatted}}}")
                elif cell.rowspan > 1:
                    cells.append(f"\\multirow{{{cell.rowspan}}}{{*}}{{{formatted}}}")
                else:
                    cells.append(formatted)
        lines.append("  " + " & ".join(cells) + r" \\ \hline")

    lines.append(r"\end{longtable}")
    lines.append("")
    return lines


# ───────────────────────── 对外接口 ─────────────────────────

def html_table_to_latex(html_str: str, caption: str = "") -> List[str]:
    """将 HTML 表格字符串转换为 LaTeX 表格代码

    自动判断表格类型（简单/合并/跨页），生成最优 LaTeX 结构。

    Args:
        html_str: HTML 表格字符串（MinerU 输出格式）
        caption: 表格标题（可选）

    Returns:
        LaTeX 代码行列表

    Examples:
        >>> html = '<table><tr><td>A</td><td>B</td></tr><tr><td>1</td><td>2</td></tr></table>'
        >>> latex = html_table_to_latex(html)
    """
    table = parse_html_table(html_str)
    if table.ncols == 0:
        return [r"% 表格解析失败或为空"]
    return generate_latex(table, caption)


def replace_html_tables_in_markdown(md_content: str, caption_template: str = "表{idx}") -> str:
    """替换 Markdown 内容中的所有 HTML 表格为 LaTeX 代码

    用于 MinerU 输出后的 MD 清洗步骤。

    Args:
        md_content: 含 HTML 表格的 Markdown 文本
        caption_template: 表格标题模板，{idx} 会被替换为表格序号

    Returns:
        清洗后的文本（HTML 表格被替换为 LaTeX）
    """
    # 找到所有 <table>...</table>
    pattern = r'<table>.*?</table>'

    def _replace(match, idx=[0]):
        idx[0] += 1
        html = match.group(0)
        caption = caption_template.format(idx=idx[0])
        latex_lines = html_table_to_latex(html, caption)
        return '\n'.join(latex_lines)

    return re.sub(pattern, _replace, md_content, flags=re.DOTALL)


# ───────────────────────── 自测 ─────────────────────────

if __name__ == '__main__':
    # 测试用例
    test_cases = [
        ("简单表", '<table><tr><td><p>方法</p></td><td><p>准确率</p></td></tr><tr><td><p>ResNet</p></td><td><p>94.2%</p></td></tr></table>'),
        ("水平合并", '<table><tr><td colspan="2"><p>主干网络</p></td><td><p>性能</p></td></tr><tr><td><p>ResNet</p></td><td><p>ImageNet</p></td><td><p>94.2%</p></td></tr></table>'),
        ("垂直合并", '<table><tr><td><p>模型</p></td><td><p>数据集</p></td><td><p>准确率</p></td></tr><tr><td rowspan="2"><p>Ours</p></td><td><p>CIFAR-10</p></td><td><p>98.5%</p></td></tr><tr><td><p>CIFAR-100</p></td><td><p>85.3%</p></td></tr></table>'),
    ]

    for name, html in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"{'='*60}")
        print(f"输入: {html[:80]}...")
        result = html_table_to_latex(html, f"测试表格-{name}")
        print(f"\n输出:")
        for line in result:
            print(f"  {line}")
