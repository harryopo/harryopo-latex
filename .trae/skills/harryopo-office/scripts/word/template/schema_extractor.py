# -*- coding: utf-8 -*-
r"""
schema_extractor.py — 从 .docx 模板提取占位符 → 自动生成 JSON Schema

核心思想：
    用户用 Word 设计好模板（所见即所得），插入 Jinja2 风格占位符
    （{{ var }}、{% for %}、{% if %}），本模块扫描模板 XML 文本，
    提取所有变量并按 jinja2 作用域推断类型（string / object / array），
    输出可编辑的 schema.json —— AI 依据它产出 data.json 填充内容。

用法（通常经 docx_template.py 调用）：
    python schema_extractor.py template.docx -o schema.json

模板占位符约定（与 docxtpl 一致）：
    {{ var }}                  普通变量 → string
    {{ obj.field }}            对象字段 → obj 为 object
    {% for x in items %}...{% endfor %}   items → array，x 为元素
    {% if var %}...{% endif %}  var 为可选字段（required=false）
    {%tr / %tc / %p / %r %}    docxtpl 段落/表格行/列/run 标签（透传忽略）
    {% hm %} / {% vm %}        水平/垂直合并单元格（透传忽略）
    {%- raw -%}...{%- endraw -%}  不参与 schema 提取（原样输出）

生成 schema.json 结构：
    {
      "schema_version": "1.0",
      "template": "xxx.docx",
      "generated_at": "2026-08-09",
      "fields": {
        "project_name": {"type": "string", "required": true, "description": ""},
        "owner": {"type": "object", "required": true, "fields": {
            "name": {"type": "string", "required": true, "description": ""}}},
        "tasks": {"type": "array", "required": true, "item": {
            "type": "object", "fields": {...}}}
      }
    }
"""

import argparse
import json
import re
import zipfile
from pathlib import Path

# ------------------------------------------------------------
# 1. 提取 docx 全部 XML 文本节点
# ------------------------------------------------------------

VAR_RE = re.compile(r'\{\{([^}]+?)\}\}')
# 支持 docxtpl 标签前缀（{%tr / {%p / {%tc / {%r），如 {%tr for x in y %}
STMT_RE = re.compile(
    r'\{%[-+]?\s*(?:(?:tr|tc|p|r)\s+)?(for|if|endif|endfor|else|set)\b([^%]*?)\s*[-+]?%\}')

# jinja2 内建变量（不参与 schema）
BUILTINS = {'loop', 'range', 'dict', 'none', 'true', 'false', 'self',
            'namespace', 'cycler', 'joiner', 'lipsum', 'grouper'}

# 需要扫描的 docx 部件（正文 + 页眉页脚 + 脚注）
PARTS = (
    'word/document.xml',
    'word/header1.xml', 'word/header2.xml', 'word/header3.xml',
    'word/footer1.xml', 'word/footer2.xml', 'word/footer3.xml',
    'word/footnotes.xml',
)


def collect_texts(docx_path):
    """读取 docx 各部件中所有 <w:t> 文本节点，返回 (部件名, 文本) 列表"""
    texts = []
    with zipfile.ZipFile(docx_path) as z:
        names = set(z.namelist())
        for part in PARTS:
            if part not in names:
                continue
            xml = z.read(part).decode('utf-8')
            # 提取所有 w:t 文本节点内容
            for m in re.finditer(r'<w:t[^>]*>(.*?)</w:t>', xml, re.S):
                # 还原 XML 转义
                txt = (m.group(1)
                       .replace('&amp;', '&').replace('&lt;', '<')
                       .replace('&gt;', '>').replace('&quot;', '"')
                       .replace('&apos;', "'"))
                if txt.strip():
                    texts.append((part, txt))
    return texts


# ------------------------------------------------------------
# 2. jinja2 作用域解析 → 变量类型推断
# ------------------------------------------------------------

