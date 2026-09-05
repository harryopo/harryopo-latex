#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
latex_diagnostics — LaTeX 编译诊断与 .tex 预检（纯函数库，无 MCP 依赖）
=======================================================================

两部分能力（借鉴 overleaf-mcp 的 7 项静态检查 + archify 的"错误码+证据+修复建议"单据形态）：

1. parse_log(log_text)          — 解析 XeLaTeX 日志 → 结构化错误/警告/页数
2. suggest_fix(message)         — 常见错误 → 修复建议（中文）
3. lint_tex(tex_text, tex_dir)  — 编译前静态预检（7 项，返回 Problem 列表）

所有 Problem 统一形态：code（稳定错误码）/ severity / line / message / suggestion。
供 build_mcp.py 的 MCP 工具与 skill 脚本直接复用。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

# ============ 通用 Problem ============

def _p(code: str, severity: str, line: Optional[int], message: str, suggestion: str) -> dict:
    return {'code': code, 'severity': severity, 'line': line,
            'message': message, 'suggestion': suggestion}


# ============ 1. 日志解析 ============

_OVERFULL_RE = re.compile(r'Overfull \\[hv]box \(([\d.]+)pt too (?:wide|high)\) in paragraph at lines (\d+)--(\d+)')
_WARN_RE = re.compile(r'((?:LaTeX|Package|Class) Warning:[^\n]*(?:\n[ \t]+[^\n]*)*)')
_ERROR_RE = re.compile(r'^! (.+)$', re.M)
_LOCATION_RE = re.compile(r'^l\.(\d+)\s?(.*)$', re.M)
_PAGES_RE = re.compile(r'Output written on .+?\((\d+) page')
_MISSFILE_RE = re.compile(r"! LaTeX Error: (?:File `([^']+)' not found\.|File `([^']+)' not found)")

# 常见错误 → 修复建议（模式 → 中文建议；按顺序首个命中生效）
# 注意：pattern 是正则——字面反斜杠/花括号/美元号必须转义（\h 等非法转义在 3.13 直接抛错）
_FIX_TABLE = (
    ('Undefined control sequence', '未定义命令：检查拼写；若是宏包命令确认已 \\usepackage；harryopo 模板请查 SKILL.md 可用命令表'),
    ('not found', '文件找不到：检查 \\include/\\input/\\includegraphics 路径与文件名大小写；harryopo 字体由 TEXINPUTS 提供，编译时需保留环境变量'),
    (r'Missing \$ inserted', '数学模式缺失：文本中含 _ ^ 或数学符号需包进 $...$'),
    ('Runaway argument', '参数未闭合：检查花括号 {} 配对或环境是否缺 \\end'),
    (r'Missing \\begin\{document\}', '导言区出现正文命令：preamble 只能放 \\usepackage/\\newcommand 等定义'),
    ('Extra alignment tab', '表格列数超出列定义：检查该行 & 数量是否比列声明多'),
    ('Misplaced alignment tab', '表格 & 出现在非表格环境：检查环境配对'),
    (r'Overfull \\[hv]box', '内容超宽：缩短文本、改列宽、或用 \\rlap{} 让内容伸入页边距（harryopo 惯例）'),
    (r'Environment .* undefined', '环境未定义：确认宏包加载（如 longtable/tabularx 需对应 \\usepackage）'),
    (r'Unicode character .* not set up', '当前字体缺该字形：中文语境换方正字体命令（\\fzht 等），或换含该字符的字体'),
    (r'Font .* not found', '字体未找到：确认 fonts/ 目录与 TEXINPUTS 环境变量（编译需在正确 cwd）'),
    (r'floats? lost', '浮动体丢失：\\begin{figure} 内不能 \\section，检查环境嵌套'),
    (r'Citation .* undefined', '引用未定义：\\cite 的 key 是否在 \\bibitem 中；需再编译一遍'),
    (r'Reference .* undefined', '交叉引用未定义：\\ref 的 key 是否有对应 \\label；需再编译一遍'),
)


def suggest_fix(message: str) -> str:
    low = message[:200]
    for pat, fix in _FIX_TABLE:
        if re.search(pat, low, re.I):
            return fix
    return '查看该错误上下文行，定位对应 .tex 源行后修正'


