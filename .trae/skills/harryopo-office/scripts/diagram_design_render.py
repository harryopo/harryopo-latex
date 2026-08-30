#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagram_design_render.py — diagram-design HTML → PNG 渲染器
==============================================================

把 diagram-design 生成的图表 HTML 转成 PNG（供插入 Word / LaTeX）。

用法：
  python diagram_design_render.py input.html -o figures/图1.png
  python diagram_design_render.py input.html -o figures/图1.png --svg   # 仅截图 SVG 区域（不含标题）
  python diagram_design_render.py input.html -o figures/图1.png --check # 先跑 self_check.py 自检

依赖：playwright（含 chromium）。首次：
  pip install playwright
  $env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright/"; python -m playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run_self_check(html_path: Path) -> bool:
    """调用 diagram-design 自带 self_check.py 验证（无障碍契约/单文件安全）。"""
    skill_dir = Path(__file__).resolve().parent.parent / "skills" / "diagram-design"
    check_script = skill_dir / "scripts" / "self_check.py"
    if not check_script.exists():
        print("⚠️ 未找到 self_check.py（期望在 skills/diagram-design/scripts/）", file=sys.stderr)
        return True
    r = subprocess.run([sys.executable, str(check_script), str(html_path)],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 0:
        print("✅ self_check 通过")
        return True
    print("❌ self_check 失败:\n" + (r.stdout or r.stderr), file=sys.stderr)
    return False


def render(html_path: Path, png_path: Path, scale: float, svg_only: bool) -> None:
    """HTML → PNG。svg_only=True 时仅截取页面内 <svg> 元素区域。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=scale)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(500)

        if svg_only:
            # 定位 <svg> 元素的渲染区域（相对视口）
            box = page.evaluate("""() => {
                const svg = document.querySelector('svg');
                if (!svg) return null;
                const r = svg.getBoundingClientRect();
                const b = document.body.getBoundingClientRect();
                return {x: r.left, y: r.top + window.scrollY, w: r.width, h: r.height};
            }""")
            if box is None:
                print("❌ 页面中没有 <svg> 元素", file=sys.stderr)
                return
            # 截图前先滚动到 svg 位置（body 居中，svg 可能在首屏内）
            page.evaluate("() => { const s = document.querySelector('svg'); s.scrollIntoView({block:'start'}); }")
            page.wait_for_timeout(200)
            page.screenshot(path=str(png_path),
                            clip={"x": box["x"], "y": box["y"], "width": box["w"], "height": box["h"]})
        else:
            page.screenshot(path=str(png_path), full_page=True)

        browser.close()
    print(f"✅ PNG: {png_path}（scale={scale}, svg_only={svg_only}）")


def main() -> int:
    parser = argparse.ArgumentParser(description="diagram-design HTML → PNG")
    parser.add_argument("input", help="diagram-design 生成的 HTML 文件")
    parser.add_argument("-o", "--output", required=True, help="输出 PNG 路径")
    parser.add_argument("--scale", type=float, default=2.0, help="像素倍率（默认 2.0，插 Word 建议 2-3）")
    parser.add_argument("--svg", action="store_true", help="仅截图 <svg> 区域（不含标题栏）")
    parser.add_argument("--check", action="store_true", help="渲染前先跑 self_check.py 自检")
    args = parser.parse_args()

    html_path = Path(args.input)
    if not html_path.exists():
        print(f"❌ 输入文件不存在: {html_path}", file=sys.stderr)
        return 1

    if args.check:
        if not _run_self_check(html_path):
            return 1

    png_path = Path(args.output)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    render(html_path, png_path, args.scale, args.svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
