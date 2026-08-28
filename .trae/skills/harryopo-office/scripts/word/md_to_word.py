# -*- coding: utf-8 -*-
r"""
md_to_word.py — Markdown 中间态 → 公文/学术 Word (.docx)

工作流（office 超级 skill · Word 流程）：
    1. AI 产出标准 Markdown（中间态，用户可直接查看/编辑）
    2. 用户确认/修改 Markdown
    3. 本脚本解析 Markdown → 渲染成 .docx（方正/开源字体一键切换）

用法：
    python md_to_word.py input.md                       # 默认方正配置，输出同目录
    python md_to_word.py input.md -o out.docx           # 指定输出路径
    python md_to_word.py input.md -c configs/opensource.json  # 开源字体
    python md_to_word.py input.md --no-toc              # 不自动更新目录

Markdown 约定（详见 SKILL.md Word 章节；语义与 convert.py 一致）：
    # 主标题（文档第一个 #）      大标题（方正大标宋，居中）
    > 副标题：xxx                 副标题（跟在主标题后）
    主标题后第一段裸文本 / > 作者：xxx   作者（居中楷体四号 14pt）
    **摘要：** 内容               摘要（标签黑体 + 内容楷体）
    **关键词：** 词1；词2          关键词
    # 一、引言（后续 #）          Heading 1（一、二、三…）
    ## 2.1 小节                   Heading 2
    ### 3.1.1 小节                Heading 3
    #### 3.1.1.1 小节             Heading 4
    正文段落…                     正文（方正书宋，首行缩进）
    **加粗**                      行内加粗 → 黑体
    > 注：…                      注释段落（仿宋，五号，灰色）
    > **表1：xxx**               表格标题（放表格上方）
    | a | b |                    表格（表头黑体居中，内容居中）
    ![图1：xxx](path.png)        图片（图注在下方；文件缺失自动占位）
    > 式(1)：xxx                 公式编号（放公式下方）
    $$ C_i = C_0 \cdot \alpha^i $$  行间公式（LaTeX → Word 原生 OMML）
    ## 参考文献                   参考文献区（[1] 条目）

设计原则：
    AI 只产出结构化 Markdown，引擎负责保真渲染；切换字体只需换配置文件。
"""

import argparse
import re
import sys
from pathlib import Path

from word_template_engine import WordTemplateEngine

# ============================================================
# LaTeX 数学 → OMML（Word 原生公式）
# ============================================================

M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
from lxml import etree

# 希腊字母映射（LaTeX 命令 → Unicode）
GREEK = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
    'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ',
    'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο',
    'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
    'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
    'Alpha': 'Α', 'Beta': 'Β', 'Gamma': 'Γ', 'Delta': 'Δ', 'Theta': 'Θ',
    'Lambda': 'Λ', 'Pi': 'Π', 'Sigma': 'Σ', 'Phi': 'Φ', 'Psi': 'Ψ',
    'Omega': 'Ω', 'Xi': 'Ξ', 'Upsilon': 'Υ',
    'varepsilon': 'ε', 'varphi': 'φ', 'vartheta': 'ϑ', 'sigma_0': 'σ',
}
# 常用运算符映射
OPS = {
    'times': '×', 'cdot': '·', 'pm': '±', 'mp': '∓', 'div': '÷',
    'leq': '≤', 'geq': '≥', 'neq': '≠', 'approx': '≈', 'equiv': '≡',
    'sim': '∼', 'll': '≪', 'gg': '≫',
    'in': '∈', 'notin': '∉', 'subset': '⊂', 'supset': '⊃',
    'subseteq': '⊆', 'supseteq': '⊇', 'cup': '∪', 'cap': '∩',
    'sum': '∑', 'prod': '∏', 'int': '∫', 'infty': '∞',
    'partial': '∂', 'nabla': '∇', 'emptyset': '∅',
    'rightarrow': '→', 'leftarrow': '←', 'leftrightarrow': '↔',
    'Rightarrow': '⇒', 'Leftarrow': '⇐', 'to': '→',
    'forall': '∀', 'exists': '∃', 'neg': '¬', 'land': '∧', 'lor': '∨',
    'circ': '∘', 'bullet': '•', 'ast': '∗', 'propto': '∝',
    'angle': '∠', 'perp': '⊥', 'parallel': '∥', 'cdotp': '·',
    'max': 'max', 'min': 'min', 'lim': 'lim', 'log': 'log', 'ln': 'ln',
    'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'exp': 'exp',
}


