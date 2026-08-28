---
name: doc-html-pdf
description: 通用文档排版 Skill：把任意 Markdown 蒸馏为结构化 JSON，再用内置多色主题渲染为排版精美的 HTML（A4 打印样式）+ PDF。适用于产品说明、使用教程、技术白皮书、研究报告、操作手册等长文档。内置 6 套主题（emerald 翠绿 / blue 海蓝 / violet 紫罗兰 / rose 玫瑰 / amber 琥珀 / slate 石墨），支持封面/目录/表格/Callout/数据卡/步骤条/代码块/FAQ 等组件。不绑定任何具体项目。
version: 2.0.0
created: 2026-08-04
---

# doc-html-pdf · 通用文档排版

> 任意 Markdown → 结构化 JSON → 精美 **HTML + PDF**。不绑定任何项目，只负责排版。

## 核心特性

- **通用输入** - 支持 YAML frontmatter（标题/作者/版本/日期自动读取）、中文/数字章节编号、段落自动合并、表格/列表/代码块/引用块自动识别
- **蒸馏形式** - Markdown 源按 `cover / toc / sections / blocks` 结构化字段蒸馏为 JSON，避免 Markdown 写排版细节导致样式漂移；`kind` 只是元信息，可任意填写
- **双格式输出** - 单次执行产出 HTML（打印样式 + A4 分页）+ PDF（Chromium 编译，封面/目录独立页）
- **多色主题** - 内置 3 套配色（emerald 默认 / blue / slate），同一份 JSON 换主题即换风格，结构/内容完全一致
- **离线优先** - 所有资源走本地，不引外部 CDN，HTML 双击即可打开，PDF 不依赖外部字体

## 环境依赖

```bash
pip install jinja2 playwright
playwright install chromium    # 首次需安装 Chromium（PDF 编译用）
```

## 目录结构

```
doc-html-pdf/
├── SKILL.md                    # 本文件（Skill 主入口）
├── README.md                   # 使用说明
├── assets/
│   └── katex/                  # KaTeX 本地资源（离线渲染数学公式，含 woff2 字体）
├── themes/                     # 3 套配色方案
│   ├── emerald.json            # 默认主题（清新自然绿）
│   ├── blue.json               # 海蓝深邃
│   └── slate.json              # 石墨冷峻
├── templates/
│   └── doc.html.j2             # 主模板（封面/目录/章节/组件）
├── content/                    # 蒸馏后的结构化内容（可自定义）
│   ├── example.json            # 全组件演示示例
│   └── math-paper.json         # 完整数学论文示例（含公式 + 架构图）
├── examples/
│   └── math-paper.md           # 数学论文 Markdown 源文件（可直接蒸馏复现）
├── scripts/
│   ├── distill.py              # Markdown → JSON 蒸馏工具
│   └── build.py                # HTML + PDF 生成器
└── output/                     # 默认输出目录（运行时生成）
```

> **数学公式已本地化**：KaTeX 0.18.1 已内置在 `assets/katex/`（约 0.35MB），公式渲染完全离线，无需 CDN。

## 快速使用

### 1. 蒸馏 Markdown 为结构化 JSON

```bash
python scripts/distill.py \
    --md "d:/path/to/文档.md" \
    --out content/文档.json \
    --kind report
```

- `--kind` 仅作封面 kicker 元信息，任意填写（report / user-guide / whitepaper…）
- Markdown 顶部支持 frontmatter：

```markdown
---
title: 项目研究报告
subtitle: Project Research Report
version: v1.0.0
date: 2026-08-04
author: 张三
school: 示例大学
class: 示例班级
---
```

### 2. 渲染 HTML + PDF

```bash
# 默认 emerald 主题，HTML + PDF
python scripts/build.py --content content/文档.json

# 指定主题 / 格式 / 输出目录
python scripts/build.py --content content/文档.json --theme slate --format pdf
python scripts/build.py --content content/文档.json --theme blue --format html --out build/

# 分页模式：默认连续流动（学术论文惯例，杜绝页尾大片空白）
python scripts/build.py --content content/文档.json --no-flow   # 每章强制换页（报告/手册风格）
```

### 3. 批量生成（content/ 下全部 × 全部主题）

```bash
python scripts/build.py --batch --format all
python scripts/build.py --themes    # 列出可用主题
```

## 内置主题

