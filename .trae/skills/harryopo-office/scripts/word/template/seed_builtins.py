# -*- coding: utf-8 -*-
r"""
seed_builtins.py — 注册表内置模板初始化（幂等，可重复运行）

将 harryopo 平台内置模板一次性写入注册表（source=builtin，category=全局）：
    1. harryopo-paper   LaTeX 论文模板（showcase-paper.tex）
    2. harryopo-report  LaTeX 报告模板（showcase-report.tex）
    3. harryopo-notes   LaTeX 数理笔记模板（math-notes，独立体系）
    4. docxtpl-example  Word 模板填充示例（template.docx，自动提取 schema）

用法:
    python seed_builtins.py            # 入库（存在则跳过）
    python seed_builtins.py --force    # 强制覆盖重建
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from template_registry import register_template, load_manifest


def _find_project_root():
    """向上找含 templates/cls 的项目根（跳过 .trae 内副本，同 office.py 铁律）"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if '.trae' in parent.parts:
            continue
        if (parent / 'templates' / 'cls').exists():
            return parent
    return None


_ROOT = _find_project_root()
_HERE = Path(__file__).parent.resolve()

# (模板源文件, id, 显示名, 版本, 标签)
BUILTINS = [
    (str(_ROOT / 'templates' / 'paper' / 'showcase-paper.tex') if _ROOT else '',
     'harryopo-paper', 'harryopo 论文模板', '4.0', ['学术', '论文']),
    (str(_ROOT / 'templates' / 'report' / 'showcase-report.tex') if _ROOT else '',
     'harryopo-report', 'harryopo 报告模板', '4.0', ['学术', '报告']),
    (str(_ROOT / 'templates' / 'math-notes' / 'example-note.tex') if _ROOT else '',
     'harryopo-notes', 'harryopo 数理笔记模板', '1.0', ['笔记', '数学']),
    (str(_HERE / 'examples' / 'template.docx'),
     'docxtpl-example', 'docxtpl 模板填充示例', '1.0', ['示例', 'docx']),
]


def main():
    force = '--force' in sys.argv
    manifest = load_manifest()
    for src, tid, name, ver, tags in BUILTINS:
        path = Path(src)
        if not path.exists():
            print(f'[SKIP] 源文件不存在: {src}')
            continue
        # 已存在且非 force → 跳过（幂等）
        if any(t['id'] == tid for t in manifest['templates']) and not force:
            print(f'[SKIP] 已存在: {tid}（--force 重建）')
            continue
        entry = register_template(
            str(path), category='全局', name=name, template_id=tid,
            version=ver, tags=tags, source='builtin', force=force)
        print(f'[OK]   {tid}  format={entry["format"]}  '
              f'schema={entry["schema_ref"] or "(M2)"}')


if __name__ == '__main__':
    main()