def _M(tag):
    """OMML 命名空间元素名"""
    return '{%s}%s' % (M_NS, tag)


def tokenize(latex):
    """LaTeX 数学字符串 → token 列表"""
    tokens = []
    buf = []
    i = 0
    n = len(latex)

    def flush():
        if buf:
            tokens.append(('text', ''.join(buf)))
            buf.clear()

    while i < n:
        c = latex[i]
        if c == '\\':
            j = i + 1
            while j < n and latex[j].isalpha():
                j += 1
            if j > i + 1:
                flush()
                tokens.append(('cmd', latex[i + 1:j]))
                i = j
            else:
                # 孤立的反斜杠，按字符处理
                if i + 1 < n:
                    buf.append(latex[i + 1])
                    i += 2
                else:
                    i += 1
        elif c in '^_':
            flush()
            tokens.append(('mod', c))
            i += 1
        elif c == '{':
            flush()
            tokens.append(('lbrace',))
            i += 1
        elif c == '}':
            flush()
            tokens.append(('rbrace',))
            i += 1
        elif c in '()[]':
            flush()
            tokens.append(('char', c))
            i += 1
        elif c.isspace():
            i += 1
        else:
            buf.append(c)
            i += 1
    flush()
    return tokens


def parse_single(tokens, pos):
    """解析单个原子（命令或字符），返回 (ast, pos_after)"""
    if pos >= len(tokens):
        return ('text', ''), pos
    tok = tokens[pos]
    if tok[0] == 'cmd':
        name = tok[1]
        if name in GREEK:
            return ('text', GREEK[name]), pos + 1
        if name in OPS:
            return ('text', OPS[name]), pos + 1
        return ('text', name), pos + 1
    if tok[0] == 'text':
        return ('text', tok[1]), pos + 1
    if tok[0] == 'char':
        return ('text', tok[1]), pos + 1
    return ('text', ''), pos


def parse_group(tokens, pos):
    """
    解析一组 token 直到遇到 '}' 或结尾。
    返回 (ast_list, pos_after)。
    """
    nodes = []
    while pos < len(tokens):
        tok = tokens[pos]
        kind = tok[0]
        if kind == 'rbrace':
            return nodes, pos + 1
        if kind == 'lbrace':
            inner, pos = parse_group(tokens, pos + 1)
            nodes.extend(inner)
            continue
        if kind == 'mod':
            nodes, pos = parse_mod(tokens, pos, nodes)
            continue
        if kind == 'cmd':
            name = tok[1]
            if name == 'frac':
                num, pos = parse_group(tokens, pos + 1)
                den, pos = parse_group(tokens, pos + 1)
                nodes.append(('frac', num, den))
                continue
            if name == 'sqrt':
                inner, pos = parse_group(tokens, pos + 1)
                nodes.append(('sqrt', inner))
                continue
            if name == 'left' or name == 'right':
                pos += 1
                continue
            if name == 'text':
                pos += 1
                if pos < len(tokens) and tokens[pos][0] == 'lbrace':
                    inner, pos = parse_group(tokens, pos + 1)
                    nodes.extend(inner)
                continue
            atom, pos = parse_single(tokens, pos)
            nodes.append(atom)
            continue
        if kind == 'text':
            nodes.append(('text', tok[1]))
            pos += 1
            continue
        if kind == 'char':
            nodes.append(('text', tok[1]))
            pos += 1
            continue
        pos += 1
    return nodes, pos