def parse_log(log_text: str) -> dict:
    """解析 xelatex 日志。返回 {success, pages, errors[], warnings[], overfull[]}。

    errors/warnings 元素含 line（尽量提取 l.NNN）与 suggestion。
    Package Error 的具体原因在后续 `(pkg)` 续行中，一并合并进 message。
    """
    errors = []
    for m in _ERROR_RE.finditer(log_text):
        msg = m.group(1).strip()
        # Package Error 的说明在续行（(fontspec) xxx 形式）——合并最多 3 行
        tail = log_text[m.end():m.end() + 500]
        cont = re.findall(r'^\((\w[\w-]*)\)\s+(.+)$', tail, re.M)[:3]
        if cont:
            msg = f'{msg} ' + ' '.join(c[1].strip() for c in cont)
        msg = ' '.join(msg.split())
        # 找错误后最近的 l.NNN（错误位置）
        lm = _LOCATION_RE.search(tail)
        line = int(lm.group(1)) if lm else None
        context = lm.group(2).strip()[:120] if lm else ''
        errors.append({
            'message': msg[:260], 'line': line, 'context': context,
            'suggestion': suggest_fix(msg),
        })
    warnings = []
    for m in _WARN_RE.finditer(log_text):
        w = ' '.join(m.group(1).split())
        if w not in warnings:
            warnings.append(w[:220])
    overfull = [{'from_line': int(m.group(2)), 'to_line': int(m.group(3)),
                 'pt': float(m.group(1))}
                for m in _OVERFULL_RE.finditer(log_text)]
    pm = _PAGES_RE.search(log_text)
    return {
        'success': not errors and bool(pm),
        'pages': int(pm.group(1)) if pm else None,
        'errors': errors,
        'warnings': warnings[:30],
        'overfull': overfull,
    }


# ============ 2. .tex 静态预检（7 项） ============

def _strip_line_comment(line: str) -> str:
    """去掉行内注释（% 后内容；\\% 不算注释起始）。"""
    out, i = [], 0
    while i < len(line):
        ch = line[i]
        if ch == '\\' and i + 1 < len(line):
            out.append(line[i:i + 2]); i += 2; continue
        if ch == '%':
            break
        out.append(ch); i += 1
    return ''.join(out)


def _clean_tex(tex_text: str):
    """按行去注释，返回 [(lineno, line_text)]（lineno 从 1 起）。"""
    return [(i + 1, _strip_line_comment(l))
            for i, l in enumerate(tex_text.splitlines())]