| ID | 名称 | 9 档色阶 | 适合场景 |
|----|------|---------|---------|
| `emerald` | 翠绿森林 | #ecfdf5 → #064e3b | **默认**，产品说明/教程/学习类 |
| `blue` | 海蓝深邃 | #eff6ff → #1e3a8a | 学术/技术/研究报告 |
| `slate` | 石墨冷峻 | #f8fafc → #0f172a | 数据报告/审计/安全合规 |

## 蒸馏 JSON 规范

`kind` 任意；`meta` 全部字段可缺省（缺省时封面自动隐藏对应行）；`cover.stats` 自动统计章节数/块数。

```json
{
  "kind": "report",
  "meta": {
    "title": "项目研究报告",
    "subtitle": "Project Research Report",
    "brand": "报告标题（页脚显示）",
    "logo": "报",
    "version": "v1.0.0",
    "date": "2026-08-04",
    "author": "张三",
    "school": "示例大学",
    "class": "示例班级"
  },
  "cover": {
    "kicker": "REPORT",
    "title": "项目研究报告",
    "subtitle": "Project Research Report",
    "stats": [{ "num": "5", "label": "章节", "sub": "Sections" }]
  },
  "preamble": [
    { "type": "paragraph", "text": "第一个章节之前的引言内容（可选，自动渲染为"前言"页）" }
  ],
  "toc": [{ "num": "一", "title": "研究背景" }],
  "sections": [
    {
      "num": "一",
      "title": "研究背景",
      "level": 1,
      "blocks": [
        { "type": "paragraph", "text": "正文段落……" },
        { "type": "table", "headers": ["列1", "列2"], "rows": [["a", "b"]] },
        { "type": "callout", "variant": "info", "title": "重点", "text": "……" },
        { "type": "list", "variant": "check", "title": "要点", "items": ["…"] }
      ]
    }
  ]
}
```

### blocks.type 组件清单

| type | 说明 | 关键字段 |
|------|------|---------|
| `paragraph` | 段落 | text |
| `heading` | 小节标题 | num / text |
| `table` | 表格 | headers / rows |
| `list` | 列表（bullet/numbered/check/cross） | variant / items / title |
| `callout` | 提示框（info/warn/tip） | variant / title / text |
| `kv` | 键值对 | items[{key,value}] |
| `data-card-grid` | 数据卡网格（2-4 列自适应） | items[{title,icon,items[]}] |
| `steps` | 横向步骤条 | items[] |
| `code-block` | 代码块 | lang / code / title |
| `math` | 数学公式（KaTeX 渲染） | tex / display |
| `architecture` | 层式架构图（纯 CSS，打印友好） | title / layers[{name,items[]}] |
| `faq` | 问答 | items[{q,a}] |

## 数学公式（KaTeX）

Markdown 源文件里直接写 LaTeX，蒸馏与构建全程离线渲染：

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

Markdown 里用 ```` ```arch ```` 语言代码块定义（`层名: 模块A | 模块B`，标题跟在 arch 后）：

````markdown
```arch 系统总体架构
应用层: Web 前端 | 移动端 | API 网关
服务层: RAG 引擎 | 向量检索 | LLM 调度
数据层: 文档库 | 向量数据库 | 元数据存储
```
````

渲染为层式架构图（左标签 + 模块横排 + 层间箭头），纯 CSS 实现，PDF 打印不依赖任何脚本。

## 完整论文示例

`examples/math-paper.md` 是一篇完整的 RAG 智能问答系统论文（摘要/引言/相关工作/架构图/核心方法公式/实验表格/结论/参考文献），覆盖数学公式与架构图全部能力：

```bash
python scripts/distill.py --md examples/math-paper.md --out content/math-paper.json --kind paper
python scripts/build.py --content content/math-paper.json --theme emerald --format all
```

## 设计原则

- **内容纯净** - Skill 不携带任何项目数据，content/ 只放通用示例，正式内容由用户 distill 生成
- **多主题等价** - 同一份 JSON 在任意主题下渲染结构/内容完全一致，只换颜色
- **离线优先** - 不引外部 CDN，HTML 双击即开，PDF 不依赖外部字体
- **打印友好** - A4 纸面设计；正文默认连续流动分页（学术论文惯例，杜绝页尾大片空白），封面/目录独立整页；如需报告/手册式每章换页用 `--no-flow`

## 自定义主题

在 `themes/` 下新建 `xxx.json`（参考 emerald.json 的字段：scale 9 档色阶 + primary/cover_gradient 等），`build.py --theme xxx` 即可直接使用，无需改代码。