def parse_mod(tokens, pos, nodes):
    """处理 ^ 或 _ 修饰符，返回 (nodes, pos_after)"""
    mode = tokens[pos][1]  # '^' 上标 / '_' 下标
    pos += 1
    if pos < len(tokens) and tokens[pos][0] == 'lbrace':
        arg, pos = parse_group(tokens, pos + 1)
    else:
        arg, pos = [parse_single(tokens, pos)[0]], parse_single(tokens, pos)[1]
    base = nodes.pop() if nodes else ('text', '')
    if mode == '^':
        nodes.append(('sup', base, arg))
    else:
        nodes.append(('sub', base, arg))
    return nodes, pos


# ---------- AST → OMML ----------

def ast_to_elem(node):
    """AST 节点 → OMML 元素"""
    kind = node[0]
    if kind == 'text':
        r = etree.Element(_M('r'))
        t = etree.SubElement(r, _M('t'))
        t.text = node[1]
        return r
    if kind == 'sup':
        s = etree.Element(_M('sSup'))
        e = etree.SubElement(s, _M('e'))
        e.append(ast_to_elem(node[1]))
        sup = etree.SubElement(s, _M('sup'))
        for n in node[2]:
            sup.append(ast_to_elem(n))
        return s
    if kind == 'sub':
        s = etree.Element(_M('sSub'))
        e = etree.SubElement(s, _M('e'))
        e.append(ast_to_elem(node[1]))
        sub = etree.SubElement(s, _M('sub'))
        for n in node[2]:
            sub.append(ast_to_elem(n))
        return s
    if kind == 'frac':
        f = etree.Element(_M('f'))
        num = etree.SubElement(f, _M('num'))
        for n in node[1]:
            num.append(ast_to_elem(n))
        den = etree.SubElement(f, _M('den'))
        for n in node[2]:
            den.append(ast_to_elem(n))
        return f
    if kind == 'sqrt':
        rad = etree.Element(_M('rad'))
        radPr = etree.SubElement(rad, _M('radPr'))
        etree.SubElement(radPr, _M('degHide'))
        deg = etree.SubElement(rad, _M('deg'))
        e = etree.SubElement(rad, _M('e'))
        for n in node[1]:
            e.append(ast_to_elem(n))
        return rad
    return ast_to_elem(('text', ''))


def latex_to_omath(latex):
    """LaTeX 数学字符串 → OMML oMath 元素"""
    latex = latex.strip().strip('$').strip()
    tokens = tokenize(latex)
    nodes, _ = parse_group(tokens, 0)
    omath = etree.Element(_M('oMath'))
    for node in nodes:
        omath.append(ast_to_elem(node))
    return omath


# ============================================================
# Markdown 解析
# ============================================================

TABLE_SEP_RE = re.compile(r'^\s*\|?[\s:|-]+\|?\s*$')


def split_table_row(line):
    """按 | 拆分表格行，返回单元格列表"""
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


def is_separator_row(cells):
    """判断是否为 Markdown 表头分隔行（|---|）"""
    if not cells:
        return False
    joined = ''.join(cells)
    return bool(joined) and set(joined.replace(' ', '')) <= set('-: ')


def _next_content(lines, idx, n):
    """从 idx 起跳过空行，返回第一个非空行的 strip 内容（无则返回 None）"""
    while idx < n:
        s = lines[idx].strip()
        if s:
            return s
        idx += 1
    return None


def _prev_content(lines, idx):
    """从 idx 起向上跳过空行，返回第一个非空行的 strip 内容（无则返回 None）"""
    while idx >= 0:
        s = lines[idx].strip()
        if s:
            return s
        idx -= 1
    return None


def _next_content_idx(lines, idx, n):
    """从 idx 起跳过空行，返回第一个非空行的索引（无则返回 n）"""
    while idx < n:
        if lines[idx].strip():
            return idx
        idx += 1
    return n


