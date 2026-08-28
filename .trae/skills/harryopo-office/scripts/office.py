#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
office.py — 办公超级 Skill 统一入口

一个命令，MD → Word / PDF (paper) / PDF (math-notes)，任意组合输出。

用法:
    python office.py render input.md                          # 默认产出全部三种
    python office.py render input.md --format word            # 只产出 Word
    python office.py render input.md --format paper           # 只产出 PDF (论文)
    python office.py render input.md --format notes           # 只产出 PDF (笔记)
    python office.py render input.md --format word,paper      # 组合输出
    python office.py render input.md --format all --open      # 产出后自动打开
    python office.py render input.md --config opensource      # 用开源字体
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ============================================================
# 路径常量（自动推算，不依赖运行目录）
# ============================================================
SCRIPT_DIR = Path(__file__).parent.resolve()          # .../scripts/
SKILL_DIR = SCRIPT_DIR.parent                          # .../harryopo-office/

# 自动查找项目根（向上遍历直到找到 templates/ 目录）
def _find_project_root():
    """从 skill 目录向上查找包含 templates/ 的目录"""
    for parent in [SKILL_DIR] + list(SKILL_DIR.parents):
        if (parent / 'templates' / 'cls').exists():
            return parent
    # 回退：假设标准结构 .../project_root/.trae/skills/harryopo-office/
    return SKILL_DIR.parents[2]  # .../project_root/

PROJECT_ROOT = _find_project_root()
TEMPLATES = PROJECT_ROOT / 'templates'
CLS_DIR = TEMPLATES / 'cls'
FONTS_DIR = TEMPLATES / 'fonts'
PAPER_DIR = TEMPLATES / 'paper'
NOTES_DIR = TEMPLATES / 'math-notes'

WORD_SCRIPT = SCRIPT_DIR / 'word' / 'md_to_word.py'
CONVERT_SCRIPT = SCRIPT_DIR / 'convert.py'
PANDOC_TEMPLATE = SCRIPT_DIR / 'pandoc' / 'mathnotes-template.latex'
PANDOC_LUA = SCRIPT_DIR / 'pandoc' / 'mathnotes-table.lua'
WORD_CONFIG_FZ = SCRIPT_DIR / 'word' / 'configs' / 'fangzheng.json'
WORD_CONFIG_OS = SCRIPT_DIR / 'word' / 'configs' / 'opensource.json'


# ============================================================
# 工具函数
# ============================================================

def run(cmd, cwd=None, env_extra=None, check=True, label=''):
    """运行子进程，返回 (success, stdout, stderr)"""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    print(f'  [{label}] {" ".join(str(c) for c in cmd[:4])}...')
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                            capture_output=True, text=True, env=env)
    if check and result.returncode != 0:
        stderr_tail = result.stderr.strip().split('\n')[-3:] if result.stderr else []
        return False, result.stdout, '\n'.join(stderr_tail)
    return True, result.stdout, result.stderr


def ensure_placeholder_figures(target_dir, md_file):
    """扫描 MD 中的图片引用，为目标目录创建缺失的占位图"""
    import re
    text = Path(md_file).read_text(encoding='utf-8')
    imgs = re.findall(r'!\[.*?\]\((.*?)\)', text)
    if not imgs:
        return
    try:
        from PIL import Image
    except ImportError:
        return
    for img_path in imgs:
        # 解析相对路径
        img_name = Path(img_path).name
        # 在目标目录下创建对应的 figures/ 子目录
        if 'figures/' in img_path or 'figures\\' in img_path:
            fig_dir = target_dir / 'figures'
            fig_dir.mkdir(exist_ok=True)
            target = fig_dir / img_name
        else:
            target = target_dir / img_name
        if not target.exists():
            img = Image.new('RGB', (800, 400), '#F0F0F0')
            img.save(str(target))
            print(f'  [占位] {target.name}')


def collect_output(src, dst):
    """复制产物到输出目录（容错：目标被锁时自动加后缀）"""
    if src.exists():
        try:
            shutil.copy2(str(src), str(dst))
        except PermissionError:
            # 目标文件被锁（如 PDF 阅读器），换带时间戳的文件名
            dst = dst.with_stem(dst.stem + '-new')
            shutil.copy2(str(src), str(dst))
        print(f'  [产物] {dst.name} ({src.stat().st_size // 1024}KB)')
        return True
    return False


