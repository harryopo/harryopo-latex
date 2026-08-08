# AI 生成办公文档（Word/PPT/PDF/LaTeX）深度调研报告

> **调研日期**：2026-08-08
> **调研范围**：GitHub 高星开源项目（2024-2026 活跃）、商业 SaaS 产品、AI Agent 生态最佳实践、Markdown→高质量排版转换链路
> **调研方法**：多轮全网搜索（WebSearch + GitHub API 数据核实），覆盖英文与中文关键词，涉及 30+ 开源项目和 10+ 商业产品

---

## 目录

1. [核心发现摘要](#1-核心发现摘要)
2. [GitHub 高星开源项目调研](#2-github-高星开源项目调研)
   - 2.1 [PDF 生成（LaTeX / Typst / WeasyPrint / PagedJS）](#21-pdf-生成latextypstweasyprintpagedjs)
   - 2.2 [Word/docx 生成（模板驱动）](#22-worddocx-生成模板驱动)
   - 2.3 [PPT/pptx 生成（现代方案）](#23-pptpptx-生成现代方案)
   - 2.4 [LaTeX 论文/报告/书籍生成](#24-latex-论文报告书籍生成)
   - 2.5 [综合型 AI 文档生成框架](#25-综合型-ai-文档生成框架)
3. [商业产品和 SaaS 方案分析](#3-商业产品和-saas-方案分析)
4. [AI Agent 生态的文档生成最佳实践](#4-ai-agent-生态的文档生成最佳实践)
5. [Markdown → 高质量排版文档的最佳转换链路](#5-markdown--高质量排版文档的最佳转换链路)
6. [全景对比表格](#6-全景对比表格)
7. [推荐排名](#7-推荐排名)
8. [结论：办公超级 Skill 的最佳集成方案](#8-结论办公超级-skill-的最佳集成方案)

---

## 1. 核心发现摘要

经过对 30+ 开源项目和 10+ 商业产品的深入调研，得出以下核心判断：

**技术趋势**：
- **Typst 已成为 LaTeX 最有力的挑战者**（55.3K stars，2025 年 GitHub 增长最快的排版语言之一），编译速度比 LaTeX 快 3-100 倍，正在被 Zerodha 等公司用于日生成 150 万份 PDF 的生产场景。
- **Pandoc 依然是万能格式转换中枢**（45.8K stars），其 `--reference-doc` 机制是实现"Markdown → 品牌化 Word"的最佳链路。
- **PPT 生成正在从"文本堆砌"走向"编辑式生成"**——中科院的 PPTAgent（4.9K stars）提出了分析参考 PPT 结构再编辑生成的新范式，远超传统的文本摘要式方法。
- **Presenton（9.4K stars）和 ALLWEONE（2.9K stars）正在成为 Gamma 的开源替代品**，采用 HTML + Tailwind CSS 渲染幻灯片，而非传统的 python-pptx 堆砌。

**设计质量的核心洞察**：
> **AI 擅长内容，但不擅长设计**。几乎所有高质量方案的本质都是：**用模板/主题系统锁定设计质量，让 AI 只负责内容生成。**

- Beautiful.ai 的"Smart Slides"通过**设计约束**保证输出不丑——添加内容时布局自动重排。
- Gamma 的核心是 **"outline gate"（大纲审查门控）**——先生成大纲供人工确认，再生成幻灯片，避免结构错误被"放大"成成品。
- Typst/LaTeX 方案的美观来自**经过设计的模板**，而非 AI 的即兴排版。

---

## 2. GitHub 高星开源项目调研

### 2.1 PDF 生成（LaTeX/Typst/WeasyPrint/PagedJS）

#### Typst — 现代 LaTeX 替代品 ⭐ 55,341

| 属性 | 详情 |
|------|------|
| **仓库** | [typst/typst](https://github.com/typst/typst) |
| **Stars** | 55,341 |
| **技术栈** | Rust（编译器）/ 标记语言 |
| **最后更新** | 2026-08-07（极高活跃度） |
| **许可** | Apache-2.0 |

**核心亮点**：
- 编译速度极快：增量编译毫秒级；2000+ 页大文档约 1 分钟（LaTeX/lualatex 需 18 分钟）
- 语法类似 Markdown，学习曲线远低于 LaTeX
- 内置脚本语言，支持程序化文档生成（数据驱动报告）
- **Typst Universe 生态**：800+ 社区包和模板（学术论文、演示文稿、书籍、简历等）
- 单一静态二进制，无需安装 TeX 发行版（Docker 镜像极小）
- 原生 Unicode + PDF 支持，中文友好
- 被 3500+ 大学和 1000+ 企业采用

**模板机制**：✅ 强大的模板系统（`#show` 规则 + 函数式组件）
**中文支持**：✅ 原生支持，字体通过 `typst fonts` 管理
**局限**：缺乏 LaTeX 的 TikZ 级别矢量图形能力；期刊投稿模板覆盖不如 LaTeX

> **生产案例**：Zerodha（印度最大券商）用 Typst 每天生成 150 万份 PDF，编译时间从 LaTeX 的数小时降至 25 分钟。详见 [zerodha.tech 博客](https://zerodha.tech/blog/1-5-million-pdfs-in-25-minutes)。

---

#### Pandoc — 万能文档格式转换中枢 ⭐ 45,768

| 属性 | 详情 |
|------|------|
| **仓库** | [jgm/pandoc](https://github.com/jgm/pandoc) |
| **Stars** | 45,768 |
| **技术栈** | Haskell |
| **最后更新** | 2026-08-07（极高活跃度） |
| **许可** | GPL-2.0+ |

**核心亮点**：
- 支持 40+ 格式互转：Markdown ↔ DOCX ↔ PDF ↔ HTML ↔ LaTeX ↔ PPTX ↔ EPUB ↔ Beamer ↔ Reveal.js...
- **`--reference-doc` 机制**：用品牌化的 `reference.docx` 作为样式参考，生成的 Word 自动继承所有样式（字体、颜色、页眉页脚）
- **Lua Filter 生态**：可在转换过程中插入自定义处理逻辑（交叉引用、图表编号、Mermaid 渲染等）
- 支持 YAML 元数据块和学术引用（`--citeproc` + `.bib`）
- 已被 [mcp-pandoc](https://github.com/vivekVells/mcp-pandoc) 封装为 MCP Server，可直接供 Claude Code/Cursor 调用

**模板机制**：✅ 内置模板系统 + `--reference-doc` 参考文档 + `--template` 自定义模板
**中文支持**：✅ 通过 XeLaTeX 引擎支持（PDF 需安装 TeX 发行版）

> **最佳实践链路**：`Markdown → pandoc --reference-doc=brand.docx → 品牌化 Word` 或 `Markdown → pandoc --pdf-engine=xelatex --template=report.tex → 高质量 PDF`

---

#### WeasyPrint — HTML/CSS → PDF 排版引擎 ⭐ 9,473

| 属性 | 详情 |
|------|------|
| **仓库** | [Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint) |
| **Stars** | 9,473 |
| **技术栈** | Python（后端 Cairo/Pango） |
| **最后更新** | 2026-08-07（极高活跃度） |
| **许可** | BSD-3-Clause |

**核心亮点**：
- 将 HTML + CSS 精准渲染为 PDF，特别擅长**分页、页眉页脚、字体嵌入**等印刷需求
- 支持 CSS Paged Media 模块（`@page`、`@bottom-center`、`counter(page)` 等）
- 纯 Python 进程，无需启动 Chromium（比 Puppeteer 轻量得多）
- 月下载量 2500 万次，15 年历史，极其稳定
- 适合：报表、发票、票据、书籍、信件、海报

**模板机制**：✅ 通过 HTML 模板 + CSS 样式表实现
**中文支持**：✅ 需通过 `@font-face` 引入中文字体（如思源黑体）

> **配套项目**：[md2pdf (rvsr5)](https://github.com/rvsr5/md2pdf) — 基于 python-markdown + WeasyPrint + Pygments 的 CLI，内置 light/dark/github 三主题。[markdown2pdf (leohuang8688)](https://github.com/leohuang8688/markdown2pdf) — 集成 WeasyPrint + Noto Color Emoji 的 OpenClaw Skill。

---

#### PagedJS — HTML → 印刷级 PDF

| 属性 | 详情 |
|------|------|
| **官网** | [pagedjs.org](https://pagedjs.org) |
| **技术栈** | JavaScript（浏览器/headless） |
| **维护** | Adam Hyde 创立，Julien Taquet / Fred Chasen / Gijs de Heij 维护 |

**核心亮点**：
- 专门实现 W3C CSS Paged Media 规范的 JavaScript 库
- 将 HTML 文档转换为**符合印刷标准的 PDF**
- 开源、尊重标准、社区驱动
- 适合书籍出版、杂志、学术报告等需要精细分页控制的场景
- 比 WeasyPrint 更适合复杂印刷排版（脚注跨页、浮动元素等）

**模板机制**：✅ 通过 CSS Paged Media 规范实现
**中文支持**：✅ 取决于浏览器字体配置

---

### 2.2 Word/docx 生成（模板驱动）

#### poi-tl — Java Word 模板引擎 ⭐ 5,129

| 属性 | 详情 |
|------|------|
| **仓库** | [Sayi/poi-tl](https://github.com/Sayi/poi-tl) |
| **Stars** | 5,129 |
| **技术栈** | Java（基于 Apache POI） |
| **最后更新** | 2026-07-15（活跃） |
| **许可** | Apache-2.0 |

**核心亮点**：
- **Word 原生模板引擎**：在 Word 中用 `{{变量名}}` 标记占位符，poi-tl 保留模板所有样式并填充数据
- 完美保留模板中的字体、颜色、表格、图片、页眉页脚
- 支持文本、图片、表格、列表、循环（`{{?list}}...{{/list}}`）、条件渲染
- 有 Markdown 插件（poi-tl-plugin-markdown）和代码高亮插件
- 中文社区活跃，文档完善

**模板机制**：✅ 核心能力——Word 文档即模板
**中文支持**：✅ 原生支持

> **为什么输出"不丑"**：因为样式完全由设计师在 Word 中定义，poi-tl 只负责数据替换，不触碰任何样式。

---

#### python-docx-template (docxtpl) — Python Word 模板

| 属性 | 详情 |
|------|------|
| **仓库** | [eliasorel/docxtpl](https://github.com/eliasorel/docxtpl) |
| **Stars** | ~2,000+ |
| **技术栈** | Python（基于 python-docx + Jinja2） |
| **活跃度** | 持续维护 |

**核心亮点**：
- 用 Jinja2 模板语法（`{{ var }}`、`{% for %}`）在 Word 中标记
- 保留 Word 原生样式，支持富文本、图片、表格、内联样式
- Python 生态最流行的 Word 模板方案
- 有 [Rust 实现 docxtplrs](https://github.com/yiyinzhang/docxtplrs)（PyO3 绑定，性能提升数倍）

**模板机制**：✅ Jinja2 模板 + Word 样式
**中文支持**：✅ 原生支持

---

#### OpenThesis — AI 文档模板引擎

| 属性 | 详情 |
|------|------|
| **仓库** | [1771902720-lgtm/OpenThesis](https://github.com/1771902720-lgtm/OpenThesis) |
| **Stars** | 新项目（增长中） |
| **技术栈** | Node.js / TypeScript |
| **最后更新** | 2026-07-07 |

**核心亮点**：
- **"模板理解"而非"模板填充"**——知道什么是标题、摘要、发文字号
- 解析任意 `.docx` 模板，用结构化 JSON 写入，导出可直接提交的 DOCX
- 面向毕业论文、期刊文章、政府公文
- 自动处理字体、页边距、页眉、页码、表格格式、公式渲染
- 支持 GB/T 9704-2012 公文格式标准

**模板机制**：✅ 核心能力——解析并理解模板结构
**中文支持**：✅ 深度优化（公文、论文）

---

#### dgdoc — HTML → Word/PPT/Excel 全格式转换

| 属性 | 详情 |
|------|------|
| **仓库** | [dgmosdev/dgdoc](https://github.com/dgmosdev/dgdoc) |
| **Stars** | 新项目 |
| **技术栈** | Go |
| **最后更新** | 2026-01-14 |

**核心亮点**：
- 将 HTML 表格、列表、图片、样式无缝转换为**原生 Word 元素**
- 同时支持 DOCX、PPTX、XLSX、ODT 输出
- 支持 `{#if}` 条件渲染、`{#items}` 循环
- Go 实现，性能好，单二进制部署

---

### 2.3 PPT/pptx 生成（现代方案）

#### PPTAgent — 学术级 PPT 编辑式生成 ⭐ 4,896

| 属性 | 详情 |
|------|------|
| **仓库** | [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent) |
| **Stars** | 4,896 |
| **技术栈** | Python |
| **最后更新** | 2026-08-03（活跃） |
| **论文** | [arXiv:2501.03936](https://arxiv.org/abs/2501.03936) |
| **许可** | MIT |

**核心亮点**：
- **中科院软件所出品**，提出了"编辑式生成"（edit-based）新范式
- 两阶段方法：① 分析参考 PPT 的结构模式和内容 Schema → ② 通过代码动作（code actions）编辑生成幻灯片
- 同时推出 **PPTEval 评估框架**，从内容、设计、连贯性三维度评估
- 输入支持 PDF/DOCX/Markdown/TXT，输出专业级 .pptx 或 .pdf
- 论文发表于 2025 年，被广泛引用

**为什么输出"不丑"**：通过分析真实参考 PPT 的布局模式，学习"好的设计长什么样"，然后在参考框架内编辑，而非从零生成。

**模板机制**：✅ 以参考 PPT 为模板
**中文支持**：✅ 中科院项目，原生中文支持

---

#### Presenton — 开源 AI 演示文稿生成器 ⭐ 9,428

| 属性 | 详情 |
|------|------|
| **仓库** | [presenton/presenton](https://github.com/presenton/presenton) |
| **Stars** | 9,428 |
| **技术栈** | TypeScript / Python / Docker |
| **最后更新** | 2026-08-07（极高活跃度） |
| **许可** | Apache-2.0 |

**核心亮点**：
- **Gamma / Beautiful.ai / Decktopus 的开源替代品**
- 使用 **HTML + Tailwind CSS** 创建幻灯片设计（而非 python-pptx），设计自由度高
- 支持从现有 PPTX 文件提取模板设计
- 多模型支持：OpenAI / Gemini / Claude API + Ollama 本地模型
- 支持 PPTX 和 PDF 格式导出
- 提供 REST API，可程序化调用
- Docker 一键部署，支持 GPU 加速

**为什么输出"不丑"**：用 Web 技术（HTML/CSS）渲染幻灯片，天然拥有现代 Web 设计能力，远超 python-pptx 的排版能力。

**模板机制**：✅ 内置 general 等模板 + 从 PPTX 提取模板
**中文支持**：✅ 支持 `language=Chinese` 参数

---

#### ALLWEONE presentation-ai — Gamma 开源替代 ⭐ 2,928

| 属性 | 详情 |
|------|------|
| **仓库** | [allweonedev/presentation-ai](https://github.com/allweonedev/presentation-ai) |
| **Stars** | 2,928 |
| **技术栈** | Next.js / TypeScript / Prisma / PostgreSQL |
| **最后更新** | 2026-06-05 |
| **许可** | 开源 |

**核心亮点**：
- 输入主题 → AI 自动生成大纲 → 审查编辑 → 选择主题 → 生成完整幻灯片
- 9 种内置设计主题 + 自定义主题创建
- 支持本地大模型（Ollama / LM Studio）
- AI 图像生成集成
- 实时生成过程可视化
- 拖放排序、完整编辑功能

**模板机制**：✅ 9 内置主题 + 自定义
**中文支持**：✅ 多语言

---

#### Slidev — 开发者友好的 Markdown 演示框架 ⭐ 48,005

| 属性 | 详情 |
|------|------|
| **仓库** | [slidevjs/slidev](https://github.com/slidevjs/slidev) |
| **Stars** | 48,005 |
| **技术栈** | Vue 3 / Vite / TypeScript |
| **最后更新** | 2026-08-05（极高活跃度） |
| **许可** | MIT |

**核心亮点**：
- **Markdown → 现代化 Web 演示文稿**
- 基于 Vue 3 + Vite，支持 Vue 组件嵌入幻灯片
- 代码高亮、Live Code（实时运行代码）、动画、注释
- 丰富的主题生态（seriph、apple-basic、bricks 等）
- 导出 PDF / PPTX / PNG / SPA
- 内置演讲者录音、绘图、激光笔
- **注意**：PPTX 导出将幻灯片转为图片，文本不可选

**为什么输出"不丑"**：Web 技术渲染 + 精心设计的主题 = 现代、美观的演示文稿。
**模板机制**：✅ 主题系统（`theme: seriph`）+ 自定义 Vue 组件
**中文支持**：✅ 支持

> **AI 结合**：已有 [Next-AI-Slide](https://github.com/lvy010/Next-AI-Slide) 等项目用 AI 生成 Slidev 演示文稿；Cursor + Slidev 是技术演讲的高效工作流。

---

#### Marp — 最简洁的 Markdown 演示生态

| 属性 | 详情 |
|------|------|
| **仓库** | [marp-team/marp-cli](https://github.com/marp-team/marp-cli) |
| **Stars** | 3,738（CLI）/ 1,138（core） |
| **技术栈** | TypeScript / Node.js |
| **最后更新** | 2026-08-07（极高活跃度） |
| **许可** | MIT |

**核心亮点**：
- **Markdown → HTML / PDF / PPTX / 图片**，零配置上手
- VS Code 扩展实时预览（`Marp for VS Code`）
- 支持 CSS 主题定制、KaTeX 数学公式、图片背景
- 语法极简：`---` 分隔幻灯片，frontmatter 配置主题
- 有"editable PPTX"模式（但官方警告可复现性较低）

**为什么输出"不丑"**：内置精心设计的默认主题 + CSS 自定义能力。
**模板机制**：✅ CSS 主题系统
**中文支持**：✅ 支持

> **AI 结合案例**：[Cursor × Marp 工作流](https://blog.printemps.tokyo/blog/cursor-marp-presentation-revolution) — 用 Cursor AI Agent 一键生成 50 页技术演示文稿（约 1.5 小时 vs 传统 14.5 小时）。已有 [JoseAI-Automatizaciones/marp-skill](https://github.com/JoseAI-Automatizaciones/marp-skill) 等 Claude Code Skill。

---

#### Reveal.js — 最成熟的 HTML 演示框架

| 属性 | 详情 |
|------|------|
| **仓库** | [hakimel/reveal.js](https://github.com/hakimel/reveal.js) |
| **Stars** | 67,000+（GitHub 最热门演示框架） |
| **技术栈** | JavaScript / HTML / CSS |
| **最后更新** | 2026-08-07（持续维护，超过 10 年） |

**核心亮点**：
- HTML 演示框架的标杆，支持嵌套幻灯片、Markdown 内容、PDF 导出
- 丰富的垂直滚动、幻灯片过渡动画、片段动画
- 通过 Pandoc（`pandoc -t revealjs`）或 Quarto 可从 Markdown 直接生成
- 插件生态丰富（math、search、zoom 等）

**模板机制**：✅ CSS 主题 + 配置选项
**中文支持**：✅ 支持

---

### 2.4 LaTeX 论文/报告/书籍生成

#### OpenPrism — AI 驱动的 LaTeX 学术写作工作台

| 属性 | 详情 |
|------|------|
| **仓库** | [OpenDCAI/OpenPrism](https://github.com/OpenDCAI/OpenPrism) |
| **Stars** | 新项目（增长中） |
| **技术栈** | Next.js / TypeScript |
| **最后更新** | 2026-02-11 |

**核心亮点**：
- **"Vibe Writing for Academia"** — 学术界的 AI 写作工作台
- 内置 ACL / CVPR / NeurIPS / ICML 等顶会模板，一键切换
- 支持 TexLive / Tectonic 自动编译 + PDF 预览
- **模板迁移**：双模式——Legacy（LaTeX→LaTeX）和 MinerU（PDF→Markdown→LaTeX）
- LLM 驱动内容迁移 + 自动编译错误修复 + VLM 版面检查
- CRDT 实时多人协作
- AI 审稿报告（一致性检查、缺失引用检测）

**模板机制**：✅ 顶会模板一键切换 + 模板迁移
**中文支持**：✅ 提供中文 README

---

#### Auto-Academic-Paper — 一键生成可发表 LaTeX 论文

| 属性 | 详情 |
|------|------|
| **仓库** | [keithligh/Auto-Academic-Paper](https://github.com/keithligh/Auto-Academic-Paper) |
| **Stars** | 增长中 |
| **技术栈** | TypeScript（全栈） |
| **最后更新** | 2026-02-13 |

**核心亮点**：
- 输入一份草稿（Markdown / PDF / TXT）→ 输出**可发表、格式完美、引用验证、TikZ 精美的 LaTeX 论文**
- 多 Agent 协作：模仿"永不疲倦的 PhD 团队"
- 自动处理引用验证、TikZ 图表、表格溢出、CJK 排序
- 反幻觉机制（ANTI_HALLUCINATION.md）

**模板机制**：✅ 学术论文模板
**中文支持**：✅ 支持 CJK

---

#### AI-Scientist-v2 — 端到端科研 Agent（含论文生成）

| 属性 | 详情 |
|------|------|
| **仓库** | [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) |
| **技术栈** | Python |
| **许可** | Apache-2.0 |

**核心亮点**：
- **端到端**：从构思 → 实验 → 分析 → 写论文（PDF/LaTeX）含引用
- 基于 Agent 式树搜索（agentic tree search）运行实验
- 生成 workshop 级别的完整论文
- 包含完整的引用阶段

---

#### Agent Laboratory — 自主科研框架

| 属性 | 详情 |
|------|------|
| **仓库** | [AgentLaboratory.github.io](https://agentlaboratory.github.io/) |
| **论文** | [arXiv:2501.04227](https://arxiv.org/abs/2501.04227) |
| **机构** | AMD / Johns Hopkins University |

**核心亮点**：
- 以人类研究想法为输入 → 文献综述 → 实验实施 → **报告撰写（LaTeX）**
- 成本降低 84%（每篇论文约 $2.33 使用 gpt-4o）
- 输出含 8 个标准部分（Abstract → Discussion）的 LaTeX 论文 + 代码仓库

---

### 2.5 综合型 AI 文档生成框架

#### autodocs-ai — Prompt → 美观文档

| 属性 | 详情 |
|------|------|
| **仓库** | [makieali/autodocs-ai](https://github.com/makieali/autodocs-ai) |
| **Stars** | 新项目 |
| **技术栈** | Python |
| **最后更新** | 2026-02-14 |
| **许可** | MIT |

**核心亮点**：
- 号称"第一个开源 AI 文档生成器"：一句话 Prompt → 专业格式 PDF/DOCX/HTML/Markdown
- 8 个内置模板（提案、发票、简历、报告等）
- 支持 OpenAI / Azure 多提供商
- 提供 REST API 和 Docker 部署

**模板机制**：✅ 8 内置模板
**中文支持**：⚠️ 未明确

---

#### agent-pdf — AI Agent 专用 PDF 生成 ⭐ 新兴

| 属性 | 详情 |
|------|------|
| **仓库** | [tszaks/agent-pdf](https://github.com/tszaks/agent-pdf) |
| **技术栈** | TypeScript / Node.js |
| **最后更新** | 2026-06-04 |

**核心亮点**：
- 专为 **AI Agent 设计**的 PDF 生成——"Agent 擅长内容，不擅长设计"
- 5 个精心设计的模板：report（学术海军蓝）、proposal（渐变现代）、invoice、docs（技术）、minimal
- 自动检测输入格式（Markdown / JSON / Raw HTML）
- **内置 MCP Server**，可直接接入 Claude Code
- 每个模板有独立的字体选择（Playfair Display、Source Serif、Plus Jakarta Sans、JetBrains Mono 等）

**为什么输出"不丑"**：模板由设计师精心制作，AI 只需提供内容，设计决策为零。
**模板机制**：✅ 5 个高质量模板
**中文支持**：⚠️ 未明确

---

#### Word-Cursor — AI 驱动的办公文档编辑器

| 属性 | 详情 |
|------|------|
| **仓库** | [yangzhuxinyzx/Word-Cursor](https://github.com/yangzhuxinyzx/Word-Cursor) |
| **技术栈** | Electron / React / ONLYOFFICE |
| **活跃度** | 活跃 |

**核心亮点**：
- 把 Cursor 的"对话式编辑 + 工具调用 + 可审阅变更"带入 **Word / Excel / PowerPoint**
- 从"编辑器"变成"工作流执行器"：描述意图 → AI 通过工具执行 → 结果可审阅、可回滚
- AI 修改以可视化 diff 呈现，支持接受/拒绝
- PPT 端到端：从大纲生成 PPTX → 不满意就"整页重做"或"局部编辑"
- 内置 Brave Search MCP、联网调研能力

**模板机制**：✅ PPT 模板匹配
**中文支持**：✅ 原生中文

---

## 3. 商业产品和 SaaS 方案分析

商业产品在"AI 输出美观"这个问题上积累了大量工程经验，值得开源方案借鉴。

### 3.1 国际产品

#### Gamma（gamma.app）— 最流行的 AI 演示工具

| 属性 | 详情 |
|------|------|
| **用户量** | 7000 万+用户（截至 2025 年底） |
| **收入** | $1 亿+ 年经常性收入（ARR） |
| **定价** | 免费（400 AI 积分）/ Plus ~$8/月 / Pro ~$15/月 |

**如何解决"AI 输出美观"**：
1. **Outline Gate（大纲门控）**：先生成大纲 → 人工审查修改 → 再生成幻灯片。避免错误结构被放大。
2. **Card-based 设计系统**：以卡片为单位组织内容，而非传统幻灯片，自动适配内容密度。
3. **一键重新设计**：对生成的幻灯片不满意，一键换主题/布局。
4. **100+ 主题模板 + 20+ AI 模型**可选。
5. 支持 60+ 语言。

**弱点**：PPTX 导出质量差（图表移位、字体替换、动画丢失），需要手动清理。这是 Web 原生渲染导出到传统格式的通病。

---

#### Beautiful.ai — 设计约束优先

| 属性 | 详情 |
|------|------|
| **定价** | $12/月起（无永久免费版） |

**如何解决"AI 输出美观"**：
1. **Smart Slides 技术**：每个幻灯片模板内嵌设计规则，添加/删除内容时布局自动重排。
2. **设计约束即功能**：你无法创建一个丑陋的幻灯片——系统会自动纠正对齐、间距、字号。
3. 强大的**数据可视化工具**（图表、数字布局）。
4. 品牌**一致性**：集中式模板和幻灯片母版管理。

**核心哲学**：Gamma 生成内容和设计；Beautiful.ai 让你写内容、它负责设计。

---

#### Tome — 已转型

Tome 在 2025 年 4 月**关闭了原有的幻灯片产品**，转向其他方向。搜索 Tome 替代品的用户应评估 Gamma 或 Beautiful.ai。

---

#### Canva Magic Design — 设计平台 + AI

Canva 将 AI 演示生成集成到其庞大的设计平台中，优势在于丰富的素材库、模板库和协作能力。

#### Plus AI — Google Slides / PowerPoint 原生

Plus AI 的独特定位是作为 **Google Slides 和 PowerPoint 的插件**运行，在原生环境中生成，避免了格式转换问题。

---

### 3.2 国产产品

#### WPS AI / 灵犀 — 6 亿用户的 AI 办公

| 属性 | 详情 |
|------|------|
| **用户量** | 全球 6 亿+用户 |
| **AI 渗透率** | 付费用户 AI 渗透率从 47.1% 飙升至 100%+ |
| **模型** | 2026 年 2 月接入智谱 GLM-5（7440 亿参数 MoE） |

**如何解决"AI 输出美观"**：
1. **混合模型策略**：简单任务（格式调整）走端侧小模型，复杂任务路由到云端 GLM-5。
2. **三步生成流程**：输入主题/上传文档/大纲 → AI 生成大纲供确认 → 选择场景模板 → 生成 PPT。
3. 支持**篇幅、场景、受众、风格**四个维度的定制。
4. **深度思考模式**：根据场景自动调整信息密度。
5. 内置 WPSAI 函数系列（智能分类、信息提取等）。

**PPT 生成**：12 分钟生成一份可直接汇报的 PPT；支持上传 Word/PDF 文档自动转 PPT。

---

#### 腾讯文档 AI（AIPPT）

| 属性 | 详情 |
|------|------|
| **引擎** | DeepSeek / 混元 / 混元 T1 |

**如何解决"AI 输出美观"**：
1. 上传文档 → AI 深入思考分析内容 → 生成 2-3 级标题结构大纲。
2. 4 种基础模板风格（简约扁平、商务职场、科技炫酷、严肃端庄）。
3. 编辑器功能完善，媲美桌面 Office（动画、切换效果、智能配图）。
4. 26 页 PPT 约 1 分钟生成。

**弱点**：免费模板少，大部分精美模板需付费；AI 有时"过度脑补"添加原文没有的内容。

---

#### 飞书文档 AI

飞书的 AI 能力集成在文档生态中，支持智能写作、格式统一、大纲生成等，但更偏向协作而非一键生成。

---

### 3.3 商业产品的共性设计原则（开源方案可借鉴）

| 原则 | 说明 | 代表产品 |
|------|------|---------|
| **大纲优先** | 先生成结构供审查，再生成内容 | Gamma、WPS、腾讯文档 |
| **模板/主题锁定** | 设计质量由专业模板保证，AI 不碰排版 | Beautiful.ai、Canva |
| **场景化模板** | 按"汇报/答辩/路演"等场景预设模板 | WPS、腾讯文档 |
| **Web 渲染** | 用 HTML/CSS 渲染幻灯片，导出时再转 PPTX | Gamma、Presenton |
| **渐进式生成** | 先粗稿 → 可编辑 → 局部重新生成 | Gamma、ALLWEONE |
| **人工确认门控** | 在关键节点插入人工审查步骤 | Gamma Outline Gate |

---

## 4. AI Agent 生态的文档生成最佳实践

### 4.1 Claude Code / Cursor 的 Skill 模式

在 Claude Code 和 Cursor 生态中，**Skill 是固化的高频工作流**。文档生成相关的 Skill 已经形成了一些最佳实践：

#### 已有的文档生成 Skills/插件

| Skill / 项目 | 功能 | 技术栈 |
|-------------|------|--------|
| [claude-skills (searayca)](https://github.com/searayca/claude-skills) | `/md_to_word`、`/md_to_pptx`、`/business_letter`、`/daily_summary` | python-docx / python-pptx |
| [mcp-pandoc](https://github.com/vivekVells/mcp-pandoc) | Pandoc 的 MCP Server 封装，支持 10+ 格式互转 | Python + Pandoc |
| [pdf-mcp-server (FabianGenell)](https://github.com/FabianGenell/pdf-mcp-server) | Markdown → 专业 PDF，多主题、模板系统、图片处理 | Node.js |
| [agent-pdf (tszaks)](https://github.com/tszaks/agent-pdf) | AI Agent 专用 PDF 生成，内置 MCP Server | TypeScript |
| [marp-skill (JoseAI)](https://github.com/JoseAI-Automatizaciones/marp-skill) | 用 Marp 创建专业演示文稿的 Claude Code Skill | Marp |
| [markdown2pdf (leohuang8688)](https://github.com/leohuang8688/markdown2pdf) | Markdown → PDF/PNG，5 主题，WeasyPrint 引擎 | Python + WeasyPrint |
| [Office Whisperer MCP](https://mcp.aibase.com/server/1568219613232373825) | 通过自然语言操作 Excel/Word/PPT/Outlook | MCP |
| [PPT_AutoMation (timwei0801)](https://github.com/timwei0801/PPT_AutoMation) | 基于 MCP 的多模态文档处理与简报建构 | Python + Claude API |

#### Skill 设计最佳实践（来自 Anthropic 官方文档）

根据 [Anthropic 官方 Skill 编写指南](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：

1. **简洁是关键**：Claude 已经很聪明，只添加它不知道的上下文。
2. **设置适当的自由度**：
   - 高自由度（文本指令）：多种有效方法时
   - 中自由度（伪代码/参数脚本）：有首选模式时
   - 低自由度（精确脚本）：操作脆弱、一致性关键时
3. **渐进式信息加载**：
   - Level 1：YAML 元数据（name + description）始终加载
   - Level 2：SKILL.md 正文仅在相关时加载
   - Level 3：`scripts/`、`references/`、`assets/` 仅在引用时加载
4. **测试所有目标模型**：Haiku 需要更多指引；Opus 需要避免过度解释。

#### 社区总结的办公文档 Skill 最佳实践

| 实践 | 说明 |
|------|------|
| **模板优于代码生成** | 用预制的 reference.docx / theme.css / .tex 模板，而非让 AI 从零写排版代码 |
| **分阶段输出** | 大纲确认 → 内容生成 → 格式渲染，而非一步到位 |
| **使用 Pandoc 作为中枢** | Markdown 作为中间格式，Pandoc 负责最终格式转换 |
| **绑定 MCP Server** | 将文档生成能力封装为 MCP Server，供所有 Agent 调用 |
| **diff 审阅机制** | AI 的修改以 diff 呈现，支持接受/拒绝 |

---

## 5. Markdown → 高质量排版文档的最佳转换链路

这是本次调研最重要的实践结论之一。以下是从"结构化内容"到"高质量排版文档"的最佳链路，按目标格式分类：

### 5.1 Markdown → Word（品牌化 DOCX）

**推荐链路 A（Pandoc 参考文档）**：
```
Markdown → pandoc --reference-doc=brand-template.docx --output=result.docx
```
- 先用 `pandoc -o reference.docx --print-default-data-file reference.docx` 生成默认参考文档
- 在 Word 中编辑参考文档的样式（标题、正文、表格、页眉页脚）
- 之后所有转换自动继承品牌样式

**推荐链路 B（python-docx-template / poi-tl）**：
```
JSON 数据 → Jinja2 模板引擎 → docxtpl/poi-tl → 品牌化 DOCX
```
- 适合数据驱动的批量生成（报表、合同、证书）

### 5.2 Markdown → PDF（高质量排版）

**推荐链路 A（LaTeX 引擎）**：
```
Markdown → pandoc --pdf-engine=xelatex --template=report.tex --output=result.pdf
```
- 排版质量最高，适合学术论文、书籍
- 需要安装 TeX 发行版（TeX Live / MiKTeX）

**推荐链路 B（Typst 引擎）**：
```
Markdown → 转换为 Typst 标记 → typst compile → result.pdf
```
- 编译速度最快，适合 CI/CD 和批量生成
- 模板来自 Typst Universe

**推荐链路 C（HTML/CSS 引擎）**：
```
Markdown → python-markdown → HTML + CSS → WeasyPrint → result.pdf
```
- Web 开发者友好，用 CSS 控制排版
- 适合报表、发票、票据

### 5.3 Markdown → PPT（现代演示）

**推荐链路 A（Marp — 最简洁）**：
```
Markdown（含 frontmatter: marp: true）→ marp --pdf/slides.md → result.pdf/pptx/html
```
- 零配置，VS Code 实时预览
- 适合技术演讲、代码密集型演示

**推荐链路 B（Slidev — 最灵活）**：
```
Markdown（含 Vue 组件）→ slidev export → result.pdf/pptx
```
- 支持交互式组件、Live Code
- 适合开发者演示

**推荐链路 C（Pandoc → Beamer）**：
```
Markdown → pandoc -t beamer -V theme:Madrid --output=result.pdf
```
- LaTeX 排版质量，数学公式支持最强
- 适合学术演讲

**推荐链路 D（AI 驱动 — Presenton/PPTAgent）**：
```
主题/文档 → AI 生成大纲 → AI 编辑参考模板 → result.pptx
```
- 最接近 Gamma 体验的开源方案

### 5.4 关键洞察：为什么"直接用 python-docx/python-pptx 堆砌"是下策

| 方式 | 排版质量 | 可维护性 | 灵活性 | 适用场景 |
|------|---------|---------|--------|---------|
| python-docx 手动堆砌 | ❌ 差（AI 排版不专业） | ❌ 差（代码即样式） | 中 | 简单文档 |
| Pandoc + reference.docx | ✅ 好（继承 Word 样式） | ✅ 好（内容与样式分离） | 高 | 品牌化文档 |
| docxtpl / poi-tl 模板 | ✅ 极好（设计师级模板） | ✅ 极好 | 高 | 批量生成 |
| WeasyPrint + CSS | ✅ 好（CSS 控制排版） | ✅ 好 | 极高 | Web 背景团队 |

**核心原则**：**让设计师负责样式（模板/CSS），让 AI 负责内容，让引擎负责渲染。不要让 AI 做设计决策。**

---

## 6. 全景对比表格

### 6.1 核心开源项目全景对比

| 项目 | Stars | 格式 | 技术栈 | 模板 | 中文 | 活跃度 | 核心优势 |
|------|-------|------|--------|------|------|--------|---------|
| **typst/typst** | 55.3K | PDF | Rust | ✅ | ✅ | 极高 | 编译快10-100倍，LaTeX现代替代 |
| **jgm/pandoc** | 45.8K | 全格式 | Haskell | ✅ | ✅ | 极高 | 万能格式转换中枢 |
| **slidevjs/slidev** | 48.0K | PPT/HTML | Vue/Vite | ✅ | ✅ | 极高 | 开发者友好的Markdown演示 |
| **hakimel/reveal.js** | 67K+ | PPT/HTML | JS | ✅ | ✅ | 高 | 最成熟的HTML演示框架 |
| **presenton** | 9.4K | PPT | TS/Python | ✅ | ✅ | 极高 | Gamma最佳开源替代 |
| **Kozea/WeasyPrint** | 9.5K | PDF | Python | ✅ | ✅ | 极高 | HTML/CSS→PDF排版引擎 |
| **icip-cas/PPTAgent** | 4.9K | PPT | Python | ✅ | ✅ | 高 | 学术级编辑式PPT生成 |
| **Sayi/poi-tl** | 5.1K | Word | Java | ✅ | ✅ | 高 | Java最强Word模板引擎 |
| **allweonedev/presentation-ai** | 2.9K | PPT | Next.js | ✅ | ✅ | 中 | Gamma开源替代 |
| **marp-cli** | 3.7K | PPT | TS/Node | ✅ | ✅ | 极高 | 最简洁的Markdown→PPT |

### 6.2 商业产品对比

| 产品 | 定位 | AI内容生成 | 设计质量 | PPTX导出 | 价格 |
|------|------|-----------|---------|---------|------|
| **Gamma** | AI优先（内容+设计） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐（可变） | ⭐⭐（有问题） | 免费/$8+ |
| **Beautiful.ai** | 设计优先（约束式） | ⭐⭐⭐ | ⭐⭐⭐⭐⭐（保证） | ⭐⭐⭐⭐（干净） | $12/月 |
| **WPS AI** | 国产全能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 会员制 |
| **腾讯文档AI** | 国产文档转PPT | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 会员制 |
| **Canva** | 设计平台+AI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 免费/付费 |

### 6.3 文档生成技术栈对比

| 技术栈 | PDF质量 | Word质量 | PPT质量 | 学习曲线 | 性能 | 中文 |
|--------|---------|---------|---------|---------|------|------|
| **LaTeX** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐(Beamer) | 陡峭 | 慢 | 需配置 |
| **Typst** | ⭐⭐⭐⭐⭐ | — | ⭐⭐⭐(typst-slide) | 平缓 | 极快 | ✅ |
| **Pandoc** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 中等 | 中 | ✅ |
| **WeasyPrint** | ⭐⭐⭐⭐ | — | — | 平缓(Web) | 中 | 需字体 |
| **Marp** | ⭐⭐⭐⭐ | — | ⭐⭐⭐⭐ | 极平缓 | 快 | ✅ |
| **Slidev** | ⭐⭐⭐⭐ | — | ⭐⭐⭐⭐⭐ | 中等(Vue) | 快 | ✅ |

---

## 7. 推荐排名

### 7.1 "最值得集成"开源项目 TOP 10

| 排名 | 项目 | 推荐理由 | 集成优先级 |
|------|------|---------|-----------|
| 1 | **Pandoc** | 万能格式转换中枢，已 有 MCP 封装，Markdown→Word/PDF/PPT 的基石 | ⭐⭐⭐⭐⭐ |
| 2 | **Typst** | 编译极快的现代排版引擎，适合 AI Agent 的实时生成场景 | ⭐⭐⭐⭐⭐ |
| 3 | **Presenton** | Gamma 最佳开源替代，HTML/CSS 渲染 PPT，有 API 可集成 | ⭐⭐⭐⭐⭐ |
| 4 | **WeasyPrint** | HTML/CSS→PDF 的最佳引擎，月下载 2500 万，极其稳定 | ⭐⭐⭐⭐ |
| 5 | **Marp** | 最简洁的 Markdown→PPT，零配置，已有 Claude Code Skill | ⭐⭐⭐⭐ |
| 6 | **Slidev** | 最灵活的 Markdown 演示框架，Vue 组件嵌入 | ⭐⭐⭐⭐ |
| 7 | **poi-tl / docxtpl** | Word 模板引擎的最佳方案，样式零损耗 | ⭐⭐⭐⭐ |
| 8 | **PPTAgent** | 学术级 PPT 编辑式生成，中科院出品，有论文背书 | ⭐⭐⭐ |
| 9 | **OpenPrism** | LaTeX 学术写作工作台，顶会模板一键切换 | ⭐⭐⭐ |
| 10 | **agent-pdf** | 专为 AI Agent 设计的 PDF 生成，内置 MCP Server | ⭐⭐⭐ |

### 7.2 按使用场景推荐

| 场景 | 首选方案 | 备选方案 |
|------|---------|---------|
| **AI 生成品牌化 Word** | Pandoc + reference.docx | docxtpl / poi-tl |
| **AI 生成高质量 PDF** | Typst 模板 / Pandoc + XeLaTeX | WeasyPrint + CSS |
| **AI 生成演示 PPT** | Presenton（Gamma体验）/ Marp（极简） | Slidev（灵活）/ PPTAgent（学术） |
| **AI 生成学术论文** | OpenPrism / Pandoc + LaTeX 模板 | Typst + 学术模板 |
| **AI 生成报告/书籍** | Typst / Pandoc + LaTeX | WeasyPrint |
| **批量生成（数据驱动）** | poi-tl / docxtpl + JSON | Pandoc + YAML 元数据 |

---

## 8. 结论：办公超级 Skill 的最佳集成方案

如果目标是构建一个**"办公超级 Skill"**（即一个 AI Agent 能根据用户需求生成 Word/PPT/PDF/LaTeX 全格式高质量文档的 Skill），基于本次调研的结论如下：

### 8.1 最佳技术架构

```
用户需求（自然语言）
    ↓
[AI 内容生成层] — LLM 生成结构化 Markdown / JSON
    ↓
[格式转换层] — 根据目标格式路由到不同引擎
    ├── Word → Pandoc + reference.docx（品牌化模板）
    ├── PDF  → Typst 模板（快速）/ XeLaTeX 模板（高质量）
    ├── PPT  → Marp（极简）/ Presenton API（Gamma体验）
    └── LaTeX → 模板填充 + 自动编译
    ↓
[质量保证层] — 模板锁定设计，引擎保证排版
    ↓
最终文档
```

### 8.2 最值得借鉴/集成的开源项目（最终结论）

**第一梯队（核心引擎，必选）**：
1. **Pandoc** — 作为 Markdown↔Word↔PDF↔LaTeX 的万能转换中枢，已有 [mcp-pandoc](https://github.com/vivekVells/mcp-pandoc) MCP 封装可直接集成。
2. **Typst** — 作为 PDF 快速生成引擎，单一二进制、毫秒级编译、模板生态丰富，是 AI Agent 实时生成的最佳选择。

**第二梯队（特定格式最佳方案）**：
3. **Presenton** — PPT 生成的最佳开源方案，HTML/CSS 渲染 + API 调用，最接近 Gamma 体验。
4. **Marp** — 极简 Markdown→PPT 的最佳工具，已有成熟的 Claude Code Skill 生态。
5. **WeasyPrint** — HTML/CSS→PDF 的最佳引擎，适合 Web 背景的报表/发票等场景。

**第三梯队（专业场景补充）**：
6. **poi-tl / docxtpl** — 当需要**像素级保留** Word 模板样式时的必备工具。
7. **PPTAgent** — 当需要**学术级** PPT 质量时的最佳选择（编辑式生成）。
8. **OpenPrism** — 当需要**学术论文**全流程写作时的最佳参考。

### 8.3 核心设计原则

1. **模板锁定设计**：绝不让 AI 做设计决策。所有排版质量由预制模板保证。
2. **Pandoc 作为中枢**：Markdown 作为 AI 输出的中间格式，Pandoc 负责最终格式转换。
3. **分阶段生成**：大纲确认 → 内容生成 → 格式渲染（借鉴 Gamma 的 Outline Gate）。
4. **MCP Server 化**：将文档生成能力封装为 MCP Server，供所有 AI Agent 统一调用。
5. **Typst 优先 PDF**：对速度敏感的场景用 Typst 替代 LaTeX（编译快 10-100 倍）。
6. **Presenton/Marp 优先 PPT**：用 Web 技术渲染 PPT，而非 python-pptx 堆砌。

### 8.4 对 harryopo LaTeX 模板体系的启示

基于本次调研，对当前项目（harryopo LaTeX 通用模板体系）的建议：

1. **Typst 值得关注**：虽然当前项目基于 XeLaTeX，但 Typst 在编译速度和易用性上的优势巨大，未来可考虑提供 Typst 版本的模板。
2. **Pandoc 集成**：可以构建一个 `Markdown → Pandoc → harryopo .cls → PDF` 的链路，让 AI 只需输出 Markdown。
3. **Marp/Slidev 输出**：报告/论文模板体系可以考虑增加演示文稿输出能力（Marp 基于 Markdown，与 LaTeX 体系互补）。
4. **MCP Server**：将 harryopo 模板编译能力封装为 MCP Server，供 Claude Code/Cursor 直接调用。

---

## 附录：调研数据来源

### 开源项目 GitHub 数据（2026-08-08 核实）

| 项目 | Stars | 最后更新 | 数据来源 |
|------|-------|---------|---------|
| typst/typst | 55,341 | 2026-08-07 | GitHub API |
| jgm/pandoc | 45,768 | 2026-08-07 | GitHub API |
| slidevjs/slidev | 48,005 | 2026-08-05 | GitHub API |
| presenton/presenton | 9,428 | 2026-08-07 | GitHub API |
| Kozea/WeasyPrint | 9,473 | 2026-08-07 | GitHub API |
| icip-cas/PPTAgent | 4,896 | 2026-08-03 | GitHub API |
| Sayi/poi-tl | 5,129 | 2026-07-15 | GitHub API |
| marp-team/marp-cli | 3,738 | 2026-07-20 | GitHub API |
| allweonedev/presentation-ai | 2,928 | 2026-06-05 | GitHub API |
| hakimel/reveal.js | 67,000+ | 2026-08-07 | WebSearch |

### 主要搜索关键词覆盖

**英文**：AI document generation open source / docx template engine / AI generate beautiful PDF / marp slidev AI / typst vs latex / LaTeX template AI agent / weasyprint pagedjs / Cursor Claude Code skill

**中文**：办公文档 AI 生成开源 / word 模板引擎 / AI 生成 PPT 开源 / WPS AI 灵犀 / 腾讯文档 AIPPT / Markdown 转 Word PPT

---

*报告结束。本文档基于 2026-08-08 的公开信息和 GitHub 数据编写，项目活跃度和 Stars 数可能随时间变化。*