def lint_tex(tex_text: str, tex_dir: Optional[Path] = None) -> list:
    """编译前静态预检。返回 Problem 列表（code L01–L07）。"""
    problems = []
    lines = _clean_tex(tex_text)
    cleaned = '\n'.join(t for _, t in lines)
    body = cleaned.split(r'\begin{document}', 1)[-1]  # 环境检查只看正文

    # L01 begin/end 环境配平（栈）
    env_re = re.compile(r'\\(begin|end)\{(\*?[a-zA-Z]+\*?)\}')
    stack = []
    for ln, text in lines:
        for m in env_re.finditer(text):
            kind, env = m.groups()
            if kind == 'begin':
                stack.append((env, ln))
            else:
                if not stack:
                    problems.append(_p('L01', 'error', ln,
                                       f'\\end{{{env}}} 没有对应的 \\begin',
                                       '检查 \\begin 是否拼写错误或被注释'))
                elif stack[-1][0] != env:
                    got = stack.pop()
                    problems.append(_p('L01', 'error', ln,
                                       f'\\end{{{env}}} 与最近 \\begin{{{got[0]}}}(行{got[1]}) 不匹配',
                                       '环境嵌套错乱，逐个核对 begin/end'))
                else:
                    stack.pop()
    for env, ln in stack:
        problems.append(_p('L01', 'error', ln,
                           f'\\begin{{{env}}}(行{ln}) 缺少 \\end',
                           '补齐 \\end{' + env + '}'))

    # L02 数学定界符配平（$ 计数，排除 \$；verbatim 内容已随注释剥离保留——先剔除代码环境）
    no_code = re.sub(r'\\begin\{(verbatim|lstlisting|minted)\*?\}[\s\S]*?\\end\{\1\*?\}',
                     '', cleaned)
    dollars = len(re.findall(r'(?<!\\)\$', no_code))
    if dollars % 2:
        problems.append(_p('L02', 'error', None,
                           f'行内数学定界符 $ 不配对（共 {dollars} 个）',
                           '逐段检查 $...$ 是否漏了另一半'))

    # L03 表格列数一致性
    tab_envs = re.finditer(
        r'\\begin\{(tabular[x*]?|longtable)\}(\*?\[[^\]]*\])?\{([^}]+)\}',
        cleaned, re.S)
    for tm in tab_envs:
        env, colspec = tm.group(1), tm.group(3)
        # 列计数：去掉 p{..}/>{..}/<{..}@{..} 的参数与前缀装饰，再数列字母
        # （tabularx 的 X 列、标准 l/c/r/p 均计 1 列；| 间距线不计）
        spec = re.sub(r'[><]?\{[^{}]*\}', '', colspec)
        spec = re.sub(r'@\{[^{}]*\}', '', spec)
        ncol = len(re.findall(r'[lcrpX]', spec.replace('|', '').replace(' ', '')))
        body_start = tm.end()
        end_m = re.compile(r'\\end\{' + env + r'\}').search(cleaned, body_start)
        seg = cleaned[body_start:end_m.start() if end_m else len(cleaned)]
        offset_lines = cleaned[:body_start].count('\n')
        reported = False
        for off, row in enumerate(seg.split('\n')):
            row = row.strip()
            if not row or row.startswith(r'\end') or row.startswith('\\hline') \
                    or row.startswith('\\cmidrule') or row.startswith('\\toprule') \
                    or row.startswith('\\bottomrule') or row.startswith('\\midrule') \
                    or row.startswith('\\endhead') or row.startswith('\\endfirsthead') \
                    or row.startswith('%'):
                continue
            n_amp = row.count('&')
            if ncol and n_amp + 1 > ncol and not reported:
                problems.append(_p('L03', 'error', offset_lines + off + 1,
                                   f'{env} 列声明 {ncol} 列但该行有 {n_amp + 1} 列内容',
                                   '减少 & 或修正列定义（含 X 列与 p{宽} 情形）'))
                reported = True  # 每个表格只报第一处

    # L04 悬空引用 + L05 重复 label
    labels = {}
    for ln, text in lines:
        for m in re.finditer(r'\\label\{([^}]+)\}', text):
            labels.setdefault(m.group(1), []).append(ln)
    for key, lns in labels.items():
        if len(lns) > 1:
            problems.append(_p('L05', 'error', lns[1],
                               f'\\label{{{key}}} 重复定义（行 {lns}）',
                               'label 必须唯一，重命名其一'))
    for ln, text in lines:
        for m in re.finditer(r'\\(?:ref|eqref|autoref|pageref|cref)\{([^}]+)\}', text):
            if m.group(1) not in labels:
                problems.append(_p('L04', 'error', ln,
                                   f'\\ref{{{m.group(1)}}} 无对应 \\label',
                                   '补 \\label 或修正引用 key'))

    # L06 \includegraphics 文件存在性
    if tex_dir:
        for ln, text in lines:
            for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text):
                target = m.group(1)
                if target.startswith('placeholder') or target.startswith('figures/placeholder'):
                    continue  # 占位图机制允许不存在
                cand = [tex_dir / target, tex_dir / (target + '.pdf'),
                        tex_dir / (target + '.png'), tex_dir / (target + '.jpg')]
                if not any(c.exists() for c in cand):
                    problems.append(_p('L06', 'error', ln,
                                       f'\\includegraphics{{{target}}} 文件不存在',
                                       '检查 figures/ 下文件名，或放入占位图'))

    # L07 正文花括号配平（累计计数，剔除命令内转义 \{ \}）
    depth, first_neg = 0, None
    for i, ch in enumerate(re.sub(r'\\[{}]', '', no_code)):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0 and first_neg is None:
                first_neg = no_code[:i].count('\n') + 1
    if depth > 0:
        problems.append(_p('L07', 'error', None,
                           f'花括号不配平：缺少 {depth} 个 }}',
                           '从最后编辑处向前核对 {{ }} 配对'))
    elif first_neg:
        problems.append(_p('L07', 'error', first_neg,
                           '出现多余的 }',
                           '检查是否误删了对应的 {'))

    return problems


def lint_tex_file(tex_path: Path) -> list:
    text = Path(tex_path).read_text(encoding='utf-8', errors='replace')
    return lint_tex(text, tex_dir=Path(tex_path).parent)
