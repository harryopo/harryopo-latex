#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harryopo-build-mcp — LaTeX 编译诊断闭环 MCP 服务
================================================

将 harryopo 的 LaTeX 编译能力包装为 MCP 工具，让 AI 获得
"编译 → 结构化诊断（错误码+行号+修复建议）→ 修复 → 重编译"的自愈闭环：

  - harryopo_build(tex_file)         3 遍 XeLaTeX 编译，返回页数/错误/警告/修复建议
  - harryopo_diagnostics(tex_file)   解析既有编译日志（不重新编译）
  - harryopo_lint(tex_file)          编译前静态预检（7 项：环境配平/$配对/表格列/悬空引用/
                                     重复label/图片存在/括号配平）

运行：python build_mcp.py            （stdio 传输，由 MCP 客户端拉起）
依赖：pip install mcp（2.x）；诊断库 latex_diagnostics.py 与本文件同目录。

范式红线：MCP 只提供"能力"，不做"决策"——何时编译、如何改稿由调用方 AI 判断。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from latex_diagnostics import lint_tex_file, parse_log  # noqa: E402

# 路径与 PATH 探测复用 office.py（单一事实来源：项目根 templates/cls|fonts|paper）
from office import CLS_DIR, FONTS_DIR, PAPER_DIR, _ensure_tex_on_path  # noqa: E402

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer('harryopo-build')


def _compile(tex_file: Path, passes: int) -> dict:
    """编译 .tex 为 PDF。

    harryopo-base.sty 的字体声明用 `Path=../fonts/`（相对编译目录），因此**编译目录
    必须是 templates/ 的子目录**（与 office.py render_paper 同约定）：把 tex 拷入
    项目根 templates/paper/（连同 figures/），编译后产物拷回原目录。
    """
    _ensure_tex_on_path()
    if not shutil.which('xelatex'):
        return {'success': False, 'error': '未找到 xelatex（TinyTeX/MiKTeX/TeX Live 均未探测到）'}
    work = PAPER_DIR / f'{tex_file.stem}-mcp.tex'
    shutil.copyfile(tex_file, work)
    src_figs = tex_file.parent / 'figures'
    if src_figs.exists():
        dst_figs = PAPER_DIR / 'figures'
        dst_figs.mkdir(exist_ok=True)
        for f in src_figs.glob('*.png'):
            shutil.copyfile(f, dst_figs / f.name)

    texinputs = f'{CLS_DIR}//;{FONTS_DIR}//;'
    env = {**os.environ, 'TEXINPUTS': texinputs}
    last_log = ''
    for i in range(max(1, passes)):
        proc = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', work.name],
            cwd=str(PAPER_DIR), env=env, capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=600)
        log_file = work.with_suffix('.log')
        if log_file.exists():
            last_log = log_file.read_text(encoding='utf-8', errors='replace')
        if proc.returncode == 0 and last_log and 'Output written' in last_log:
            break

    # 产物拷回原目录（PDF/log/aux）
    pdf = work.with_suffix('.pdf')
    pdf_out = None
    if pdf.exists() and pdf.stat().st_size > 5000:
        dest = tex_file.parent / pdf.name
        shutil.copyfile(pdf, dest)
        pdf_out = str(dest)
    dest_log = tex_file.parent / f'{tex_file.stem}.log'
    work.with_suffix('.log').exists() and shutil.copyfile(work.with_suffix('.log'), dest_log)

    parsed = parse_log(last_log) if last_log else {
        'success': False, 'pages': None, 'errors': [], 'warnings': [], 'overfull': []}
    parsed['pdf'] = pdf_out
    parsed['tex'] = str(tex_file)
    return parsed


@server.tool()
def harryopo_build(tex_file: str, passes: int = 3) -> dict:
    """编译 .tex 为 PDF（XeLaTeX ×N 遍 + harryopo 模板 TEXINPUTS），返回结构化诊断。

    Args:
        tex_file: .tex 文件路径（编译产物生成在同目录）
        passes:   xelatex 编译遍数（默认 3，保证交叉引用/目录稳定）
    """
    tex = Path(tex_file).resolve()
    if not tex.exists():
        return {'success': False, 'error': f'文件不存在: {tex}'}
    if tex.suffix != '.tex':
        return {'success': False, 'error': f'仅支持 .tex，收到 {tex.suffix}'}
    result = _compile(tex, passes)
    # 顶部诊断摘要：错误最多展示 8 条，全部带行号与修复建议
    result['errors'] = result.get('errors', [])[:8]
    return result


@server.tool()
def harryopo_diagnostics(tex_file: str) -> dict:
    """解析既有编译日志（不重新编译），返回错误/警告/Overfull 与修复建议。

    Args:
        tex_file: .tex 或 .log 路径（.tex 时自动查找同名 .log）
    """
    p = Path(tex_file).resolve()
    if p.suffix == '.log':
        log = p
    else:
        log = p.with_suffix('.log')
    if not log.exists():
        return {'success': False, 'error': f'未找到编译日志: {log}（先 build 再诊断）'}
    parsed = parse_log(log.read_text(encoding='utf-8', errors='replace'))
    parsed['log'] = str(log)
    parsed['errors'] = parsed.get('errors', [])[:20]
    return parsed


@server.tool()
def harryopo_lint(tex_file: str) -> dict:
    """编译前 .tex 静态预检（7 项）：环境配平/数学$配对/表格列数/悬空引用/
    重复label/图片存在/花括号配平。返回 Problem 列表（code/line/message/suggestion）。

    Args:
        tex_file: .tex 文件路径
    """
    tex = Path(tex_file).resolve()
    if not tex.exists():
        return {'success': False, 'error': f'文件不存在: {tex}'}
    problems = lint_tex_file(tex)
    return {'success': not problems, 'tex': str(tex),
            'problem_count': len(problems), 'problems': problems}


if __name__ == '__main__':
    server.run(transport='stdio')
