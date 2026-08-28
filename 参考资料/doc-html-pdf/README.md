# doc-html-pdf · 使用说明

> 通用文档排版 Skill · v2.0.0 · 任意 Markdown → 精美 HTML + PDF

## 一句话说明

把任意 Markdown 蒸馏为结构化 JSON，再用 6 套主题色模板渲染为 **HTML + PDF**（A4 纸面，封面/目录独立页）。

## 适用场景

| 场景 | 怎么做 |
|------|--------|
| 产品说明 / 合规文档 | 写 Markdown → `distill.py` → `build.py --theme emerald` |
| 使用教程 / FAQ | 写 Markdown → `distill.py --kind user-guide` → `build.py` |
| 技术白皮书 / 研究报告 | `build.py --theme blue` 或 `--theme slate` |
| 多主题对比预览 | `build.py --batch` 一次生成 content/ 全部 × 6 主题 |
| 网页嵌入 / 打印 | 直接使用 `output/*.html` / `output/*.pdf` |

## 安装依赖（一次性）

```bash
pip install jinja2 playwright
playwright install chromium
```

## 命令速查

```bash
# 蒸馏（Markdown → JSON）
python scripts/distill.py --md <md路径> --out content/<名称>.json --kind <类型>

# 单文档生成（默认 emerald 主题，HTML+PDF）
python scripts/build.py --content content/<名称>.json

# 指定主题 / 仅 PDF / 自定义输出目录
python scripts/build.py --content content/<名称>.json --theme slate --format pdf
python scripts/build.py --content content/<名称>.json --theme blue --format html --out build/

# 分页模式：默认连续流动（学术论文惯例，杜绝页尾空白）；每章换页加 --no-flow
python scripts/build.py --content content/<名称>.json --no-flow

# 批量生成（content/ 全部 × 6 主题）
python scripts/build.py --batch --format all

# 列出可用主题
python scripts/build.py --themes
```

## 快速体验

仓库自带两个示例，直接跑：

```bash
# 示例一：全组件演示（段落/表格/Callout/数据卡/步骤条/代码块/FAQ/公式/架构图）
python scripts/build.py --content content/example.json --theme emerald --format all

# 示例二：完整数学论文（摘要/公式/架构图/实验表格/参考文献）
python scripts/build.py --content content/math-paper.json --theme emerald --format all
```

打开 `output/example-emerald.html` / `output/example-emerald.pdf` 或 `output/math-paper-emerald.html` / `output/math-paper-emerald.pdf` 即可查看完整排版效果。数学论文的 Markdown 源在 `examples/math-paper.md`，可自行蒸馏复现。

## Markdown 源文件写法

顶部可写 YAML frontmatter（可选，缺省字段封面自动隐藏）：

```markdown
---
title: 项目研究报告
subtitle: Project Research Report
version: v1.0.0
date: 2026-08-04
author: 张三
school: 示例大学
---

# 项目研究报告

## 一、研究背景

正文段落……

> **重点提示** 引用块自动转为 Callout 提示框。

| 列1 | 列2 |
|-----|-----|
| a   | b   |
```

- `#` 文档标题，`##` 章节（支持"一、"、"1."、"第一章"、无编号），`###` 小节
- 连续段落自动合并为一段
- 表格、列表（`-`/`1.`）、代码块（```` ``` ````）、引用块（`>`）自动识别
- 数学公式：行内 `$...$`、块级 `$$...$$`（KaTeX 本地离线渲染，公式中裸 `<`/`>` 自动转义，如 `a_{<t}` 无需手动处理）
- 架构图：```` ```arch ```` 语言代码块（`层名: 模块A | 模块B`，标题跟在 arch 后）

## 数学公式（KaTeX）

Markdown 源文件里直接写 LaTeX，全程离线渲染，不依赖 CDN：

```markdown
行内公式：欧拉恒等式 $e^{i\pi} + 1 = 0$

块级公式（单行或跨行均可）：

$$
\text{sim}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \cdot \|\mathbf{d}\|}
$$
```

- **行内**：`$...$`；**块级**：`$$...$$`（自动居中，独立成块）
- 公式中的裸 `<`/`>`（如 `a_{<t}`）自动转换为 `\lt`/`\gt` 渲染，无需手动转义
- 长公式建议用 `\begin{aligned}` 手动断行，避免超宽

## 架构图

Markdown 里用 ```` ```arch ```` 语言代码块定义（`层名: 模块A | 模块B`）：

````markdown
```arch 系统总体架构
应用层: Web 前端 | 移动端 | API 网关
服务层: RAG 引擎 | 向量检索 | LLM 调度
数据层: 文档库 | 向量数据库 | 元数据存储
```
````

渲染为层式架构图（左标签 + 模块横排 + 层间箭头），纯 CSS 实现，PDF 打印不依赖任何脚本。

## 主题选择指南

| 场景 | 推荐主题 | 理由 |
|------|---------|------|
| 产品说明 / 教程 | `emerald` | 清新自然绿，默认 |
| 学术报告 / 技术分享 | `blue` | 经典学术蓝，稳重 |
| 设计 / 创意比赛 | `violet` | 艺术感强 |
| 情感 / 阅读主题 | `rose` | 温润亲和 |
| 教学 / 科普 | `amber` | 暖色友好 |
| 审计 / 数据安全 | `slate` | 冷峻专业 |

## 蒸馏后修改内容

- **改内容不改结构**：直接编辑 `content/*.json`，所有主题产物同步更新
- **新增组件类型**：编辑 `templates/doc.html.j2` 在 block 分支中加渲染分支，再在 JSON 的 `sections[].blocks[]` 中使用
- **新增主题**：复制 `themes/emerald.json` 改名改色阶即可，无需改代码
