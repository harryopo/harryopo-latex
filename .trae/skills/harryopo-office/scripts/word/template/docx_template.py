# -*- coding: utf-8 -*-
r"""
docx_template.py — docxtpl 模板填充子 skill 主入口

工作流（AI 按模板出文档，中间态 JSON 可编辑）：
    1. 用户提供设计好的 Word 模板 template.docx（含 Jinja2 占位符）
    2. extract：扫描模板占位符 → 自动生成 schema.json（字段清单 + 类型推断）
    3. AI 阅读 schema.json → 向用户确认字段含义 → 产出 data.json
    4. 用户可编辑 data.json
    5. render：data.json → 保真填充输出 .docx（格式 100% 保留模板）

用法：
    # 提取 schema（模板 → 字段清单）
    python docx_template.py extract template.docx -o schema.json

    # 校验 data（对照 schema）
    python docx_template.py validate data.json -s schema.json

    # 渲染（data → docx，可选 --check 先校验）
    python docx_template.py render template.docx -d data.json -o out.docx --check

    不带子命令时默认执行 extract。

模板占位符语法（用户用 Word 编辑模板时插入）：
    {{ project_name }}                    变量（正文/表格单元格直接写）
    {%tr for task in tasks %}...{%tr endfor %}   表格行循环
    {%tc for c in cols %}...{%tc endfor %}       表格列循环
    {%p if show %}...{%p endif %}               段落级条件
    {% if var %}...{% endif %}                  行内条件
    {% hm %} / {% vm %} ... {% endvm %}         水平/垂直合并单元格
    {{ myimage }} + data 中 {"image": "a.png", "width_mm": 30}   图片

注意：占位符在 Word 中必须保持连续、不要加粗/改色（避免被拆成多个 run）。
"""

import argparse
import json
import sys
from pathlib import Path

from schema_extractor import extract_schema
from template_render import render as do_render, validate_data


def cmd_extract(args):
    schema = extract_schema(args.template)
    out = Path(args.output) if args.output else \
        Path(args.template).with_suffix('.schema.json')
    out.write_text(json.dumps(schema, ensure_ascii=False, indent=2),
                   encoding='utf-8')
    print(f'模板: {args.template}')
    print(f'提取到 {len(schema["fields"])} 个字段:')
    for name, spec in schema['fields'].items():
        t = spec['type']
        req = '必填' if spec.get('required', True) else '可选'
        if t == 'object':
            detail = f'({len(spec.get("fields", {}))} 个字段)'
        elif t == 'array':
            it = spec.get('item', {})
            detail = f'(元素 {it.get("type", "?")})'
        else:
            detail = ''
        print(f'  - {name} [{t}/{req}]{detail}')
    print(f'\nschema 已保存: {out}')


def cmd_validate(args):
    data = json.loads(Path(args.data).read_text(encoding='utf-8'))
    schema = json.loads(Path(args.schema).read_text(encoding='utf-8'))
    errors = validate_data(data, schema)
    if errors:
        print('== 校验未通过 ==')
        for e in errors:
            print(f'  ✗ {e}')
        sys.exit(1)
    print('== 校验通过 ==')
    fields = schema.get('fields', {})
    for name in data:
        if name in fields:
            t = fields[name]['type']
            print(f'  ✓ {name} [{t}]')


def cmd_render(args):
    out = do_render(args.template, args.data, args.output,
                    args.check, args.schema, args.force)
    print(f'完成: {out}')


def main():
    ap = argparse.ArgumentParser(
        description='docxtpl 模板填充：extract(schema) / validate / render',
        prog='docx_template.py')
    sub = ap.add_subparsers(dest='cmd')

    p_extract = sub.add_parser('extract', help='模板 → schema.json')
    p_extract.add_argument('template', help='模板 .docx')
    p_extract.add_argument('-o', '--output', default=None, help='schema.json 输出')
    p_extract.set_defaults(func=cmd_extract)

    p_validate = sub.add_parser('validate', help='校验 data.json 对照 schema')
    p_validate.add_argument('data', help='data.json')
    p_validate.add_argument('-s', '--schema', required=True, help='schema.json')
    p_validate.set_defaults(func=cmd_validate)

    p_render = sub.add_parser('render', help='data.json → .docx')
    p_render.add_argument('template', help='模板 .docx')
    p_render.add_argument('-d', '--data', required=True, help='data.json')
    p_render.add_argument('-o', '--output', default=None, help='输出 .docx')
    p_render.add_argument('--check', action='store_true', help='渲染前校验')
    p_render.add_argument('-s', '--schema', default=None, help='schema.json')
    p_render.add_argument('--force', action='store_true', help='校验失败仍渲染')
    p_render.set_defaults(func=cmd_render)

    args = ap.parse_args()
    if not args.cmd:
        # 默认 extract
        p_extract.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == '__main__':
    main()
