#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
text_norm.py — 中文文本规范化（标点全角化 + 空格清理）

目的：AI 产出的 Markdown 中间态常带"AI 味"——英文标点（"..." / , : ; ? ! ( )）
与中英文之间的半角空格。本模块在渲染引擎入口统一清洗（护栏层），
配合 SKILL.md 的输出约束（约束层）构成双保险（呼应 8/31 ASCII 字符画
"约束+护栏"双保险经验）。

处理规则：
  1. 标点全角化（仅 CJK 上下文，ASCII 语境不动）：
     - `,` `:` `;` `?` `!` 前邻 CJK → ，：；？！
       （`10:30`、`1,000` 等数字语境不转换）
     - `(` 后邻 CJK → （ ；`)` 前邻 CJK → ）
       （`式(1)`、`f(x)` 等英文/数字语境不转换）
     - 直双引号 `"`：段落含 CJK 时按开闭顺序配对转 “ ”
     - 直单引号 `'`：仅与 CJK 相邻时转 ‘ ’（不动 don't 等英文所有格/缩写）
  2. 空格清理：任一侧为 CJK/全角标点的半角空格一律删除
     （含中文-英文、中文-数字之间；公文排版风格，用户 2026-09-02 决策）
  3. 保护范围（不处理）：
     - 围栏代码块（``` / ~~~ 整块跳过，mermaid 等图表块自然受保护）
     - 多行公式块（$$ 单独成行的块）与行内公式 $...$ / $$...$$
     - 行内代码 `...`
     - URL（markdown 链接/图片的 ](url) 与裸 http(s)://）
     - 行首缩进与 markdown 结构标记（# > - * + 1. 等）

用法：
    from text_norm import normalize_markdown
    md_text = normalize_markdown(md_text)
"""

import re

# CJK 汉字（含扩展 A / 兼容表意区）
_CJK = '\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff'
# 中文侧字符类 = CJK 汉字 + 全角标点/符号（，。：；？！（）《》""''、—…·【】等）
_CJK_CLS = (_CJK + '\u3000-\u303f\uff00-\uffef'
            '\u2018\u2019\u201c\u201d\u2014\u2026\u00b7')

_CJK_RE = re.compile('[' + _CJK + ']')
_CJK_CLS_RE = re.compile('[' + _CJK_CLS + ']')

# 围栏代码块标记
_FENCE_RE = re.compile(r'^\s*(```|~~~)')
# 多行公式块（$$ 单独成行）
_MATH_FENCE_RE = re.compile(r'^\s*\$\$\s*$')
# 行首结构标记（缩进 + 标题/引用/列表/有序列表标记，整体保护不参与清洗）
_LEADING_MARK_RE = re.compile(r'^(\s*(?:#{1,6}\s+|>\s?|[-*+]\s+|\d{1,3}[.)]\s+))')
# 行内保护片段：行内代码 / 行内公式 / markdown URL 部分 ](...) / 裸 URL
_INLINE_PROTECT_RE = re.compile(
    r'(`[^`\n]+`)'
    r'|(\$\$[^$]+\$\$|\$[^$\n]+\$)'
    r'|(\]\([^)]*\))'  # ]( 含空格路径也保护，避免路径内空格被删
    r'|(https?://[^\s)）\u3001\u3002，。]+)'
)

_PLACEHOLDER = '\x00{}\x00'


def _has_cjk(s: str) -> bool:
    return bool(_CJK_RE.search(s))


def _convert_punct(seg: str) -> str:
    """标点全角化（仅 CJK 上下文）+ 双引号配对 + 单引号 CJK 邻接转换"""
    res = []
    n = len(seg)
    open_dq = True  # 直双引号配对状态
    for i, ch in enumerate(seg):
        if ch == '"' and _has_cjk(seg):
            res.append('\u201c' if open_dq else '\u201d')
            open_dq = not open_dq
            continue
        if ch == "'" :
            prev = seg[i - 1] if i > 0 else ''
            nxt = seg[i + 1] if i < n - 1 else ''
            if nxt and _CJK_CLS_RE.match(nxt):
                res.append('\u2018')  # 后邻 CJK → 前引号
                continue
            if prev and _CJK_CLS_RE.match(prev):
                res.append('\u2019')  # 前邻 CJK → 后引号
                continue
            res.append(ch)
            continue
        prev = seg[i - 1] if i > 0 else ''
        nxt = seg[i + 1] if i < n - 1 else ''
        prev_cjk = bool(prev) and bool(_CJK_CLS_RE.match(prev))
        next_cjk = bool(nxt) and bool(_CJK_CLS_RE.match(nxt))
        if ch == ',' and prev_cjk:
            res.append('\uff0c')
        elif ch == ':' and prev_cjk:
            res.append('\uff1a')
        elif ch == ';' and prev_cjk:
            res.append('\uff1b')
        elif ch == '?' and prev_cjk:
            res.append('\uff1f')
        elif ch == '!' and prev_cjk:
            res.append('\uff01')
        elif ch == '(' and next_cjk:
            res.append('\uff08')
        elif ch == ')' and prev_cjk:
            res.append('\uff09')
        else:
            res.append(ch)
    return ''.join(res)


def _strip_cjk_spaces(s: str) -> str:
    """删除任一侧为中文侧字符（CJK/全角标点）的半角空格（收敛到不动点）"""
    prev = None
    while prev != s:
        prev = s
        s = re.sub('(?<=[' + _CJK_CLS + ']) +', '', s)
        s = re.sub(' +(?=[' + _CJK_CLS + '])', '', s)
    return s


def _normalize_line(line: str) -> str:
    """单行规范化：保护行首结构标记与行内片段，清洗其余部分"""
    m = _LEADING_MARK_RE.match(line)
    prefix, rest = ('', line)
    if m:
        prefix, rest = m.group(1), line[m.end():]

    # 保护行内片段（代码/公式/URL），占位符不参与清洗
    parts = []

    def _save(mo: 're.Match') -> str:
        parts.append(mo.group(0))
        return _PLACEHOLDER.format(len(parts) - 1)

    rest = _INLINE_PROTECT_RE.sub(_save, rest)
    rest = _convert_punct(rest)
    rest = _strip_cjk_spaces(rest)
    rest = re.sub(
        '\x00(\\d+)\x00',
        lambda mo: parts[int(mo.group(1))],
        rest,
    )
    return prefix + rest


def normalize_markdown(md_text: str) -> str:
    """Markdown 全文规范化入口（Word / LaTeX 两个渲染引擎共用）"""
    out = []
    in_fence = False
    fence_mark = ''
    in_math_block = False
    for line in md_text.split('\n'):
        fm = _FENCE_RE.match(line)
        if fm:
            mark = fm.group(1)[:3]
            if not in_fence:
                in_fence, fence_mark = True, mark
            elif mark == fence_mark:
                in_fence = False
            out.append(line)
            continue
        if not in_fence and _MATH_FENCE_RE.match(line):
            # $$ 单独成行：切换多行公式块状态，块内不清洗
            in_math_block = not in_math_block
            out.append(line)
            continue
        if in_fence or in_math_block:
            out.append(line)
            continue
        out.append(_normalize_line(line))
    return '\n'.join(out)