# ============================================================
# 三条链路
# ============================================================

def render_word(md_file, output_dir, config_name='fangzheng'):
    """链路1: MD → Word"""
    print('\n=== 链路1: MD → Word ===')
    config = WORD_CONFIG_OS if config_name == 'opensource' else WORD_CONFIG_FZ
    output = output_dir / f'{md_file.stem}-word.docx'

    ok, out, err = run(
        [sys.executable, str(WORD_SCRIPT), str(md_file),
         '-o', str(output), '-c', str(config)],
        label='md_to_word'
    )
    if not ok:
        print(f'  [失败] {err}')
        return None
    print(f'  [成功] {output.name}')
    return output


def render_paper(md_file, output_dir):
    """链路2: MD → LaTeX PDF (paper)"""
    print('\n=== 链路2: MD → PDF (paper) ===')
    stem = md_file.stem
    tex_file = output_dir / f'{stem}-paper.tex'

    # Step 1: MD → TEX
    ok, out, err = run(
        [sys.executable, str(CONVERT_SCRIPT), str(md_file),
         '--type', 'paper', '-o', str(tex_file)],
        label='convert.py'
    )
    if not ok:
        print(f'  [失败] {err}')
        return None

    # Step 2: 复制到 templates/paper/ 编译
    compile_tex = PAPER_DIR / f'{stem}-e2e.tex'
    shutil.copy2(str(tex_file), str(compile_tex))

    # Step 2.5: 复制图表图片（mermaid / super-diagram）到编译目录（如果有）
    src_figs = output_dir / 'figures'
    if src_figs.exists():
        dst_figs = PAPER_DIR / 'figures'
        dst_figs.mkdir(exist_ok=True)
        for f in src_figs.glob('*.png'):
            shutil.copy2(str(f), str(dst_figs / f.name))

    # Step 3: 创建占位图（不覆盖已有真实图）
    ensure_placeholder_figures(PAPER_DIR, md_file)

    # Step 4: 编译
    texinputs = f'{CLS_DIR}//;{FONTS_DIR}//;'
    for i in range(2):
        ok, out, err = run(
            ['xelatex', '-interaction=nonstopmode', compile_tex.name],
            cwd=PAPER_DIR, env_extra={'TEXINPUTS': texinputs},
            check=False, label=f'xelatex #{i+1}'
        )

    pdf = PAPER_DIR / compile_tex.with_suffix('.pdf').name
    final_pdf = output_dir / f'{stem}-paper.pdf'
    if pdf.exists() and pdf.stat().st_size > 5000:
        collect_output(pdf, final_pdf)
        return final_pdf
    print('  [失败] PDF 未生成或过小')
    return None


def render_notes(md_file, output_dir):
    """链路3: MD → LaTeX PDF (math-notes)"""
    print('\n=== 链路3: MD → PDF (math-notes) ===')
    stem = md_file.stem
    tex_file = output_dir / f'{stem}-notes.tex'

    # Step 1: Pandoc → TEX
    pandoc_exe = shutil.which('pandoc')
    if not pandoc_exe:
        print('  [失败] pandoc 未安装')
        return None

    ok, out, err = run(
        [pandoc_exe, str(md_file),
         f'--template={PANDOC_TEMPLATE}',
         f'--lua-filter={PANDOC_LUA}',
         '--standalone', '-o', str(tex_file)],
        label='pandoc'
    )
    if not ok:
        print(f'  [失败] {err}')
        return None

    # Step 2: 复制到 templates/math-notes/ 编译
    compile_tex = NOTES_DIR / f'{stem}-e2e.tex'
    shutil.copy2(str(tex_file), str(compile_tex))

    # Step 2.5: 复制图表图片（mermaid / super-diagram）到编译目录（如果有）
    src_figs = output_dir / 'figures'
    if src_figs.exists():
        dst_figs = NOTES_DIR / 'figures'
        dst_figs.mkdir(exist_ok=True)
        for f in src_figs.glob('*.png'):
            shutil.copy2(str(f), str(dst_figs / f.name))

    # Step 3: 创建占位图（不覆盖已有真实图）
    ensure_placeholder_figures(NOTES_DIR, md_file)

    # Step 4: 编译
    for i in range(2):
        ok, out, err = run(
            ['xelatex', '-interaction=nonstopmode', compile_tex.name],
            cwd=NOTES_DIR,
            check=False, label=f'xelatex #{i+1}'
        )

    pdf = NOTES_DIR / compile_tex.with_suffix('.pdf').name
    final_pdf = output_dir / f'{stem}-notes.pdf'
    if pdf.exists() and pdf.stat().st_size > 5000:
        collect_output(pdf, final_pdf)
        return final_pdf
    print('  [失败] PDF 未生成或过小')
    return None