def build_document(md_text, config_path=None, output_path='output.docx',
                   update_toc=True, base_dir=None):
    """解析 Markdown 中间态 → 生成 Word 文档

    base_dir: MD 文件所在目录，用于解析图片相对路径
              （office.py 等从别的 cwd 调用时，图片 `figures/xx.png`
               必须相对 MD 文件而非进程 cwd）
    """
    engine = WordTemplateEngine(config_path)

    # 自动目录放第一页（用户约定：目录第一页，正文从第二页开始）
    engine.add_toc()

    lines = md_text.split('\n')
    i = 0
    n = len(lines)

    # 主标题元信息（副标题/作者）
    first_title = None  # 文档主标题（仅第一个 `# `；后续 `# ` 是章节一级标题）
    subtitle = None
    author = None

    # 参考文献区
    in_refs = False
    refs = []

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # ---- 主标题 / 章节一级标题 ----
        # 语义与 convert.py 一致：第一个 `# ` 是文档主标题（收集副标题/作者），
        # 后续 `# ` 是章节一级标题（Heading 1，如 `# 一、引言`）
        if stripped.startswith('# '):
            if first_title is None:
                first_title = stripped[2:].strip()
                subtitle = None
                author = None
                # 向后收集副标题/作者（跳过空行）：
                #   1. blockquote 形式：> 副标题：xxx / > 作者：xxx
                #   2. 裸文本形式：标题后第一段（与 convert.py 回退逻辑一致）
                #      —— 非 # / 非 ![ / 非 ** 开头、非 摘要/关键词/作者 前缀、长度 < 60
                j = i + 1
                while j < n:
                    s = lines[j].strip()
                    if not s:
                        j += 1
                        continue
                    if s.startswith('> '):
                        content = s[2:].strip()
                        if content.startswith('副标题'):
                            subtitle = content.split('：', 1)[-1].split(':', 1)[-1].strip()
                            j += 1
                            continue
                        if content.startswith('作者'):
                            author = content.split('：', 1)[-1].split(':', 1)[-1].strip()
                            j += 1
                            continue
                    elif (not s.startswith('#')
                          and not s.startswith('![')
                          and not s.startswith('**')
                          and not re.match(r'^(摘要|关键词|作者)[：:]', s)
                          and len(s) < 60):
                        author = s
                        j += 1
                        continue
                    break
                engine.add_title(first_title, subtitle=subtitle, author=author)
                i = j
            else:
                h = stripped[2:].strip()
                engine.add_heading1(h)
                in_refs = h.startswith('参考') or '文献' in h
                i += 1
            continue

        # ---- 标题层级（与 convert.py 语义一致：#→H1 / ##→H2 / ###→H3 / ####→H4）----
        if stripped.startswith('#### '):
            engine.add_heading4(stripped[5:].strip())
            i += 1
            continue
        if stripped.startswith('### '):
            engine.add_heading3(stripped[4:].strip())
            i += 1
            continue
        if stripped.startswith('## '):
            h = stripped[3:].strip()
            engine.add_heading2(h)
            in_refs = h.startswith('参考') or '文献' in h
            i += 1
            continue

        # ---- 引用块（注释 / 表格标题 / 公式编号）----
        if stripped.startswith('> '):
            content = stripped[2:].strip()
            # 表格标题（> **表1：xxx** 或 > 表1：xxx）：
            # 前方（跳过空行）是表格 → 跳过，由表格处理器消费
            m = re.match(r'\*?\*?(表\d+[：:].*?)\*?\*?$', content)
            if m:
                nxt = _next_content(lines, i + 1, n)
                if nxt and nxt.startswith('|'):
                    i += 1
                    continue
            # 注释段落
            engine.add_annotation(content)
            i += 1
            continue

        # ---- 表格 ----
        if stripped.startswith('|'):
            # 收集连续表格行
            table_lines = []
            j = i
            while j < n and lines[j].strip().startswith('|'):
                table_lines.append(lines[j].strip())
                j += 1
            i = j
            # 解析
            parsed = [split_table_row(l) for l in table_lines]
            # 去掉分隔行
            rows = [r for r in parsed if not is_separator_row(r)]
            if not rows:
                continue
            headers = rows[0]
            data_rows = rows[1:]
            # 表格标题：向上（跳过空行）找 > 表N：
            caption = None
            k = i - len(table_lines) - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            if k >= 0 and lines[k].strip().startswith('> '):
                c = lines[k].strip()[2:].strip()
                m = re.match(r'\*?\*?(表\d+[：:].*?)\*?\*?$', c)
                if m:
                    caption = m.group(1).strip()
                    lines[k] = ''  # 消费该行
            engine.add_table(headers, data_rows, caption_text=caption)
            continue

        # ---- 行间公式 ----
        if stripped.startswith('$$'):
            j = i + 1
            formula = []
            while j < n and not lines[j].strip().startswith('$$'):
                if lines[j].strip():
                    formula.append(lines[j].strip())
                j += 1
            latex = ' '.join(formula)
            omath = latex_to_omath(latex)
            # 公式编号：向前（跳过空行）找 > 式(N)：
            caption = None
            k = _next_content_idx(lines, j + 1, n)
            if k < n:
                c = lines[k].strip()
                if c.startswith('> '):
                    cm = re.match(r'>\s*(式\(\d+\)[：:].*)', c)
                    if cm:
                        caption = cm.group(1).strip()
                        j = k
            engine.add_equation(omath, caption_text=caption)
            i = j + 1
            continue

        # ---- 图片 ----
        m = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
        if m:
            alt, path = m.groups()
            # 向前（跳过空行）找 > 注： 作为图片注释
            note = None
            k = _next_content_idx(lines, i + 1, n)
            if k < n:
                c = lines[k].strip()
                if c.startswith('> ') and c[2:].strip().startswith('注'):
                    note = c[2:].strip()
                    lines[k] = ''
            # 路径解析：先按 cwd，再按 MD 文件所在目录（base_dir）
            img_path = Path(path)
            if not img_path.exists() and base_dir and not img_path.is_absolute():
                alt_path = Path(base_dir) / img_path
                if alt_path.exists():
                    img_path = alt_path
            if img_path.exists():
                engine.add_picture(str(img_path), caption_text=alt or None, note=note)
            else:
                engine.add_figure_placeholder(alt or '图', hint=path or '[图片占位区]', note=note)
            i += 1
            continue

        # ---- 参考文献条目 ----
        m = re.match(r'\[(\d+)\]\s*(.*)', stripped)
        if m and in_refs:
            refs.append(m.group(2))
            i += 1
            continue

        # ---- 摘要 / 关键词 ----
        m = re.match(r'\*\*(摘要|关键词)[：:]\*\*\s*(.*)', stripped)
        if m:
            kind, content = m.group(1), m.group(2).strip()
            if kind == '摘要':
                engine.add_abstract(content)
            else:
                # 关键词（标签黑体 + 内容楷体）
                p = engine.doc.add_paragraph()
                engine._set_spacing(p, before=4, after=16)
                engine._set_indent(p, 2)
                engine._make_run(p, '关键词：', engine._get_font('heading2'),
                                 size=12, bold=True)
                engine._make_run(p, content, engine._get_font('heading3'),
                                 size=12)
            i += 1
            continue

        # ---- 正文 ----
        engine.add_body(stripped)
        i += 1

    # ---- 参考文献 ----
    if refs:
        engine.add_references(refs)

    engine.save(output_path, update_toc=update_toc)
    return output_path


def main():
    ap = argparse.ArgumentParser(
        description='Markdown 中间态 → 公文/学术 Word (.docx)')
    ap.add_argument('input', help='输入 Markdown 文件（中间态，可编辑）')
    ap.add_argument('-o', '--output', help='输出 docx 路径（默认同目录同名）')
    ap.add_argument('-c', '--config', default=None,
                    help='字体配置 JSON（默认 configs/fangzheng.json）')
    ap.add_argument('--no-toc', action='store_true',
                    help='不自动更新目录域（保留手动更新）')
    args = ap.parse_args()

    md_path = Path(args.input)
    if not md_path.exists():
        print(f'[ERROR] 输入文件不存在：{md_path}')
        sys.exit(1)

    config_path = args.config
    if config_path is None:
        config_path = str(Path(__file__).parent / 'configs' / 'fangzheng.json')

    output = args.output or str(md_path.with_suffix('.docx'))

    md_text = md_path.read_text(encoding='utf-8')
    build_document(md_text, config_path=config_path,
                   output_path=output, update_toc=not args.no_toc,
                   base_dir=md_path.parent)


if __name__ == '__main__':
    main()
