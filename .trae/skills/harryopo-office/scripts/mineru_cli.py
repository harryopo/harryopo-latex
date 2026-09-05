#!/usr/bin/env python3
"""
mineru_cli.py — DOCX/PDF/图片 → Markdown 全流程转换脚本

管线：
  DOCX → MinerU office 解析 → Markdown + HTML 表格
  PDF/图片 → MinerU pipeline 解析 → Markdown + HTML 表格
  MD → 直接清洗

清洗规则：
  1. 去标题加粗（Word 标题样式含 bold，MinerU 如实保留了 **）
  2. HTML 表格 → LaTeX 代码（用 html_table_to_latex.py）
  3. 图片路径规范化

用法：
  python mineru_cli.py input.docx -o output_dir/
  python mineru_cli.py input.pdf -o output_dir/ --backend pipeline
  python mineru_cli.py input.md  -o output_dir/

输出：
  output_dir/result.md     — 清洗后的 Markdown（可交给 convert.py）
  output_dir/result.json   — MinerU 原始 JSON（调试用，可选）
  output_dir/images/       — 提取的图片
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# ───────────────────────── MinerU 封装 ─────────────────────────

def parse_docx(file_bytes: bytes, img_dir: str) -> tuple:
    """用 MinerU office 后端解析 DOCX

    Returns: (middle_json, results)
    """
    from mineru.backend.office.docx_analyze import office_docx_analyze
    from mineru.data.data_reader_writer import FileBasedDataWriter

    Path(img_dir).mkdir(parents=True, exist_ok=True)
    image_writer = FileBasedDataWriter(img_dir)
    return office_docx_analyze(file_bytes, image_writer)


def parse_pdf_or_image(file_path: str, img_dir: str, lang: str = "ch") -> tuple:
    """PDF/图片 → Markdown：调用官方 `mineru.cli.common.do_parse`（Python 直连）。

    3.x 的 pipeline 内部 API 改为流式接口（无稳定 `PipelineAnalyze` 可依赖），
    官方 CLI 又是"本地 mineru-api 服务 + HTTP"架构（首次模型下载时健康检查超时，
    见 8/05 踩坑记录）。因此 PDF/图片路径用官方统一入口 `do_parse`（backend=
    'pipeline'，本地模型，首次运行自动从 modelscope 下载模型），仅保留 MD 产出，
    关闭可视化/中间 JSON 等附加产物加速。清洗逻辑保持不变。

    Returns: (fake_middle_json, None) —— fake_middle_json 带 '_md_text'，
             供 middle_json_to_markdown 直接返回官方 MD。
    """
    file_path = Path(file_path)
    stem = file_path.stem
    out_dir = Path(img_dir).parent / 'mineru_official'
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f'   [pipeline] do_parse {file_path.name} → {out_dir.name}/{stem}/'
          f'（首次运行自动下载模型，约数 GB）')
    from mineru.cli.common import do_parse
    do_parse(
        output_dir=str(out_dir),
        pdf_file_names=[stem],
        pdf_bytes_list=[file_path.read_bytes()],
        p_lang_list=[lang],
        backend='pipeline',
        f_draw_layout_bbox=False,
        f_draw_span_bbox=False,
        f_dump_md=True,
        f_dump_middle_json=False,
        f_dump_model_output=False,
        f_dump_orig_pdf=False,
        f_dump_content_list=False,
    )

    md_candidates = sorted(out_dir.rglob(f'{stem}.md')) or sorted(out_dir.rglob('*.md'))
    if not md_candidates:
        raise RuntimeError(f'do_parse 未产出 MD: {out_dir}')
    md_file = md_candidates[0]
    md_text = md_file.read_text(encoding='utf-8')
    print(f'   官方 MD: {md_file.relative_to(out_dir)} ({len(md_text)} chars)')

    # 搬运 images 到 img_dir（保持 result.md 的相对引用可用）
    Path(img_dir).mkdir(parents=True, exist_ok=True)
    moved = 0
    for pattern in ('*.jpg', '*.jpeg', '*.png'):
        for src in md_file.parent.rglob(pattern):
            dst = Path(img_dir) / src.name
            if not dst.exists():
                shutil.copyfile(src, dst)
                moved += 1
    if moved:
        print(f'   images: 搬运 {moved} 张 → {img_dir}')

    return {'_md_text': md_text}, None


def middle_json_to_markdown(middle_json: dict, img_dir: str) -> str:
    """将 MinerU middle_json 转为 Markdown"""
    from mineru.backend.office.office_middle_json_mkcontent import union_make as office_mk
    from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_mk
    from mineru.utils.enum_class import MakeMode

    # 官方 CLI 委托路径：MD 已由官方产出，直接返回
    if '_md_text' in middle_json:
        return middle_json['_md_text']

    pdf_info = middle_json.get('pdf_info', [])
    backend = middle_json.get('_backend', 'office')

    if backend == 'pipeline':
        return pipeline_mk(pdf_info, MakeMode.MM_MD, img_dir)
    else:
        return office_mk(pdf_info, MakeMode.MM_MD, img_dir)


# ───────────────────────── MD 清洗 ─────────────────────────

def clean_markdown_review(md_content: str) -> str:
    """阶段1清洗：生成供用户审查的标准 Markdown

    规则：
    1. 去标题加粗（# **标题** → # 标题）
    2. <strong> → **加粗**（表格内加粗保留为 MD 标记）
    3. <em>/<i> → *斜体*
    4. <ol><li> → 有序列表 / <ul><li> → 无序列表
    5. 去掉其他 HTML 标签（<p>/<a> 等）
    6. 压缩多余空行
    7. 保留 HTML 表格结构（用户可审查合并单元格是否正确）

    输出：干净的 Markdown，加粗用 ** 标记，表格保留 HTML（可读性好）
    """
    cleaned = md_content

    # 1. 去标题加粗
    cleaned = re.sub(
        r'^(#{1,6}\s+?)\*\*(.+?)\*\*\s*$',
        r'\1\2',
        cleaned,
        flags=re.MULTILINE
    )

    # 2-4. 清理 HTML 标签但保留语义标记
    # <strong>/<b> → **加粗**
    cleaned = re.sub(r'<(?:strong|b)>(.*?)</(?:strong|b)>', r'**\1**', cleaned, flags=re.DOTALL)
    # <em>/<i> → *斜体*
    cleaned = re.sub(r'<(?:em|i)>(.*?)</(?:em|i)>', r'*\1*', cleaned, flags=re.DOTALL)
    # <a href="...">text</a> → text
    cleaned = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', cleaned, flags=re.DOTALL)
    # <ol><li>...</li></ol> → 编号列表
    def _convert_list(match):
        items = re.findall(r'<li>(.*?)</li>', match.group(0), re.DOTALL)
        inner = re.sub(r'<[^>]+>', '', match.group(0))
        cleaned_items = [re.sub(r'<[^>]+>', '', item).strip() for item in items]
        if '<ol>' in match.group(0):
            return '\n'.join(f'{i+1}. {item}' for i, item in enumerate(cleaned_items))
        else:
            return '\n'.join(f'- {item}' for item in cleaned_items)
    cleaned = re.sub(r'<[ou]l>.*?</[ou]l>', _convert_list, cleaned, flags=re.DOTALL)
    # 去掉 <p> 标签
    cleaned = re.sub(r'</?p>', '', cleaned)
    # 去掉其他残留 HTML 标签（但保留 <table>/<tr>/<td> 表格结构）
    # 不在表格内的零散 HTML 标签
    cleaned = re.sub(r'<(?!/?table|/?tr|/?td|/?th|colspan|rowspan)[^>]+>', '', cleaned)

    # 5. 压缩 3+ 连续空行
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()


def clean_markdown_convert(md_content: str) -> str:
    """阶段2清洗：将审查通过的 Markdown 转为含 LaTeX 代码的 Markdown

    规则：
    1. HTML 表格 → LaTeX 表格代码（调用 html_table_to_latex.py）
    2. 压缩空行

    输入：阶段1的输出（用户已审查确认）
    输出：含 LaTeX 环境的 Markdown（交给 convert.py 处理）
    """
    cleaned = md_content

    # HTML 表格 → LaTeX
    try:
        from html_table_to_latex import replace_html_tables_in_markdown
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from html_table_to_latex import replace_html_tables_in_markdown

    cleaned = replace_html_tables_in_markdown(cleaned)

    # 压缩空行
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()


# 兼容旧接口
def clean_markdown(md_content: str, replace_html_tables: bool = True) -> str:
    """兼容旧接口：一步到位清洗"""
    reviewed = clean_markdown_review(md_content)
    if replace_html_tables:
        return clean_markdown_convert(reviewed)
    return reviewed


# ───────────────────────── 主入口 ─────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='DOCX/PDF/MD → Markdown 转换（MinerU + 清洗）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 阶段1：DOCX → 审查MD（展示给用户确认）
  python mineru_cli.py input.docx -o output/ --stage review

  # 阶段2：审查MD → LaTeX MD（用户确认后执行）
  python mineru_cli.py output/review.md -o output/ --stage convert

  # 一步到位（跳过审查，不推荐）
  python mineru_cli.py input.docx -o output/
        """
    )
    parser.add_argument('input', help='输入文件路径（.docx/.pdf/.md/.png/.jpg）')
    parser.add_argument('-o', '--output', default='./output', help='输出目录（默认 ./output）')
    parser.add_argument('--stage', choices=['auto', 'review', 'convert'],
                        default='auto', help='清洗阶段：review=审查MD，convert=转LaTeX MD，auto=一步到位')
    parser.add_argument('--backend', choices=['auto', 'office', 'pipeline'],
                        default='auto', help='MinerU 后端（auto 自动选择，默认 auto）')
    parser.add_argument('--lang', default='ch', help='OCR 语言（默认 ch 中文）')
    parser.add_argument('--skip-mineru', action='store_true',
                        help='跳过 MinerU 解析，仅清洗 MD（输入已是 MD 时使用）')
    parser.add_argument('--save-json', action='store_true',
                        help='保存 MinerU 原始 JSON（调试用）')
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    img_dir = str(output_dir / 'images')

    if not input_path.exists():
        print(f'错误：输入文件不存在: {input_path}', file=sys.stderr)
        sys.exit(1)

    suffix = input_path.suffix.lower()
    print(f'输入: {input_path}')
    print(f'输出: {output_dir}')

    # ──── Step 1: 解析 ────
    middle_json = None

    if args.skip_mineru or suffix == '.md':
        # 直接读取 MD
        print('\n[1/3] 读取 Markdown（跳过 MinerU）...')
        md_content = input_path.read_text(encoding='utf-8')
        print(f'   读取完成: {len(md_content)} chars')
    elif suffix == '.docx':
        # DOCX → MinerU office 后端
        print('\n[1/3] MinerU 解析 DOCX...')
        file_bytes = input_path.read_bytes()
        middle_json, results = parse_docx(file_bytes, img_dir)
        if middle_json:
            middle_json['_backend'] = 'office'
        print(f'   解析完成: {len(results)} 页')
        md_content = middle_json_to_markdown(middle_json, img_dir)
        print(f'   Markdown 生成: {len(md_content)} chars')
    elif suffix in ('.pdf', '.png', '.jpg', '.jpeg'):
        # PDF/图片 → MinerU pipeline 后端
        print('\n[1/3] MinerU 解析（pipeline 后端，首次较慢）...')
        middle_json, results = parse_pdf_or_image(str(input_path), img_dir, args.lang)
        if middle_json:
            middle_json['_backend'] = 'pipeline'
        print(f'   解析完成')
        md_content = middle_json_to_markdown(middle_json, img_dir)
        print(f'   Markdown 生成: {len(md_content)} chars')
    else:
        print(f'错误：不支持的文件类型: {suffix}', file=sys.stderr)
        sys.exit(1)

    # 保存原始 MD（调试用）
    raw_md_file = output_dir / 'raw_mineru.md'
    raw_md_file.write_text(md_content, encoding='utf-8')

    # 保存 JSON（调试用）
    if args.save_json and middle_json:
        json_file = output_dir / 'result.json'
        json_file.write_text(
            json.dumps(middle_json, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f'   JSON 保存: {json_file}')

    # ──── Step 2: 清洗 ────
    stage = args.stage

    # convert 阶段：输入是审查 MD，跳过 MinerU 解析阶段已完成
    if stage == 'convert':
        print('\n[2/2] 阶段2：审查MD → LaTeX MD...')
        reviewed_md = md_content  # 输入的就是审查后的 MD
        cleaned = clean_markdown_convert(reviewed_md)
        html_table_count = len(re.findall(r'<table>', reviewed_md))
        latex_table_count = len(re.findall(r'\\begin\{(?:longtable|tabular|table\|tabularx)\}', cleaned))
        fzht_count = len(re.findall(r'\\fzht\{', cleaned))
        bold_count = len(re.findall(r'\*\*', reviewed_md))
        print(f'   HTML 表格: {html_table_count} → LaTeX 表格: {latex_table_count}')
        print(f'   加粗标记 **: {bold_count // 2} 处')
        print(f'   清洗后: {len(cleaned)} chars')

        print('\n[输出] 保存结果...')
        result_file = output_dir / 'converted.md'
        result_file.write_text(cleaned, encoding='utf-8')
        print(f'   ✅ {result_file}')
        print(f'\n完成！用 convert.py 转 LaTeX:')
        print(f'   python convert.py {result_file} --type paper --no-math')
        return

    # review 或 auto 阶段
    print(f'\n[2/{"3" if stage == "auto" else "2"}] 清洗 Markdown（阶段1：审查MD）...')
    reviewed = clean_markdown_review(md_content)

    bold_count = len(re.findall(r'\*\*', reviewed)) // 2
    html_table_count = len(re.findall(r'<table>', reviewed))
    print(f'   加粗标记 **: {bold_count} 处')
    print(f'   HTML 表格: {html_table_count} 个（保留结构供审查）')
    print(f'   清洗后: {len(reviewed)} chars')

    if stage == 'review':
        print('\n[输出] 保存审查MD...')
        review_file = output_dir / 'review.md'
        review_file.write_text(reviewed, encoding='utf-8')
        print(f'   ✅ {review_file}')
        print(f'\n请审查 {review_file} 内容。')
        print(f'确认无误后执行阶段2:')
        print(f'   python mineru_cli.py {review_file} -o {output_dir} --stage convert')
        return

    # auto 模式：继续阶段2
    print(f'\n[3/3] 清洗 Markdown（阶段2：转LaTeX MD）...')
    cleaned = clean_markdown_convert(reviewed)
    latex_table_count = len(re.findall(r'\\begin\{(?:longtable|tabular|table|tabularx)\}', cleaned))
    print(f'   LaTeX 表格: {latex_table_count}')

    print('\n[输出] 保存结果...')
    result_file = output_dir / 'result.md'
    result_file.write_text(cleaned, encoding='utf-8')
    print(f'   ✅ {result_file}')
    print(f'\n完成！用 convert.py 转 LaTeX:')
    print(f'   python convert.py {result_file} --type paper --no-math')


if __name__ == '__main__':
    main()