# ============================================================
# 主入口
# ============================================================

def cmd_render(args):
    """render 子命令：渲染 MD 到多种格式"""
    input_file = Path(args.input).resolve()
    if not input_file.exists():
        print(f'错误：找不到 {input_file}')
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解析格式
    formats = args.format.lower().split(',')
    if 'all' in formats:
        formats = ['word', 'paper', 'notes']

    print(f'输入文件: {input_file}')
    print(f'输出目录: {output_dir}')
    print(f'目标格式: {", ".join(formats)}')
    print(f'字体方案: {args.config}')

    # ---- DOCX 预处理：转为 MD ----
    if input_file.suffix.lower() in ('.docx', '.doc'):
        print('\n=== DOCX → Markdown ===')
        tmp_md = output_dir / f'{input_file.stem}_docx.tmp.md'
        md_file = tmp_md
        md_text = None
        converter = 'none'
        # A 档 fast path：anydoc 首选（Rust 内核，毫秒级，GFM 表格原生）。
        # 含图片的文档回退旧链路（anydoc 内嵌图只渲染 alt 文本不落盘，丢图）。
        try:
            import anydoc
            doc = anydoc.to_document(input_file.read_bytes())
            if not doc.assets:
                md_text = anydoc.to_markdown(str(input_file))
                converter = 'anydoc'
            else:
                print('  [INFO] 文档含图片，anydoc 降级为 pandoc（保图片落盘）', file=sys.stderr)
        except Exception:
            pass  # anydoc 未安装 / 转换失败 → 降级 pandoc

        if md_text is None:
            try:
                import subprocess
                # pandoc 转换：禁用 smart（避免弯引号）、禁用自动换行（避免表格/段落断行）
                cmd = ['pandoc', str(input_file), '-f', 'docx',
                       '-t', 'markdown-smart', '--wrap=none', '-o', str(tmp_md)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    md_text = tmp_md.read_text(encoding='utf-8')
                    converter = 'pandoc'
                else:
                    print(f'[WARN] pandoc DOCX→MD 失败: {result.stderr[:200]}', file=sys.stderr)
            except FileNotFoundError:
                print('[WARN] pandoc 未安装，改用 python-docx 提取', file=sys.stderr)

        if md_text is None:
            from convert import convert_docx_via_python
            md_text = convert_docx_via_python(str(input_file))
            converter = 'python-docx'
            if not md_text:
                print('[ERROR] DOCX 转换失败，请安装 anydoc / pandoc / python-docx 之一', file=sys.stderr)
                sys.exit(1)

        # 清洗转换输出：删 TOC / 大标题 / 反转义 / 图片占位 / 表格回填 / Unicode 数学。
        # anydoc 自带 GFM 表格（tables=[] 不重复插表）；pandoc 输出 simple table
        # 需 python-docx 回填（extract_docx_tables）。
        from docx_clean import clean_pandoc_md, extract_docx_tables
        tables = [] if converter == 'anydoc' else extract_docx_tables(str(input_file))
        cleaned = clean_pandoc_md(md_text, tables)
        tmp_md.write_text(cleaned, encoding='utf-8')
        print(f'  [OK] {tmp_md.name}（转换器 {converter}，清洗完成，表格 {len(tables)} 个）')
    else:
        md_file = input_file  # 直接是 MD


    # ---- 图表统一预处理（super-diagram + mermaid）----
    # 将 MD 中的图表数据代码块渲染为 PNG，替换为 ![](figures/xxx.png)
    md_text = md_file.read_text(encoding='utf-8')
    if '```mermaid' in md_text or '```super-diagram' in md_text:
        print('\n=== 图表统一预处理 ===')
        try:
            from diagram_render import extract_and_render, replace_in_md
            fig_dir = output_dir / 'figures'
            replacements = extract_and_render(str(md_file), str(fig_dir))
            if replacements:
                # 替换为相对路径图片引用（正斜杠，兼容 LaTeX/Word）
                md_text = replace_in_md(md_text, replacements)
                print(f'  [OK] 渲染了 {len(replacements)} 个图表')
        except ImportError:
            print('  [WARN] diagram_render 模块未找到，跳过图表渲染')

        # 写预处理后的临时 MD
        processed_md = output_dir / f'{md_file.stem}.processed.md'
        processed_md.write_text(md_text, encoding='utf-8')
        md_file = processed_md
        print(f'  [临时] {processed_md.name}')

    results = {}

    if 'word' in formats:
        results['word'] = render_word(md_file, output_dir, args.config)
    if 'paper' in formats:
        results['paper'] = render_paper(md_file, output_dir)
    if 'notes' in formats:
        results['notes'] = render_notes(md_file, output_dir)

    # 汇总
    print('\n' + '=' * 50)
    print('产物汇总:')
    for fmt, path in results.items():
        if path:
            print(f'  {fmt:8s} → {path} ({path.stat().st_size // 1024}KB)')
        else:
            print(f'  {fmt:8s} → 失败')
    print('=' * 50)

    # 自动打开
    if args.open:
        for path in results.values():
            if path and path.exists():
                os.startfile(str(path))

    # 返回码
    failed = [f for f, p in results.items() if not p]
    if failed:
        print(f'\n警告: 以下格式失败: {", ".join(failed)}')
        sys.exit(1)


def cmd_info(args):
    """info 子命令：打印路径和环境信息"""
    print('=== 办公超级 Skill 环境信息 ===\n')
    print(f'脚本目录:   {SCRIPT_DIR}')
    print(f'Skill 目录: {SKILL_DIR}')
    print(f'项目根:     {PROJECT_ROOT}')
    print(f'模板 cls:   {CLS_DIR}  ({"OK" if CLS_DIR.exists() else "缺失!"})')
    print(f'字体目录:   {FONTS_DIR}  ({"OK" if FONTS_DIR.exists() else "缺失!"})')
    print(f'Paper 目录: {PAPER_DIR}  ({"OK" if PAPER_DIR.exists() else "缺失!"})')
    print(f'Notes 目录: {NOTES_DIR}  ({"OK" if NOTES_DIR.exists() else "缺失!"})')
    print()

    # 检查工具
    pandoc = shutil.which('pandoc')
    xelatex = shutil.which('xelatex')
    print(f'Pandoc:    {pandoc or "未安装!"}')
    print(f'XeLaTeX:   {xelatex or "未安装!"}')

    try:
        import docx
        print(f'python-docx: {docx.__version__}')
    except ImportError:
        print('python-docx: 未安装!')

    try:
        from PIL import Image
        print(f'Pillow:    已安装')
    except ImportError:
        print('Pillow:    未安装!')


def main():
    parser = argparse.ArgumentParser(
        prog='office',
        description='办公超级 Skill 统一入口 — MD → Word / PDF / LaTeX'
    )
    sub = parser.add_subparsers(dest='command')

    # render 子命令
    p_render = sub.add_parser('render', help='渲染 MD 到多种格式')
    p_render.add_argument('input', help='输入 MD 文件路径')
    p_render.add_argument('--format', '-f', default='all',
                          help='输出格式: word, paper, notes, all (默认 all)')
    p_render.add_argument('--config', '-c', default='fangzheng',
                          help='字体方案: fangzheng / opensource (默认 fangzheng)')
    p_render.add_argument('--output-dir', '-o', help='输出目录 (默认 MD 同级)')
    p_render.add_argument('--open', action='store_true',
                          help='完成后自动打开产物')
    p_render.set_defaults(func=cmd_render)

    # info 子命令
    p_info = sub.add_parser('info', help='打印环境信息')
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
