"""
doc-html-pdf · 主生成脚本
=========================

功能：
  1. 加载内容 JSON（蒸馏产物）+ 主题 JSON（颜色方案）
  2. 用 Jinja2 模板渲染精美 HTML（打印样式 + 分页）
  3. 用 Playwright（Chromium）把 HTML 编译为 A4 PDF

用法：
  python scripts/build.py --content content/example.json --theme emerald --format all
  python scripts/build.py --content content/example.json --theme blue --format pdf
  python scripts/build.py --content content/example.json --no-flow   # 每章强制换页（报告风格）
  python scripts/build.py --batch --format all        # 扫描 content/*.json × 全部主题
"""
import argparse
import json
import os
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

# ============== 路径设置 ==============
SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"
THEMES_DIR = SKILL_ROOT / "themes"
CONTENT_DIR = SKILL_ROOT / "content"
OUTPUT_DIR = SKILL_ROOT / "output"
KATEX_DIR = SKILL_ROOT / "assets" / "katex"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============== 加载器 ==============
def load_theme(theme_id: str) -> dict:
    """加载主题 JSON"""
    path = THEMES_DIR / f"{theme_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"主题 {theme_id} 不存在：{path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_themes() -> list[str]:
    """扫描 themes/ 下全部主题 ID"""
    return sorted(p.stem for p in THEMES_DIR.glob("*.json"))


def load_content(content_path: str | Path) -> dict:
    """加载蒸馏后的内容 JSON"""
    p = Path(content_path)
    if not p.exists():
        p = CONTENT_DIR / content_path
    if not p.exists():
        raise FileNotFoundError(f"内容文件不存在：{p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def rel_katex(html_path: Path, name: str) -> str:
    """计算 HTML 文件到 assets/katex 资源的相对路径"""
    try:
        rel = os.path.relpath(KATEX_DIR, html_path.parent)
    except ValueError:
        rel = str(KATEX_DIR)
    return (Path(rel) / name).as_posix()


# ============== HTML 渲染 ==============
def render_html(content: dict, theme: dict, html_path: Path = None, flow: bool = True) -> str:
    """用 Jinja2 模板渲染 HTML

    flow: 连续流动分页（学术论文惯例，章节不强制换页，杜绝页尾大片空白）；
          设为 False 时每章强制换页（报告/手册风格）。
    """
    html_path = html_path or (OUTPUT_DIR / "preview.html")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )
    template = env.get_template("doc.html.j2")
    return template.render(
        content=content,
        theme=theme,
        meta=content["meta"],
        cover=content["cover"],
        toc=content["toc"],
        sections=content["sections"],
        preamble=content.get("preamble", []),
        flow=flow,
        katex_css=rel_katex(html_path, "katex.min.css"),
        katex_js=rel_katex(html_path, "katex.min.js"),
        katex_autorender=rel_katex(html_path, "auto-render.min.js"),
    )


# ============== PDF 编译 ==============
def compile_pdf(html_path: Path, pdf_path: Path) -> None:
    """用 Playwright 把 HTML 编译为 PDF"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///{html_path.as_posix()}", wait_until="networkidle")
        page.wait_for_selector(".katex", timeout=5000)   # 等 KaTeX 渲染完成
        page.wait_for_timeout(500)                        # 额外等待布局稳定
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            prefer_css_page_size=True,
        )
        browser.close()


# ============== 单文档生成 ==============
def generate(content_path: str | Path, theme_id: str, formats: list[str] = None, out_dir: Path = OUTPUT_DIR, flow: bool = True) -> dict:
    """生成单个文档。返回：{"html": path, "pdf": path}"""
    formats = formats or ["html", "pdf"]
    content = load_content(content_path)
    theme = load_theme(theme_id)

    name = Path(content_path).stem
    base = f"{name}-{theme_id}"

    results = {}

    if "html" in formats:
        html_path = out_dir / f"{base}.html"
        html_content = render_html(content, theme, html_path, flow=flow)
        html_path.write_text(html_content, encoding="utf-8")
        results["html"] = html_path
        print(f"  ✓ HTML: {html_path}")

    if "pdf" in formats:
        if "html" not in results:
            html_path = out_dir / f"{base}.html"
            html_content = render_html(content, theme, html_path, flow=flow)
            html_path.write_text(html_content, encoding="utf-8")
            results["html"] = html_path
        pdf_path = out_dir / f"{base}.pdf"
        compile_pdf(results["html"], pdf_path)
        results["pdf"] = pdf_path
        print(f"  ✓ PDF:  {pdf_path}")

    return results


# ============== 批量生成 ==============
def batch_generate(formats: list[str] = None, flow: bool = True) -> None:
    """批量生成：content/*.json × themes/*.json 全部组合"""
    formats = formats or ["html", "pdf"]
    content_files = sorted(CONTENT_DIR.glob("*.json"))
    if not content_files:
        print("⚠️  content/ 目录下没有 JSON 内容文件，请先运行 distill.py 生成。")
        sys.exit(1)
    themes = list_themes()

    print(f"\n{'='*60}")
    print(f" doc-html-pdf · 批量生成")
    print(f" 内容: {len(content_files)} 个 × 主题: {len(themes)} 套 = {len(content_files)*len(themes)} 份")
    print(f" 格式: {', '.join(formats)}")
    print(f" 分页: {'连续流动' if flow else '每章强制换页'}")
    print(f"{'='*60}\n")

    total = 0
    for path in content_files:
        for theme_id in themes:
            print(f"📄 {path.stem} · {theme_id} 主题")
            generate(path, theme_id, formats, flow=flow)
            total += 1
            print()

    print(f"{'='*60}")
    print(f" ✅ 完成：共生成 {total} 份文档（{total * len(formats)} 个文件）")
    print(f" 📂 输出目录：{OUTPUT_DIR}")
    print(f"{'='*60}\n")


# ============== CLI ==============
def main():
    parser = argparse.ArgumentParser(description="doc-html-pdf · 文档生成器（HTML + PDF）")
    parser.add_argument("--content", "-c", help="内容 JSON 路径（content/ 下的文件名或完整路径）")
    parser.add_argument("--theme", "-t", default="emerald", help="主题 ID（emerald/blue/slate，可用 --themes 列出）")
    parser.add_argument("--format", "-f", default="all", help="输出格式：all / html,pdf（逗号分隔）")
    parser.add_argument("--batch", "-b", action="store_true", help="批量生成 content/*.json × 全部主题")
    parser.add_argument("--out", "-o", default=str(OUTPUT_DIR), help="输出目录（默认 output/）")
    parser.add_argument("--flow", dest="flow", action="store_true", default=True, help="连续流动分页（默认，学术论文惯例，章节不强制换页，杜绝页尾空白）")
    parser.add_argument("--no-flow", dest="flow", action="store_false", help="每章强制换页（报告/手册风格）")
    parser.add_argument("--themes", action="store_true", help="列出可用主题")
    args = parser.parse_args()

    if args.themes:
        print("可用主题：", ", ".join(list_themes()))
        sys.exit(0)

    if args.format == "all":
        formats = ["html", "pdf"]
    else:
        formats = [f.strip() for f in args.format.split(",")]
        invalid = [f for f in formats if f not in ("html", "pdf")]
        if invalid:
            print(f"❌ 不支持的格式：{', '.join(invalid)}（仅支持 html/pdf）")
            sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.batch:
        batch_generate(formats, flow=args.flow)
    elif args.content:
        print(f"\n📄 {args.content} · {args.theme} 主题")
        generate(args.content, args.theme, formats, out_dir, flow=args.flow)
    else:
        parser.print_help()
        print("\n提示：使用 --content 指定内容文件，或 --batch 批量生成全部")
        sys.exit(1)


if __name__ == "__main__":
    main()
