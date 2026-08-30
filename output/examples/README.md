# harryopo-office 示例文档产物

本目录是 **harryopo-office skill 官方示例** 的完整产物（源 MD 即本目录 `*.md`），由最新 skill 统一渲染，五份示例均为 **Word + PDF + LaTeX 三格式齐全**：

| 示例 | Word | PDF (paper) | PDF (report) | LaTeX 源码 |
|------|------|-------------|--------------|------------|
| 论文单栏 | paper-single-column-word.docx | paper-single-column-paper.pdf | — | paper-single-column-paper.tex |
| 论文双栏 | paper-twocolumn-word.docx | paper-twocolumn-paper.pdf | — | paper-twocolumn-paper.tex |
| 论文全特性 | paper-showcase-word.docx | paper-showcase-paper.pdf | — | paper-showcase-paper.tex |
| 报告 | report-word.docx | — | report-paper.pdf | report-report.tex |
| 报告全特性 | report-showcase.processed-word.docx | — | report-showcase.processed-paper.pdf | report-showcase.processed-report.tex |

**2026-08-30 更新（主流程规范落地）**：

- **框架图**：paper-showcase / report-showcase 的架构图由 ASCII 字符画升级为 **super-diagram 契约渲染的真框架图**（` ```super-diagram ` JSON 块 → 管线自动渲染 PNG → 图注 + `> 注：` 注释，见 `figures/`）；report-showcase 另含 Mermaid 业务流程图
- **注释规范**：表注 / 图注统一渲染在**表格 / 图片下方**（`> 注：` 语法），两个 showcase 各有示范
- 文件名带 `.processed`：因文档含图表代码块，渲染时先预处理为 PNG 再编译；`figures/` 存放渲染出的图片

## 重新生成

```bash
# 前置依赖：python-docx / latex2mathml / pywin32 / playwright（+chromium）
python .trae/skills/harryopo-office/scripts/office.py render output/examples/paper-showcase.md --format word,paper
python .trae/skills/harryopo-office/scripts/office.py render output/examples/report-showcase.md --format word,paper --type report
```

> 注意：图表块渲染失败会**硬失败退出**（不静默降级），避免 JSON 源码混入文档；playwright chromium 用 `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright python -m playwright install chromium` 安装。

## 查看

- **Word**：直接双击打开
- **PDF**：直接双击打开
- **LaTeX**：用 VS Code + LaTeX Workshop 打开 `.tex`，点 ▶ 编译预览
- **MD**：用 Markdown Preview Enhanced + `harryopo-preview.css` 预览内容结构

详细说明与元信息约定见 [templates/previews/README.md](../../.trae/skills/harryopo-office/templates/previews/README.md)。
