# -*- coding: utf-8 -*-
r"""
template_registry.py — 模板注册表 v1（manifest.json）

核心思想（方案书 v2 §7 + 调研报告 2026-08-28-模板注册表v1可行性调研）：
    用户入库模板 → 自动扫描占位符 → 生成 JSON Schema → AI structured output
    受约束产出数据 → 引擎渲染保真输出。注册表是模板的"中央元数据单点"，
    引擎按 id 取 schema，LLM 不直接动模板文件（对齐 arXiv 双轨框架：
    离线 manifest 提取模板约束 + 在线混合管道 LLM 只做语义）。

目录结构（相对项目根 templates/registry/）：
    manifest.json                索引（所有模板条目数组，白名单严格校验）
    word/                        用户 Word 模板库（docxtpl 引擎）
    latex/                       LaTeX 模板库（harryopo 体系 / 用户）
    markdown/                    MD 中间态模板
    html/                        HTML 模板（阶段 3 编辑器用）
    schemas/<id>.schema.json     Word 模板入库时自动生成的 JSON Schema

CLI:
    python template_registry.py add <template> [-c 分类] [-n 名称] [--id ID] [--force]
    python template_registry.py list [-f docx|latex|markdown] [-c 分类] [query]
    python template_registry.py describe <id>
    python template_registry.py schema <id> [-o schema.json]
    python template_registry.py search <query>
    python template_registry.py remove <id> [--force] [-d]   # -d 同时删文件
    python template_registry.py update-usage <id> [--inc 1]  # 使用计数

模板条目字段（白名单，未知字段拒绝加载 —— 对齐 M365 Copilot 严格模式）：
    manifest_version: manifest 版本
    id:               全局唯一（{source前缀}-{name}，如 user-公文模板）
    name:             显示名称
    version:          模板版本
    format:           docx | latex | markdown | html
    category:         全局 | 场景 | 用户自定义
    engine:           docxtpl | md_to_word | harryopo-xelatex | html
    source:           builtin（内置）| user（用户上传）| market（市场，M3）
    template_path:    相对 registry 的模板文件路径
    schema_ref:       相对 registry 的 JSON Schema 路径（空串 = 未生成）
    preview:          预览图路径（M3 自动生成）
    placeholder_syntax: 占位符语法标识（jinja2 / tex-placeholder-v1 / md-convention）
    tags:             标签列表（搜索用）
    usage_count:      使用计数
    created_at / updated_at: 创建/更新时间
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

# ============================================================
# 路径与常量
# ============================================================

SCRIPT_DIR = Path(__file__).parent.resolve()          # .../scripts/word/template/
WORD_DIR = SCRIPT_DIR.parent                          # .../scripts/word/


def _find_project_root():
    """从脚本目录向上查找项目根（包含 templates/cls 且不在 .trae skill 内）"""
    for parent in [SCRIPT_DIR] + list(SCRIPT_DIR.parents):
        # 跳过 skill 目录内的 templates/ 副本（.trae 下），锚定真实项目根
        if (parent / 'templates' / 'cls').exists() and '.trae' not in parent.parts:
            return parent
    return SCRIPT_DIR.parents[3]  # 回退：.../project_root/


PROJECT_ROOT = _find_project_root()
REGISTRY_DIR = PROJECT_ROOT / 'templates' / 'registry'
MANIFEST = REGISTRY_DIR / 'manifest.json'

MANIFEST_VERSION = '1.0'

# 格式 → 引擎 映射
FORMAT_ENGINE = {
    'docx': 'docxtpl',
    'latex': 'harryopo-xelatex',
    'markdown': 'md_to_word',
    'html': 'html',
}

# 白名单字段（严格校验：未知字段 → 拒绝加载并报错定位）
ENTRY_FIELDS = {
    'manifest_version', 'id', 'name', 'version', 'format', 'category',
    'engine', 'source', 'template_path', 'schema_ref', 'preview',
    'placeholder_syntax', 'tags', 'usage_count', 'created_at', 'updated_at',
}
TOP_FIELDS = {'manifest_version', 'templates'}

FORMATS = set(FORMAT_ENGINE)
SOURCES = {'builtin', 'user', 'market'}
CATEGORIES = {'全局', '场景', '用户自定义'}
PLACEHOLDER_SYNTAX = {'jinja2', 'tex-placeholder-v1', 'md-convention', ''}


# ============================================================
# manifest 读写 + 严格校验
# ============================================================

def now_str():
    """当前日期 YYYY-MM-DD"""
    from datetime import date
    return date.today().isoformat()


def load_manifest():
    """读取 manifest.json；不存在则初始化空注册表。严格校验白名单字段。"""
    if not MANIFEST.exists():
        return {'manifest_version': MANIFEST_VERSION, 'templates': []}
    raw = json.loads(MANIFEST.read_text(encoding='utf-8'))

    # 顶层字段白名单校验
    unknown_top = set(raw) - TOP_FIELDS
    if unknown_top:
        raise ValueError(f'manifest 顶层含未知字段: {sorted(unknown_top)}（白名单: {sorted(TOP_FIELDS)}）')

    templates = raw.get('templates', [])
    seen_ids = set()
    for tpl in templates:
        unknown = set(tpl) - ENTRY_FIELDS
        if unknown:
            raise ValueError(
                f'模板条目含未知字段: {sorted(unknown)}（id={tpl.get("id", "?")}）')
        # 枚举合法性
        if tpl.get('format') not in FORMATS:
            raise ValueError(f'模板 {tpl.get("id")} 的 format 非法: {tpl.get("format")}')
        if tpl.get('source') not in SOURCES:
            raise ValueError(f'模板 {tpl.get("id")} 的 source 非法: {tpl.get("source")}')
        # id 唯一性
        tid = tpl.get('id')
        if tid in seen_ids:
            raise ValueError(f'模板 id 重复: {tid}')
        seen_ids.add(tid)
    return {'manifest_version': raw.get('manifest_version', MANIFEST_VERSION),
            'templates': templates}


def save_manifest(manifest):
    """写回 manifest.json（UTF-8、2 空格缩进）"""
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                        encoding='utf-8')


def find_template(manifest, template_id):
    """按 id 查找模板条目，未找到返回 None"""
    for tpl in manifest['templates']:
        if tpl['id'] == template_id:
            return tpl
    return None


# ============================================================
# 入库路由
# ============================================================

def _infer_format(path):
    """由扩展名推断 format"""
    ext = path.suffix.lstrip('.').lower()
    if ext in ('docx', 'doc'):
        return 'docx'
    if ext in ('tex',):
        return 'latex'
    if ext in ('md', 'markdown'):
        return 'markdown'
    if ext in ('html', 'htm'):
        return 'html'
    raise ValueError(f'不支持的模板格式: {ext}（支持 docx/tex/md/html）')


def _slugify(stem):
    """模板名 → 安全 id 片段（保留中文/字母/数字/连字符）"""
    s = re.sub(r'[^\w\u4e00-\u9fff-]', '-', stem, flags=re.UNICODE)
    return s.strip('-') or 'template'


def _copy_to_registry(src, fmt, id_name):
    """复制模板文件到 registry/<fmt>/，返回相对路径"""
    fmt_dir = REGISTRY_DIR / fmt
    fmt_dir.mkdir(parents=True, exist_ok=True)
    dst = fmt_dir / f'{id_name}{src.suffix}'
    shutil.copy2(str(src), str(dst))
    return dst.relative_to(REGISTRY_DIR).as_posix()


def _extract_docx_schema(docx_path, id_name):
    """Word 模板 → JSON Schema（复用 schema_extractor，含循环/对象/条件推断）"""
    sys.path.insert(0, str(SCRIPT_DIR))
    from schema_extractor import extract_schema
    schema = extract_schema(docx_path)
    schema['template'] = id_name  # 记录模板 id 而非原始路径
    schema_dir = REGISTRY_DIR / 'schemas'
    schema_dir.mkdir(parents=True, exist_ok=True)
    schema_path = schema_dir / f'{id_name}.schema.json'
    schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2),
                           encoding='utf-8')
    return schema_path.relative_to(REGISTRY_DIR).as_posix()


def register_template(template_path, category='用户自定义', name=None,
                      template_id=None, version='1.0', force=False, tags=None,
                      source='user'):
    """
    模板入库主流程：
        1. 校验模板存在 + 推断 format
        2. 复制模板到 registry/<fmt>/
        3. docx → 自动提取 JSON Schema
        4. latex/markdown/html → M1 仅登记（schema 留空，M2 生成）
        5. 追加 manifest 条目
    返回新条目 dict。
    """
    src = Path(template_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f'模板文件不存在: {src}')

    fmt = _infer_format(src)
    stem = src.stem
    if name is None:
        name = stem
    if template_id is None:
        template_id = f'user-{_slugify(stem)}'
    if source not in SOURCES:
        raise ValueError(f'非法 source: {source}（可选: {sorted(SOURCES)}）')

    manifest = load_manifest()
    existing = find_template(manifest, template_id)
    if existing and not force:
        raise ValueError(
            f'模板 id 已存在: {template_id}（用 --force 覆盖，或 --id 指定新 id）')

    # 复制模板文件
    rel_path = _copy_to_registry(src, fmt, template_id)

    # docx 自动提取 schema；其余格式 M1 仅登记
    schema_ref = ''
    if fmt == 'docx':
        schema_ref = _extract_docx_schema(
            REGISTRY_DIR / fmt / f'{template_id}{src.suffix}', template_id)

    entry = {
        'manifest_version': MANIFEST_VERSION,
        'id': template_id,
        'name': name,
        'version': version,
        'format': fmt,
        'category': category if category in CATEGORIES or category else '用户自定义',
        'engine': FORMAT_ENGINE[fmt],
        'source': source,
        'template_path': rel_path,
        'schema_ref': schema_ref,
        'preview': '',
        'placeholder_syntax': 'jinja2' if fmt == 'docx' else (
            'tex-placeholder-v1' if fmt == 'latex' else 'md-convention'),
        'tags': tags or [],
        'usage_count': 0,
        'created_at': now_str(),
        'updated_at': now_str(),
    }

    if existing:
        # --force 覆盖：保留原 id，更新除 created_at/usage_count 外的字段
        old = existing
        old.update(entry)
        old['created_at'] = existing['created_at']
    else:
        manifest['templates'].append(entry)

    save_manifest(manifest)
    return entry


# ============================================================
# CLI 子命令
# ============================================================

def cmd_add(args):
    entry = register_template(args.template, category=args.category,
                              name=args.name, template_id=args.id,
                              version=args.version, force=args.force,
                              tags=args.tags)
    print(f'== 模板已入库 ==')
    print(f'  id:           {entry["id"]}')
    print(f'  name:         {entry["name"]}')
    print(f'  format:       {entry["format"]}  engine: {entry["engine"]}')
    print(f'  category:     {entry["category"]}')
    print(f'  template:     registry/{entry["template_path"]}')
    print(f'  schema:       registry/{entry["schema_ref"] or "(未生成，M2)"}')
    if entry['schema_ref']:
        print(f'  schema 字段数: {len(json.loads((REGISTRY_DIR / entry["schema_ref"]).read_text(encoding="utf-8")).get("fields", {}))}')


def cmd_list(args):
    manifest = load_manifest()
    templates = manifest['templates']

    # 过滤
    if args.format:
        templates = [t for t in templates if t['format'] == args.format]
    if args.category:
        templates = [t for t in templates if t['category'] == args.category]
    if args.query:
        q = args.query.lower()
        templates = [t for t in templates
                     if q in t['id'].lower() or q in t['name'].lower()
                     or any(q in (tag or '').lower() for tag in t.get('tags', []))
                     or q in t['category'].lower()]

    if not templates:
        print('（无模板）')
        return
    print(f'共 {len(templates)} 个模板:')
    print(f'{"id":<32} {"format":<10} {"engine":<18} {"category":<8} {"uses":<5} name')
    print('-' * 100)
    for t in templates:
        print(f'{t["id"]:<32} {t["format"]:<10} {t["engine"]:<18} '
              f'{t["category"]:<8} {t.get("usage_count", 0):<5} {t["name"]}')


def cmd_describe(args):
    manifest = load_manifest()
    tpl = find_template(manifest, args.template_id)
    if not tpl:
        print(f'错误：模板不存在: {args.template_id}（用 list 查看全部）')
        sys.exit(1)
    print(f'== {tpl["id"]} ==')
    for key in ('name', 'version', 'format', 'category', 'engine', 'source',
                'template_path', 'schema_ref', 'placeholder_syntax', 'tags',
                'usage_count', 'created_at', 'updated_at'):
        val = tpl.get(key, '')
        print(f'  {key:<18} {val if val not in (None, "", []) else "(空)"}')
    # schema 字段摘要
    if tpl.get('schema_ref'):
        schema = json.loads((REGISTRY_DIR / tpl['schema_ref']).read_text(encoding='utf-8'))
        fields = schema.get('fields', {})
        print(f'\n  schema 字段 ({len(fields)} 个):')
        for fname, spec in fields.items():
            t = spec['type']
            req = '必填' if spec.get('required', True) else '可选'
            print(f'    - {fname} [{t}/{req}]')


def cmd_schema(args):
    manifest = load_manifest()
    tpl = find_template(manifest, args.template_id)
    if not tpl:
        print(f'错误：模板不存在: {args.template_id}')
        sys.exit(1)
    if not tpl.get('schema_ref'):
        print(f'模板 {tpl["id"]} 尚未生成 schema（{tpl["format"]} 格式 M2 支持）')
        sys.exit(1)
    schema_path = REGISTRY_DIR / tpl['schema_ref']
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(schema_path), str(out))
        print(f'schema 已保存: {out}')
    else:
        print(schema_path.read_text(encoding='utf-8'))


def cmd_search(args):
    args.query = args.query
    args.format = None
    args.category = None
    cmd_list(args)


def cmd_remove(args):
    manifest = load_manifest()
    tpl = find_template(manifest, args.template_id)
    if not tpl:
        print(f'错误：模板不存在: {args.template_id}')
        sys.exit(1)
    if tpl['source'] == 'builtin' and not args.force:
        print(f'错误：{tpl["id"]} 是内置模板，需 --force 才能删除',
              file=sys.stderr)
        sys.exit(1)
    # 删除相关文件
    if args.delete_files:
        tpl_file = REGISTRY_DIR / tpl['template_path']
        if tpl_file.exists():
            tpl_file.unlink()
        if tpl.get('schema_ref'):
            schema_file = REGISTRY_DIR / tpl['schema_ref']
            if schema_file.exists():
                schema_file.unlink()
        print(f'  [已删文件] {tpl_file.name}' + (f' + {Path(tpl["schema_ref"]).name}' if tpl.get('schema_ref') else ''))
    manifest['templates'] = [t for t in manifest['templates']
                             if t['id'] != args.template_id]
    save_manifest(manifest)
    print(f'== 已移除模板: {args.template_id} ==')


def cmd_update_usage(args):
    manifest = load_manifest()
    tpl = find_template(manifest, args.template_id)
    if not tpl:
        print(f'错误：模板不存在: {args.template_id}')
        sys.exit(1)
    tpl['usage_count'] = tpl.get('usage_count', 0) + args.inc
    tpl['updated_at'] = now_str()
    save_manifest(manifest)
    print(f'{tpl["id"]} usage_count = {tpl["usage_count"]}')


# ============================================================
# 主入口
# ============================================================

def main():
    ap = argparse.ArgumentParser(
        prog='template_registry.py',
        description='模板注册表 v1（manifest.json）— 模板入库 / 发现 / schema 管理')
    sub = ap.add_subparsers(dest='cmd')

    p_add = sub.add_parser('add', help='模板入库（docx 自动提取 schema）')
    p_add.add_argument('template', help='模板文件路径（.docx/.tex/.md/.html）')
    p_add.add_argument('-c', '--category', default='用户自定义',
                       help='分类: 全局/场景/用户自定义 或具体场景名')
    p_add.add_argument('-n', '--name', default=None, help='显示名称（默认文件名）')
    p_add.add_argument('--id', dest='id', default=None,
                       help='模板 id（默认 user-<文件名>）')
    p_add.add_argument('-v', '--version', default='1.0', help='模板版本')
    p_add.add_argument('--tags', nargs='*', default=None, help='标签（空格分隔）')
    p_add.add_argument('--force', action='store_true', help='id 冲突时覆盖')
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser('list', help='列出模板（可过滤）')
    p_list.add_argument('-f', '--format', choices=sorted(FORMATS), default=None)
    p_list.add_argument('-c', '--category', default=None)
    p_list.add_argument('query', nargs='?', default=None, help='名称/id/标签模糊匹配')
    p_list.set_defaults(func=cmd_list)

    p_desc = sub.add_parser('describe', help='模板详情 + schema 摘要')
    p_desc.add_argument('template_id')
    p_desc.set_defaults(func=cmd_describe)

    p_schema = sub.add_parser('schema', help='导出模板 JSON Schema')
    p_schema.add_argument('template_id')
    p_schema.add_argument('-o', '--output', default=None, help='输出文件（默认打印）')
    p_schema.set_defaults(func=cmd_schema)

    p_search = sub.add_parser('search', help='按名称/id/标签搜索模板')
    p_search.add_argument('query')
    p_search.set_defaults(func=cmd_search)

    p_rm = sub.add_parser('remove', help='移除模板')
    p_rm.add_argument('template_id')
    p_rm.add_argument('--force', action='store_true', help='允许删内置模板')
    p_rm.add_argument('-d', '--delete-files', action='store_true',
                      help='同时删除模板文件与 schema')
    p_rm.set_defaults(func=cmd_remove)

    p_usage = sub.add_parser('update-usage', help='使用计数 +1')
    p_usage.add_argument('template_id')
    p_usage.add_argument('--inc', type=int, default=1)
    p_usage.set_defaults(func=cmd_update_usage)

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except (FileNotFoundError, ValueError) as e:
        print(f'错误：{e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
