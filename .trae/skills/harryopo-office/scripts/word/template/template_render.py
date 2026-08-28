# -*- coding: utf-8 -*-
r"""
template_render.py — data.json → 保真 .docx（docxtpl 渲染器）

用法（通常经 docx_template.py 调用）：
    python template_render.py template.docx -d data.json -o output.docx [--check]

data.json 结构与 schema.json 对应（见 schema_extractor.py 输出的 fields 树）。

图片字段约定：
    data.json 中某字段值为字典 {"image": "path.png", "width_mm": 30, "height_mm": 20}
    → 渲染时自动转为 docxtpl InlineImage（width/height 可选，缺省按原图比例）。

校验（--check）：
    对照 schema.json 检查 data.json：
      - 必填字段缺失 → 报错
      - 类型不符（array/object/string）→ 报错
    校验失败可加 --force 仍渲染（占位符将原样留在文档中，便于排查）。
"""

import argparse
import json
import re
import sys
from pathlib import Path

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm


# ------------------------------------------------------------
# data.json 校验（对照 schema.json）
# ------------------------------------------------------------

def _check_value(field_name, spec, value, errors, path=''):
    """递归校验单个字段值"""
    ftype = spec.get('type', 'string')
    cur = f"{path}.{field_name}" if path else field_name

    if value is None or value == '':
        if spec.get('required', True):
            errors.append(f"缺失必填字段: {cur}")
        return

    if ftype == 'array':
        if not isinstance(value, list):
            errors.append(f"字段 {cur} 应为数组，实际: {type(value).__name__}")
            return
        item_spec = spec.get('item', {'type': 'string'})
        for i, item in enumerate(value):
            if item_spec.get('type') == 'object':
                for f, fs in item_spec.get('fields', {}).items():
                    _check_value(f, fs, item.get(f), errors, f"{cur}[{i}]")
            elif not isinstance(item, (str, int, float)):
                errors.append(f"字段 {cur}[{i}] 应为标量")

    elif ftype == 'object':
        if not isinstance(value, dict):
            errors.append(f"字段 {cur} 应为对象，实际: {type(value).__name__}")
            return
        for f, fs in spec.get('fields', {}).items():
            _check_value(f, fs, value.get(f), errors, cur)
        # 对象字段是图片（{image: path}）也允许
        if 'image' in value and not isinstance(value.get('image'), str):
            errors.append(f"字段 {cur}.image 应为字符串路径")

    else:  # string
        if isinstance(value, dict) and 'image' in value:
            # 图片字段（{"image": path, "width_mm":…}）
            if not isinstance(value.get('image'), str):
                errors.append(f"字段 {cur}.image 应为字符串路径")
        elif isinstance(value, (dict, list)):
            errors.append(f"字段 {cur} 应为字符串，实际: {type(value).__name__}")


def validate_data(data, schema, strict=True):
    """返回错误列表；strict=False 时只报必填缺失"""
    errors = []
    fields = schema.get('fields', {})
    for name, spec in fields.items():
        if name in data:
            _check_value(name, spec, data[name], errors)
        elif spec.get('required', True):
            errors.append(f"缺失必填字段: {name}")
    return errors


# ------------------------------------------------------------
# 图片字段 → InlineImage
# ------------------------------------------------------------

IMAGE_SPEC_RE = re.compile(
    r'^\s*\{\s*"image"\s*:\s*"?([^",}]+)"?\s*(?:,.*?)?\}\s*$', re.S)


def _build_context(data, template):
    """
    将 data dict 转为 docxtpl context：
      - 图片 dict（{"image": path, "width_mm":…}）→ InlineImage
      - 递归处理数组/对象
    """
    if isinstance(data, dict):
        ctx = {}
        for k, v in data.items():
            if (isinstance(v, dict) and 'image' in v):
                img_path = v['image']
                width = v.get('width_mm')
                height = v.get('height_mm')
                try:
                    if width and height:
                        img = InlineImage(template, img_path,
                                          width=Mm(width), height=Mm(height))
                    elif width:
                        img = InlineImage(template, img_path, width=Mm(width))
                    else:
                        img = InlineImage(template, img_path)
                except Exception as e:
                    print(f'  [!] 图片加载失败 {img_path}: {e}')
                    img = f'[图片缺失: {img_path}]'
                ctx[k] = img
            else:
                ctx[k] = _build_context(v, template)
        return ctx
    if isinstance(data, list):
        return [_build_context(item, template) for item in data]
    return data


# ------------------------------------------------------------
# 渲染
# ------------------------------------------------------------

def render(template_path, data_path, output_path=None, check=False,
           schema_path=None, force=False):
    """主入口：data.json → 渲染 .docx"""
    template_path = Path(template_path)
    data_path = Path(data_path)
    output_path = Path(output_path) if output_path else \
        template_path.with_name(f"{template_path.stem}_filled.docx")

    data = json.loads(data_path.read_text(encoding='utf-8'))

    # ---- 校验 ----
    if check:
        schema = None
        if schema_path:
            schema = json.loads(Path(schema_path).read_text(encoding='utf-8'))
        elif template_path.with_suffix('.schema.json').exists():
            schema = json.loads(
                template_path.with_suffix('.schema.json').read_text(encoding='utf-8'))
        if schema:
            errors = validate_data(data, schema)
            if errors:
                print('== data.json 校验未通过 ==')
                for e in errors:
                    print(f'  ✗ {e}')
                if not force:
                    sys.exit(1)
                print('  (--force 已指定，继续渲染，缺失占位符将保留)')
            else:
                print(f'== 校验通过：{len(data)} 个字段 ==')

    # ---- 渲染 ----
    print(f'加载模板: {template_path}')
    tpl = DocxTemplate(str(template_path))
    context = _build_context(data, tpl)
    tpl.render(context)
    tpl.save(str(output_path))
    print(f'已生成: {output_path}')
    return str(output_path)


def main():
    ap = argparse.ArgumentParser(description='docxtpl 渲染：data.json → .docx')
    ap.add_argument('template', help='模板 .docx 路径')
    ap.add_argument('-d', '--data', required=True, help='data.json 填充数据')
    ap.add_argument('-o', '--output', default=None, help='输出 .docx 路径')
    ap.add_argument('--check', action='store_true',
                    help='渲染前对照 schema 校验 data.json')
    ap.add_argument('-s', '--schema', default=None, help='schema.json 路径（默认模板同名）')
    ap.add_argument('--force', action='store_true', help='校验失败仍渲染')
    args = ap.parse_args()
    render(args.template, args.data, args.output, args.check,
           args.schema, args.force)


if __name__ == '__main__':
    main()