def parse_statements(texts):
    """
    遍历所有文本节点，模拟 jinja2 作用域栈，返回：
        variables: {var_name: type_hint}
        loops:     [{var: 循环元素名, iterable: 列表变量名, scope: (start,end)}]
        conditionals: [变量名列表]（出现在 if 条件中）
    """
    # 把所有文本拼接成带部件边界的流，便于顺序分析
    # 但 for/endfor 可能跨单元格/段落（{%tr %} 表格行场景），故全局拼接
    stream = '\n'.join(t for _, t in texts)

    variables = {}   # name -> 'plain'（默认 string）
    loops = []       # 循环记录
    cond_vars = set()  # if 条件中出现过的变量

    # ---- 收集所有 {{ }} 变量 ----
    for m in VAR_RE.finditer(stream):
        expr = m.group(1).strip()
        # 去掉过滤器（| default(...) 等）
        expr = expr.split('|')[0].strip()
        if not expr:
            continue
        # 变量名（去掉下标/点访问的基名）
        base = expr.split('.')[0].strip()
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', base):
            continue
        if base in BUILTINS:
            continue
        variables[base] = variables.get(base, 'plain')

    # ---- 收集 {% %} 语句并构建作用域栈 ----
    stmts = list(STMT_RE.finditer(stream))
    stack = []  # (kind, var, iterable, start_pos)
    i = 0
    for m in stmts:
        kind, rest = m.group(1), m.group(2).strip()
        if kind == 'for':
            fm = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s+in\s+([A-Za-z_][A-Za-z0-9_\.]*)$', rest)
            if fm:
                var, it = fm.group(1), fm.group(2)
                it_base = it.split('.')[0].strip()
                variables[it_base] = 'list'
                stack.append(('for', var, it_base, m.start()))
        elif kind == 'if':
            # 提取 if 条件中引用的变量
            for v in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', rest):
                if v in ('and', 'or', 'not', 'in', 'is', 'none',
                         'true', 'false') or v in BUILTINS:
                    continue
                cond_vars.add(v)
                # 条件变量也登记（组装时 required=false）
                variables.setdefault(v, 'plain')
            stack.append(('if', None, None, m.start()))
        elif kind == 'endfor':
            # 弹出最近的 for
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] == 'for':
                    _, var, it_base, start = stack[idx]
                    loops.append({'var': var, 'iterable': it_base,
                                  'scope': (start, m.end())})
                    del stack[idx]
                    break
        elif kind == 'endif':
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx][0] == 'if':
                    del stack[idx]
                    break
        # else / set 忽略
        i += 1

    # ---- 循环作用域内：循环元素 var.xxx → 元素为 object ----
    for lp in loops:
        var, it_base, (s, e) = lp['var'], lp['iterable'], lp['scope']
        # 循环元素本身可以是 object（var.field 出现时）
        obj_fields = set()
        for m in VAR_RE.finditer(stream):
            if not (s <= m.start() <= e):
                continue
            expr = m.group(1).strip().split('|')[0].strip()
            if expr.startswith(var + '.'):
                fname = expr.split('.', 1)[1].split('.')[0].strip()
                if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', fname):
                    obj_fields.add(fname)
        if obj_fields:
            lp['item_fields'] = obj_fields
        else:
            lp['item_fields'] = set()
        # 循环元素名也登记为变量（标量元素场景）
        variables.setdefault(var, 'plain')

    return variables, loops, cond_vars


# ------------------------------------------------------------
# 3. schema 组装辅助
# ------------------------------------------------------------

def collect_object_fields(texts):
    """
    收集所有 {{ obj.field }} 引用，返回 {obj: {field: ...}}。
    用于构建 object 类型字段（循环元素之外的普通对象）。
    """
    objs = {}
    for _, txt in texts:
        for m in VAR_RE.finditer(txt):
            expr = m.group(1).strip().split('|')[0].strip()
            if '.' in expr:
                base, _, field = expr.partition('.')
                field = field.split('.')[0].strip()
                if (re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', base)
                        and re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', field)
                        and base not in BUILTINS):
                    objs.setdefault(base, set()).add(field)
    return objs


def extract_schema(docx_path):
    """主入口：模板 → schema dict"""
    docx_path = Path(docx_path)
    texts = collect_texts(docx_path)
    variables, loops, cond_vars = parse_statements(texts)
    object_fields = collect_object_fields(texts)

    # 组装 schema
    fields = {}
    for name in sorted(variables.keys()):
        fields[name] = {'type': 'string', 'required': True, 'description': ''}

    # 循环 → array
    for lp in loops:
        var, it = lp['var'], lp['iterable']
        if it in fields:
            fields[it] = {'type': 'array', 'required': True, 'description': ''}
            if lp['item_fields']:
                fields[it]['item'] = {'type': 'object', 'fields': {}}
                for f in sorted(lp['item_fields']):
                    fields[it]['item']['fields'][f] = {
                        'type': 'string', 'required': True, 'description': ''}
            else:
                fields[it]['item'] = {'type': 'string', 'description': ''}

    # 对象字段（非循环元素的 obj.field）→ object
    for base, fset in object_fields.items():
        if base in fields and fields[base]['type'] == 'string':
            fields[base] = {'type': 'object', 'required': True,
                            'description': '', 'fields': {}}
            for f in sorted(fset):
                fields[base]['fields'][f] = {
                    'type': 'string', 'required': True, 'description': ''}
        elif base not in fields:
            fields[base] = {'type': 'object', 'required': True,
                            'description': '', 'fields': {}}
            for f in sorted(fset):
                fields[base]['fields'][f] = {
                    'type': 'string', 'required': True, 'description': ''}

    # 条件变量 → 可选
    for c in cond_vars:
        if c in fields:
            fields[c]['required'] = False

    # 循环元素变量（var）不进顶层——其结构已体现在 array 的 item 中
    for lp in loops:
        fields.pop(lp['var'], None)

    schema = {
        'schema_version': '1.0',
        'template': str(docx_path),
        'generated_at': '',
        'fields': fields,
    }
    return schema


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='从 .docx 模板提取占位符 → JSON Schema')
    ap.add_argument('template', help='模板 .docx 路径')
    ap.add_argument('-o', '--output', default=None, help='schema.json 输出路径（默认同目录）')
    args = ap.parse_args()

    schema = extract_schema(args.template)
    out = Path(args.output) if args.output else Path(args.template).with_suffix('.schema.json')
    out.write_text(json.dumps(schema, ensure_ascii=False, indent=2),
                   encoding='utf-8')

    total = len(schema['fields'])
    print(f'模板: {args.template}')
    print(f'提取到 {total} 个字段:')
    for name, spec in schema['fields'].items():
        t = spec['type']
        req = '必填' if spec.get('required', True) else '可选'
        detail = ''
        if t == 'array':
            it = spec.get('item', {})
            detail = f" 元素={it.get('type', '?')}"
        elif t == 'object':
            detail = f" 字段={len(spec.get('fields', {}))}个"
        print(f'  - {name} [{t}/{req}]{detail}')
    print(f'\nschema 已保存: {out}')


if __name__ == '__main__':
    main()
