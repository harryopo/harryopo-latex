#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
blindcheck — 盲审版个人信息隐匿检查
====================================

扫描 .tex/.md（可递归目录），找出**盲审版不应出现**的身份暴露点：
作者/单位元信息、学号工号、个人邮箱、手机号、致谢/基金章节、指导教师、
绝对路径中的用户名。输出发现清单（文件:行 + 类别 + 脱敏预览 + 整改建议）。

设计参照 latex-thesis-zh（bahayonghang）的"盲审隐匿"能力；规则内置默认集，
不做配置文件（ false positive 靠人工复核，本工具只负责"找出来"）。

用法：
  python blindcheck.py 论文.tex
  python blindcheck.py chapters/            # 目录递归
  python blindcheck 论文.tex --json         # AI 消费
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── 检查规则（顺序即报告顺序）──
# 每条: (类别, 编译正则, 建议)
RULES = [
    ('作者元信息', r'\\author\{[^}]*[^\s{}][^}]*\}',
     '盲审版作者应匿名：\\author{} 留空或按学校盲审模板处理'),
    ('单位元信息', r'\\institute\{[^}]*[^\s{}][^}]*\}',
     '盲审版单位应匿名：\\institute{} 留空'),
    ('作者元信息(MD)', r'(?m)^>\s*(?:作者|姓名)\s*[：:]\s*\S+',
     'MD 中间态的作者 blockquote 在盲审版应删除或留空'),
    ('单位元信息(MD)', r'(?m)^>\s*(?:单位|学校|学院)\s*[：:]\s*\S+',
     'MD 中间态的单位 blockquote 在盲审版应删除或留空'),
    ('学号/工号', r'(?<!\d)(?:学号|工号|No\.?|ID)\s*[：:]?\s*\d{6,12}(?!\d)',
     '删除学号/工号或以"****"替代'),
    ('疑似学号(纯数字)', r'(?<![\d.])2[0-9]{7,10}(?![\d.])',
     '连续数字疑似学号——确认是否为年份/数值，是则忽略，否则隐匿'),
    ('个人邮箱', r'[A-Za-z0-9._%+-]+@(?:qq|163|126|gmail|outlook|hotmail|foxmail)\.(?:com|net)',
     '个人邮箱应删除或换机构匿名邮箱'),
    ('手机号', r'(?<!\d)1[3-9]\d{9}(?!\d)',
     '手机号应删除'),
    ('致谢章节', r'\\(?:section|chapter)\*?\{[^}]*(?:致谢|鸣谢|acknowledg)',
     '盲审版通常整章删除致谢（含导师/基金信息）'),
    ('基金项目', r'(?:基金|资助|funded|grant)\s*[：:]|\\thanks\{',
     '基金项目信息可反推团队身份——按学校盲审要求删除或匿名化'),
    ('指导教师', r'(?:指导教师|导师|supervisor|advisor)\s*[：:]?\s*[\u4e00-\u9fa5A-Za-z]{2,4}',
     '删除导师姓名（正文提及与封面均算）'),
    ('用户名路径', r'[A-Za-z]:[\\/]+Users[\\/]+[^\\/ \]]{2,20}',
     '绝对路径含本机用户名——改用相对路径（\\\\input/图片引用）'),
]

_TEX_SUFFIXES = {'.tex', '.md', '.markdown'}
_SKIP_DIRS = {'.git', '__pycache__', 'node_modules', 'opensource-reference',
              '.trae', '.mimosa', 'output', '简历'}


def _redact(text: str, keep: int = 2) -> str:
    """预览脱敏：保留首尾 keep 字符，中间以 *** 替代。"""
    text = ' '.join(text.split())
    if len(text) <= keep * 2 + 3:
        return text
    return f'{text[:keep]}***{text[-keep:]}'


def scan_text(text: str) -> list:
    """扫描单文件文本，返回 [{category, line, preview, suggestion}]。"""
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for cat, pat, fix in RULES:
            for m in re.finditer(pat, line):
                findings.append({
                    'category': cat,
                    'line': lineno,
                    'preview': _redact(m.group(0)),
                    'suggestion': fix,
                })
    return findings


def iter_files(target: Path):
    if target.is_file():
        if target.suffix.lower() in _TEX_SUFFIXES:
            yield target
        return
    for p in sorted(target.rglob('*')):
        if p.suffix.lower() in _TEX_SUFFIXES and not any(
                part in _SKIP_DIRS for part in p.parts):
            yield p


def main() -> int:
    ap = argparse.ArgumentParser(
        description='盲审版个人信息隐匿检查（.tex/.md，目录递归）')
    ap.add_argument('target', help='文件或目录')
    ap.add_argument('--json', action='store_true', help='输出 JSON（供 AI 消费）')
    args = ap.parse_args()
    target = Path(args.target)
    if not target.exists():
        print(f'[FATAL] 路径不存在: {target}', file=sys.stderr)
        return 2

    all_findings = []
    files_scanned = 0
    for f in iter_files(target):
        files_scanned += 1
        for item in scan_text(f.read_text(encoding='utf-8', errors='replace')):
            item['file'] = str(f)
            all_findings.append(item)

    if args.json:
        print(json.dumps({'target': str(target), 'files_scanned': files_scanned,
                          'finding_count': len(all_findings),
                          'findings': all_findings},
                         ensure_ascii=False, indent=2))
        return 0 if not all_findings else 1

    if not all_findings:
        print(f'[OK] 扫描 {files_scanned} 个文件，未发现身份暴露点')
        return 0

    print(f'=== 盲审隐匿检查: {target} （{files_scanned} 个文件，'
          f'{len(all_findings)} 处发现）===')
    cur = None
    for it in all_findings:
        if it['file'] != cur:
            cur = it['file']
            print(f'-- {cur}')
        print(f"  [行{it['line']:>4}] {it['category']}: {it['preview']}"
              f"  → {it['suggestion']}")
    print(f'--- 共 {len(all_findings)} 处；盲审前逐条整改后复扫 ---')
    return 1


if __name__ == '__main__':
    sys.exit(main())
