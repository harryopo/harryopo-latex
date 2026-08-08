# Word/Markdown → LaTeX 开源技术方案深度调研报告

> **调研日期**: 2026-08-05
> **调研目的**: 为 harryopo LaTeX 模板体系寻找最佳的 Word/Markdown → LaTeX 转换方案
> **适用场景**: 学术研究用途，将 Word 文档/Markdown 转换为使用自定义模板的 LaTeX 论文
> **重点关注**: 2024-2026 年仍活跃维护的项目，含中文开源项目

---

## 目录

1. [Pandoc 方案](#1-pandoc-方案)
2. [反向方案（LaTeX→其他格式）](#2-反向方案latex其他格式)
3. [专门的 Word→LaTeX 工具](#3-专门的-wordlatex-工具)
4. [AI 驱动方案](#4-ai-驱动方案)
5. [可视化 LaTeX 编辑器](#5-可视化-latex-编辑器)
6. [表格转换难点](#6-表格转换难点)
7. [适用性评分汇总](#7-适用性评分汇总)
8. [针对 harryopo 的推荐方案](#8-针对-harryopo-的推荐方案)

---

## 1. Pandoc 方案

### 1.1 Pandoc 核心能力

| 项目 | 信息 |
|------|------|
| **项目名** | Pandoc |
| **GitHub** | https://github.com/jgm/pandoc |
| **Star 数** | ~37k+（估算，基于行业地位） |
| **最新版本** | 3.8.3 (2025-2026) |
| **最近更新** | 活跃维护中（2025-10-20 发布 3.8.2.1） |
| **许可证** | GPL-2.0+ |
| **适用性评分** | **4/5** |

**核心能力**：
- 支持 40+ 种文档格式互转，包括 docx、markdown、LaTeX、HTML、EPUB 等
- docx → LaTeX 是其核心功能之一，通过抽象语法树（AST）中间格式转换
- 支持 YAML metadata、引用文献（通过 `--citeproc`）、数学公式（OMML ↔ LaTeX）
- 可通过 Lua 过滤器（`--lua-filter`）自定义转换逻辑
- 原生支持 Markdown 扩展语法（表格、脚注、定义列表等）

**Markdown → LaTeX 效果**：
- **优秀**：这是 Pandoc 的黄金路径，效果最佳
- 支持所有标准 Markdown 语法，包括 GFM 表格、脚注、引用
- 数学公式 `$...$` / `$$...$$` 原生支持
- 可通过自定义模板（`--template`）控制输出格式

**docx → LaTeX 能力边界**：
- ✅ 段落、标题层级、列表、加粗/斜体
- ✅ 基本表格（简单合并单元格）
- ✅ 数学公式（OMML → LaTeX，通过 texmath）
- ✅ 图片、超链接、脚注
- ⚠️ 复杂表格（跨行跨列合并）约 90% 概率出错（行业数据）
- ⚠️ 样式映射有限，无法精确还原 Word 样式
- ❌ 不支持 Word 宏、复杂域代码、嵌入对象
- ❌ 版式信息（页面大小、边距、分栏）需要额外配置

### 1.2 Pandoc 自定义模板机制

**reference doc 机制**（用于 docx 输出）：
- `--reference-doc=reference.docx` 指定样式参考文档
- 仅适用于 docx 输出，不适用于 LaTeX 输出

**template 机制**（用于 LaTeX 输出）：
- `--template=eisvogel.latex` 指定 LaTeX 模板
- 模板中使用 `$variable$` 语法插入 Pandoc 变量
- 可通过 YAML frontmatter 传入大量配置参数
- 支持 `header-includes` 插入自定义 LaTeX 代码

**自定义模板的关键变量**：
```yaml
---
documentclass: article  # 可改为 ctexart 配合中文
classoption:
  - 11pt
  - twocolumn
fontsize: 11pt
geometry:
  - top=2.5cm
  - bottom=2.5cm
header-includes: |
  \usepackage{harryopo-base}
  \useharryopotheme{paper}
---
```

### 1.3 Pandoc 表格处理

**已知问题**（基于 Pandoc issue #11147，2025-09-16）：
- docx reader 计算列宽时，**所有表格默认按 100% 宽度处理**
- 列宽比例通过 `tblGrid` 除以总和计算，丢失原始表格宽度
- 复杂表格（5列以上、内容较长）易产生 `Overfull \hbox` 错误

**Pandoc 表格类型支持**：
- ✅ 简单表格（无合并单元格）
- ⚠️ `\multicolumn` 水平合并（基本支持）
- ❌ `\multirow` 垂直合并（支持差，常丢失）
- ❌ 嵌套表格（不支持）
- ⚠️ 跨页表格（需手动指定 `longtable` 输出）

### 1.4 Eisvogel 模板（pandoc-latex-template）

| 项目 | 信息 |
|------|------|
| **项目名** | Eisvogel (pandoc-latex-template) |
| **GitHub** | https://github.com/Wandmalfarbe/pandoc-latex-template |
| **Star 数** | **7,221** (2026-08-05) |
| **最新版本** | v3.5.1 (2026-07-04) |
| **最近更新** | 活跃维护（29 个 release） |
| **许可证** | BSD-3-Clause |
| **适用性评分** | **4/5** |

**核心能力**：
- 最流行的 Pandoc LaTeX 模板，专为学术文档/讲义设计
- 支持自定义标题页（颜色、Logo、背景图）
- 支持中文（配合 XeLaTeX + 字体设置）
- 内置代码高亮、目录、页眉页脚配置
- 提供 book、article 等多种文档类支持

**已知限制**：
- 宽表格（5列以上、长内容）易导致编译失败（issue #440, 2025-12-10）
- 12列以上表格几乎必然失败
- 模板较为沉重，与自定义 .cls 体系集成需要调整

**对我们的意义**：
- 可以借鉴 Eisvogel 的模板变量设计思路
- 可以作为 Pandoc → harryopo 的模板适配层
- 但不能直接使用，需要改造为加载 harryopo-base.sty 的版本

### 1.5 其他 Pandoc 增强项目

**pandoc-thesis** (https://github.com/cagix/pandoc-thesis)
- 学术论文/学位论文模板，集成 Eisvogel
- 139 commits，2026-06-22 更新，活跃
- 提供 GitHub Actions CI 编译

**markdown-to-arxiv** (https://github.com/abhishektiwari/markdown-to-arxiv)
- Markdown → arXiv/bioRxiv/Eisvogel 多模板输出
- 12 commits，2025-11-19 更新
- 支持 BibTeX 引用、GraphViz/PlantUML 图表

---

## 2. 反向方案（LaTeX→其他格式）

> 本节为补充调研，不是本次需求重点，但了解有助于构建完整工具链。

### 2.1 make4ht (tex4ht)

| 项目 | 信息 |
|------|------|
| **项目名** | make4ht |
| **GitHub** | https://github.com/michal-h21/make4ht |
| **最新版本** | v0.4e (2026-02-24) |
| **最近更新** | 活跃维护 |
| **许可证** | LPPL |
| **适用性评分** | **2/5**（反向工具，不直接适用） |

**核心能力**：
- LaTeX → HTML5/XML/epub/ODT 转换
- 基于 tex4ht 引擎，提供现代构建系统
- 支持 Lua 过滤器、DOM 后处理
- 数学公式可输出为 MathML 或 SVG

**对我们的意义**：
- 可用于将 harryopo 生成的 LaTeX 反向校验
- 可构建 LaTeX → Web 预览管线

### 2.2 LaTeXML

| 项目 | 信息 |
|------|------|
| **项目名** | LaTeXML |
| **GitHub** | https://github.com/brucemiller/LaTeXML |
| **Star 数** | ~1k+（估算） |
| **最近更新** | 活跃维护（2026） |
| **许可证** | CC0/Public Domain |
| **适用性评分** | **2/5**（反向工具） |

**核心能力**：
- LaTeX → XML/HTML/MathML/ePub/JATS
- 被 arXiv.org、DARPA 等机构使用
- 数学公式转 MathML 精度极高
- 适合学术出版 workflows

---

## 3. 专门的 Word→LaTeX 工具

### 3.1 docx2tex (transpect)

| 项目 | 信息 |
|------|------|
| **项目名** | docx2tex |
| **GitHub** | https://github.com/transpect/docx2tex |
| **Star 数** | 未公开（1,301 commits，成熟项目） |
| **最近更新** | **2026-04-28**（活跃维护） |
| **许可证** | 需确认（基于 le-tex 商业框架） |
| **适用性评分** | **4/5** |

**核心能力**：
- **最专业的 docx → LaTeX 开源工具**
- 基于 transpect 框架（XProc + XSLT）
- 三层架构：DOCX → Hub XML 中间格式 → LaTeX
- 支持 MathML → LaTeX（通过 mml2tex 模块）
- 支持 CSV/XML 双配置方式（样式映射）
- 支持 tabularx、longtable 表格模型
- 支持 MathType 公式源（OLE+WMF）

**两种配置方式**：
```csv
# CSV 配置（新手友好）
Heading 1 ; \chapter{ ; }
Heading 2 ; \section{ ; }
Quote     ; \begin{quote} ; \end{quote}
```
```xml
<!-- XML 配置（高级定制） -->
<template context="dbk:para[@role = 'Heading1']">
  <rule break-after="2" name="chapter" type="cmd">
    <param/>
  </rule>
</template>
```

**限制**：
- 需要 Java 13+（较重依赖）
- 学习曲线较陡（XSLT/XProc 知识）
- 中文支持需要额外配置 xeCJK/ctex

**对我们的意义**：
- **高度可定制**，非常适合对接 harryopo 自定义模板
- 可以通过 XML 配置精确映射 Word 样式到 harryopo 命令
- 表格支持（tabularx/longtable）与我们的需求匹配

### 3.2 Word2LaTeX (LSZ-03)

| 项目 | 信息 |
|------|------|
| **项目名** | Word2LaTeX |
| **GitHub** | https://github.com/LSZ-03/Word2LaTeX |
| **Star 数** | 新项目（13 commits） |
| **最近更新** | **2026-05-11**（新发布） |
| **许可证** | 需确认 |
| **适用性评分** | **3/5**（潜力大但太新） |

**核心能力**：
- Word (.docx) → 期刊特定 LaTeX 转换器
- **115 个期刊模板**（28 个出版商家族）
- 三层架构：解析器 → 语义AST → 约束AST → LaTeX
- 支持公式识别、引用管理、标签生成
- 确定性解析（非 AI），可重现

**限制**：
- 项目极新（2026-05 才公开），生态未成熟
- 公式识别和表格自适应布局仍需优化
- 文档和社区尚未建立

### 3.3 CoreTex (TheClazer)

| 项目 | 信息 |
|------|------|
| **项目名** | CoreTex |
| **GitHub** | https://github.com/TheClazer/CoreTex |
| **Star 数** | 新项目（33 commits） |
| **最近更新** | **2026-07-03**（活跃） |
| **许可证** | MIT |
| **适用性评分** | **3/5**（有 Web 界面，但太新） |

**核心能力**：
- 完整的 Web 应用（前端 + 后端 + Worker）
- 支持直接 OMML 解析器、Beamer 模板
- BibTeX 提取、样式映射配置
- S3/R2 图片存储、Railway 自动扩缩容
- Docker 部署

### 3.4 doc2tex (rralDev/IOST-ASCOL)

| 项目 | 信息 |
|------|------|
| **项目名** | doc2tex |
| **GitHub** | https://github.com/rralDev/doc2tex |
| **Star 数** | 较低 |
| **最近更新** | **2026-01-13** |
| **许可证** | 需确认 |
| **适用性评分** | **2/5**（功能简单） |

**核心能力**：
- DOCX ↔ LaTeX 双向转换
- 基于 python-docx，保留标题、加粗/斜体、表格
- 简单表格和图片处理
- CLI + Web 双界面
- 本地处理（不上传云端）

### 3.5 ms2md (ucli-tools)

| 项目 | 信息 |
|------|------|
| **项目名** | ms2md |
| **GitHub** | https://github.com/ucli-tools/ms2md |
| **Star 数** | 0（新项目，5 commits） |
| **最近更新** | 2025-05-05 |
| **许可证** | Apache-2.0 |
| **适用性评分** | **2/5** |

**核心能力**：
- Word → Markdown + LaTeX 转换器（Python）
- 专注数学公式、表格、图表的转换
- 适合技术书籍、学术论文、科学文档

### 3.6 word-formatter-app (ViranjPatel)

| 项目 | 信息 |
|------|------|
| **项目名** | Document Processor |
| **GitHub** | https://github.com/ViranjPatel/word-formatter-app |
| **Star 数** | 较低（24 commits） |
| **最近更新** | 2025-06-08 |
| **许可证** | 需确认 |
| **适用性评分** | **2/5** |

**核心能力**：
- Flask Web 应用，双功能：Word 格式化 + LaTeX 转换
- 保留标题、表格、列表结构
- 输出可编译 LaTeX 代码

---

## 4. AI 驱动方案

### 4.1 MinerU（强烈推荐）

| 项目 | 信息 |
|------|------|
| **项目名** | MinerU |
| **GitHub** | https://github.com/opendatalab/MinerU |
| **Star 数** | **~75,700** (2026-08-05) |
| **最新版本** | 4.0.0a5 (预发布) / 3.4.4 (稳定版) |
| **最近更新** | **2026-07-30**（极活跃） |
| **许可证** | MinerU 开源许可（基于 Apache 2.0） |
| **适用性评分** | **5/5** |

**核心能力**：
- **目前最强的文档解析工具**，OpenDataLab（上海AI实验室）出品
- 支持 PDF、DOCX、PPTX、XLSX、图片、网页 → Markdown/JSON
- **公式 → LaTeX** 精度极高（UniMERNet 模型）
- **表格 → HTML**，支持跨页表格合并
- 自动去除页眉/页脚/页码
- 支持扫描件 OCR、手写体识别
- **109 种语言** OCR 识别
- VLM + OCR 双引擎（pipeline / vlm / hybrid 三种后端）
- OmniDocBench v1.6 评分 **95.69**（SOTA）

**技术架构**：
- `pipeline` 后端：快速稳定，无幻觉，CPU/GPU 通用
- `vlm` 后端：高精度，支持 vLLM/LMDeploy
- `hybrid` 后端：高精度 + 原生文本提取，低幻觉

**部署方式**：
- Web UI（mineru.net）、桌面客户端、CLI、REST API
- Python/Go/TypeScript SDK
- Docker、私有化部署、完全离线
- 支持 10+ 国产 AI 芯片（昇腾、寒武纪等）

**限制**：
- 不直接输出 LaTeX 文档（输出 Markdown + LaTeX 公式片段）
- 需要进一步转换 Markdown → LaTeX（可配合 Pandoc）
- VLM 后端需要 GPU（pipeline 后端可 CPU 运行）
- 4GB VRAM 即可运行（轻量级）

**对我们的意义**：
- **最佳的 docx/pdf 解析前端**
- 输出的 Markdown 可通过 Pandoc 转为 harryopo LaTeX
- 公式识别精度业界最高
- 已有 MCP Server，可与 AI Coding 工具集成

### 4.2 Marker（强烈推荐）

| 项目 | 信息 |
|------|------|
| **项目名** | Marker (marker-pdf) |
| **GitHub** | https://github.com/datalab-to/marker |
| **Star 数** | ~20k+（估算，基于行业地位和 fork 数） |
| **最新版本** | 2.0.0 (2026) |
| **最近更新** | **2026-07**（活跃） |
| **许可证** | GPL-3.0（代码）+ OpenRAIL-M（模型权重） |
| **适用性评分** | **5/5** |

**核心能力**：
- Vik Paruchuri（Kaggle 创始团队成员）出品，Datalab 维护
- PDF/图片/PPTX/DOCX/XLSX/HTML/EPUB → Markdown/JSON/HTML
- **公式 → LaTeX**（通过 Texify 模型）
- 表格、表单、行内数学、链接、引用、代码块格式化
- 图片提取并保存
- **25 页/秒**（H100 批处理），单页约 0.6 秒
- olmocr-bench 评分 **76.0%**（balanced 模式）

**特色功能**：
- `--use_llm` 混合模式：结合 Gemini/Claude/OpenAI/Ollama 提升精度
- 可跨页合并表格、处理行内数学、格式化表格
- 支持自定义处理器和格式化逻辑
- 支持 JSON Schema 结构化提取（beta）

**限制**：
- 早期版本对中文支持较弱（已通过 LLM 集成改善）
- GPL-3.0 许可证对商业使用有限制
- 不直接输出 LaTeX 文档（输出 Markdown + LaTeX 公式）

### 4.3 Docling

| 项目 | 信息 |
|------|------|
| **项目名** | Docling |
| **GitHub** | https://github.com/DS4SD/docling |
| **Star 数** | ~25k+（估算，IBM 生态项目） |
| **最近更新** | **2026**（活跃） |
| **许可证** | MIT |
| **适用性评分** | **4/5** |
| **维护方** | IBM 苏黎世研究院 / Linux Foundation AI & Data |

**核心能力**：
- 企业级多格式文档处理平台
- 支持 PDF/DOCX/PPTX/XLSX/HTML/Markdown/LaTeX/JATS 等
- 统一中间格式 Docling Document
- 与 IBM Cloud、Red Hat OpenShift 深度集成
- 高级表格提取、数学公式提取

**限制**：
- 中文支持标注为"实验性"
- 复杂公式识别不如 MinerU
- "广"有时伴随"精"的妥协

### 4.4 ScribeTeX（AI 视觉模型方案）

| 项目 | 信息 |
|------|------|
| **项目名** | ScribeTeX |
| **GitHub** | https://github.com/ScribeTeX/ScribeTeX |
| **Star 数** | 新项目 |
| **最近更新** | **2026-01** |
| **许可证** | Apache-2.0 |
| **适用性评分** | **3/5**（API 成本高） |

**核心能力**：
- 使用 AI 视觉模型（GPT/Gemini/Claude）将文档转为 LaTeX
- 支持 PDF/图片/TXT/Markdown/DOCX
- 自动 PDF 编译（需 pdflatex）
- 分块处理大文档

**支持模型**（2026-01）：
- OpenAI: gpt-4.1, gpt-5.x
- Google: gemini-2.5-flash/pro
- Anthropic: claude-sonnet-4.5, claude-opus-4.5

**限制**：
- API 成本：每页 $0.001-0.03（取决于模型）
- DOCX 仅提取文本（格式可能丢失）
- 需要至少一个 LLM 提供商的 API Key

### 4.5 texify（已废弃）

| 项目 | 信息 |
|------|------|
| **项目名** | texify |
| **GitHub** | https://github.com/VikParuchuri/texify |
| **状态** | **已废弃**（2025-01-29 标记 deprecated） |
| **后续** | 功能已迁移到 surya 和 Marker |

**说明**：texify 是 Marker 作者早期的公式 OCR 工具，现已整合进 Marker 的管线。

### 4.6 Nougat（Meta）

| 项目 | 信息 |
|------|------|
| **项目名** | Nougat (Neural Optical Understanding for Academic Documents) |
| **GitHub** | https://github.com/facebookresearch/nougat |
| **Star 数** | ~10k+（估算） |
| **最近更新** | 2025（活跃度降低） |
| **许可证** | CC-BY-NC（非商用） |
| **适用性评分** | **3/5** |

**核心能力**：
- Meta 出品的科学论文专用 OCR
- PDF → Markdown（含 LaTeX 公式）
- 专门针对学术论文优化
- 可通过 Google Colab 免费使用

**限制**：
- 非商用许可证（CC-BY-NC）
- 中文支持有限
- 已被 MinerU/Marker 超越

### 4.7 商业 AI 服务（参考）

**Mathpix**（https://mathpix.com）
- 最知名的公式 OCR 商业服务
- PDF/图片 → LaTeX/DOCX/Markdown/Excel/ChemDraw
- API 集成、Snip 桌面应用
- 精度极高但收费

**Doc2X**（https://noedgeai.com）
- AI 驱动的文档智能平台
- PDF/图片 → Word/LaTeX/HTML/Markdown
- 支持手写公式、合并单元格表格
- 中文支持好

**TeXify**（https://www.texifyai.app）
- AI 文档转 LaTeX SaaS
- 98% 转换精度（宣称）
- 50+ LaTeX 模板（IEEE/APA/thesis/beamer）
- 一键导出到 Overleaf

---

## 5. 可视化 LaTeX 编辑器

### 5.1 LaTeX.js（纯 JS 渲染器）

| 项目 | 信息 |
|------|------|
| **项目名** | LaTeX.js |
| **GitHub** | https://github.com/michael-brade/LaTeX.js |
| **官网** | https://latex.js.org/ |
| **Star 数** | ~2k+（估算） |
| **最近更新** | 需确认（项目相对成熟稳定） |
| **许可证** | MIT/LGPL（需确认） |
| **适用性评分** | **3/5** |

**核心能力**：
- **100% JavaScript** 的 LaTeX → HTML5 翻译器
- 浏览器端运行，无需服务器
- 无外部依赖
- 提供 CLI（`latex.js`）和 Web 组件（`<latex-js>`）
- 支持自定义宏扩展
- 单次遍历（vs LaTeX 多次编译）

**限制**：
- 无法 100% 还原 LaTeX 输出（glue 等概念无法映射到 HTML）
- 复杂宏包支持有限
- 主要用于预览，不等同于完整 LaTeX 引擎

**适用场景**：
- Web 端实时预览
- 在线 LaTeX 编辑器的渲染层
- 文档展示

### 5.2 react-latex-editor（React 富文本编辑器）

| 项目 | 信息 |
|------|------|
| **项目名** | react-latex-editor (React Rich Text with Math) |
| **npm** | https://www.npmjs.com/package/react-latex-editor |
| **最新版本** | 1.3.6 (2026-07，14天前) |
| **许可证** | 需确认 |
| **适用性评分** | **4/5**（Web 嵌入场景） |

**核心能力**：
- 基于 **TipTap** + **MathLive** 的 React 富文本编辑器
- 支持行内和块级数学公式（MathLive 符号面板）
- 表格（增删行列、合并/拆分单元格、调整列宽）
- 图片（拖拽、URL、调整大小、对齐）
- YouTube 视频嵌入
- 代码块（语法高亮）
- 完整 TypeScript 支持
- 响应式设计
- gzip 后约 90KB

**对我们意义**：
- 可作为 Web 端 LaTeX 编辑器的核心组件
- 输出 HTML，可进一步转换为 LaTeX
- Next.js 兼容（App Router / Pages Router）

### 5.3 react-native-latex-js（React Native 渲染）

| 项目 | 信息 |
|------|------|
| **项目名** | react-native-latex-js |
| **npm** | https://www.npmjs.com/package/react-native-latex-js |
| **最新版本** | 1.0.0 (7个月前) |
| **适用性评分** | **3/5**（移动端场景） |

**核心能力**：
- React Native 组件，使用 LaTeX.js + WebView 渲染
- 离线工作（LaTeX.js 内联打包）
- 自定义样式、TypeScript 支持
- 跨平台（iOS & Android）

### 5.4 LaTeX2JS（Vue/React 组件）

| 项目 | 信息 |
|------|------|
| **项目名** | LaTeX2JS |
| **GitHub** | https://github.com/Mathapedia/LaTeX2JS |
| **Star 数** | 中等（313 commits） |
| **最近更新** | **2025-07-23** |
| **许可证** | 需确认 |
| **适用性评分** | **3/5** |

**核心能力**：
- Vue/React 的 LaTeX 渲染组件
- Composition API 和 SSR 支持
- 支持 MathJax 集成
- 多包架构（monorepo）

### 5.5 其他编辑器/工具

**Overleaf**（https://overleaf.com）
- 最流行的在线 LaTeX 编辑器
- 支持协作、版本控制、富文本预览
- 提供 API（可嵌入）

**Typst**（https://typst.app）
- **现代 LaTeX 替代品**，Rust 编写
- Markdown 式语法，毫秒级编译
- ~40k+ stars（GitHub）
- Apache-2.0 许可证
- **不支持直接输出 LaTeX**，但理念值得借鉴

**TeXstudio / TeXShop / VS Code + LaTeX Workshop**
- 桌面 LaTeX IDE
- 源码 + PDF 预览双栏
- 不适合 Web 嵌入

---

## 6. 表格转换难点

### 6.1 根本问题：结构不匹配

**Word 表格存储方式**：
- 网格单元格（XML），每个单元格可含段落、图片、嵌套表格
- 单元格属性（宽度、阴影、边框、合并状态）独立存储
- 无固定列规范，列宽动态计算

**LaTeX 表格存储方式**：
- 必须前置声明列规范（如 `{l c r p{5cm}}`）
- 每行必须严格符合列规范
- 合并单元格需要显式 `\multicolumn` 和 `\multirow`
- 多页表格需要切换到 `longtable` 环境

### 6.2 常见转换问题及解决方案

| 问题 | 技术成因 | 影响层级 | 解决方案 |
|------|----------|----------|----------|
| 列定义不符 | 工具误判合并单元格边界 | 结构层 | 手动调整 `tabular` 列声明 |
| 多行单元格分裂 | 未识别软回车（Shift+Enter） | 内容层 | 预处理统一换行方式 |
| 合并单元格丢失 | 跨行/跨列信息未提取 | 结构层 | 手动添加 `\multicolumn`/`\multirow` |
| 特殊字符编码异常 | UTF-8 未映射到 LaTeX 命令 | 表示层 | 加载 ctex，使用 LaTeX 转义 |
| `\hline` 错位/缺失 | 仅基于段落分隔生成行 | 样式层 | 改用 `booktabs`（`\toprule` 等） |
| 列宽不均 | 工具按比例计算（100% 宽度） | 布局层 | 使用 `tabularx` 自适应列宽 |

### 6.3 分层解决方案

**初级：手动校正**
- 适用：简单表格
- 方法：编辑 Pandoc 生成的 `.tex`，调整列声明，插入 `\multicolumn{2}{c}{Header}`

**中级：预处理 Word 文档**
- 适用：中等复杂表格
- 方法：移除嵌套元素、统一换行、用实线边框明确划分区域

**高级：定制 Pandoc Lua 过滤器**
```lua
function Table(tbl)
  for i, row in ipairs(tbl.body) do
    for j, cell in ipairs(row) do
      if cell.content and #cell.content > 1 then
        -- 合并多段内容为单 cell
        cell.content = { pandoc.Plain(table.concat(cell.content, ' ')) }
      end
    end
  end
  return tbl
end
```

**专家级：解析 Word XML**
- 解压 `.docx`（ZIP 包）
- 解析 `w:tblGrid` 和 `w:vMerge` 标签
- 重建 LaTeX 语义结构

### 6.4 业界最佳实践

1. **使用 `tabularx` 替代 `tabular`**：`\begin{tabularx}{\textwidth}{|X|X|}` 实现自适应列宽
2. **使用 `booktabs` 替代 `\hline`**：`\toprule`/`\midrule`/`\bottomrule` 更专业
3. **加载 `array` 宏包**：支持 `m{3cm}` 垂直居中等高级控制
4. **中文表格加载 `ctex`**：避免乱码
5. **跨页表格使用 `longtable`**：自动断页续表
6. **转换后验证清单**：
   - 检查每行 `&` 数量一致性
   - 检查括号匹配
   - 检查命令转义

### 6.5 各工具表格处理能力对比

| 工具 | 简单表格 | 水平合并 | 垂直合并 | 跨页表格 | 嵌套表格 |
|------|----------|----------|----------|----------|----------|
| Pandoc | ✅ 优秀 | ⚠️ 基本 | ❌ 差 | ⚠️ 需配置 | ❌ |
| docx2tex | ✅ 优秀 | ✅ 良好 | ⚠️ 一般 | ✅ 支持 | ❌ |
| MinerU | ✅ 优秀 | ✅ 良好 | ✅ 良好 | ✅ 跨页合并 | ❌ |
| Marker | ✅ 优秀 | ✅ 良好 | ✅ 良好 | ✅ LLM辅助 | ❌ |
| 手动重建 | ✅ 完美 | ✅ 完美 | ✅ 完美 | ✅ 完美 | ✅ |

---

## 7. 适用性评分汇总

| 方案 | Star数 | 活跃度 | docx→LaTeX | 自定义模板 | 表格支持 | 综合 |
|------|--------|--------|------------|-----------|----------|------|
| **MinerU** | 75.7k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | **5/5** |
| **Marker** | 20k+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | **5/5** |
| **Pandoc** | 37k+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **4/5** |
| **docx2tex** | 1.3k commits | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **4/5** |
| **Eisvogel** | 7.2k | ⭐⭐⭐⭐ | - | ⭐⭐⭐⭐ | ⭐⭐⭐ | **4/5** |
| **Docling** | 25k+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | **4/5** |
| **Word2LaTeX** | 新项目 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **3/5** |
| **CoreTex** | 新项目 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | **3/5** |
| **ScribeTeX** | 新项目 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **3/5** |
| **LaTeX.js** | 2k+ | ⭐⭐⭐ | - | - | - | **3/5** |

---

## 8. 针对 harryopo 的推荐方案

### 8.1 推荐架构：三层管线

```
Word/Markdown 文档
       ↓
[第一层] MinerU / Marker  ← 解析 + 公式识别（输出 Markdown + LaTeX 公式）
       ↓
[第二层] Pandoc + 自定义 Lua 过滤器  ← Markdown → LaTeX（加载 harryopo 模板）
       ↓
[第三层] harryopo-paper.cls / harryopo-report.cls  ← 编译输出 PDF
```

### 8.2 方案对比与选择

**方案 A：纯 Pandoc（轻量级）**
- 适用：Markdown 源文档、简单公式、简单表格
- 优点：单一工具、轻量、可定制模板
- 缺点：docx 复杂表格处理弱
- 实现：`pandoc input.md -o output.tex --template harryopo.latex`

**方案 B：MinerU + Pandoc（推荐，重量级）**
- 适用：docx/pdf 源文档、复杂公式、复杂表格
- 优点：公式/表格精度最高
- 缺点：需要 Python 环境 + 模型
- 实现：MinerU 解析 → Markdown → Pandoc 转 LaTeX

**方案 C：docx2tex（专业 docx 路径）**
- 适用：专业 docx 文档（如出版社手稿）
- 优点：最专业的 docx 处理、高度可定制
- 缺点：需要 Java 13+、学习曲线陡
- 实现：通过 XML 配置映射 harryopo 命令

**方案 D：Marker + Pandoc（AI 增强路径）**
- 适用：扫描件、图片、复杂版面
- 优点：处理速度最快（25页/秒）、LLM 增强
- 缺点：GPL-3.0 许可证、模型较大

### 8.3 实施建议

1. **第一阶段（MVP）**：实现 Pandoc + harryopo 模板
   - 创建 `harryopo-pandoc-template.latex`
   - 编写基础 Lua 过滤器处理 harryopo 特有命令
   - 测试 Markdown → LaTeX → PDF 完整链路

2. **第二阶段（增强）**：集成 MinerU
   - 利用 MinerU MCP Server（已有 Skill 支持）
   - 实现 docx/pdf → Markdown → LaTeX 管线
   - 解决复杂公式和表格的转换

3. **第三阶段（专业）**：对接 docx2tex
   - 为需要专业 docx 处理的场景提供方案
   - 编写 harryopo 的 docx2tex XML 配置

4. **第四阶段（可视化）**：Web 编辑器
   - 基于 react-latex-editor 构建 Web 编辑界面
   - 使用 LaTeX.js 提供实时预览
   - 集成 MinerU API 实现文档上传转换

### 8.4 注意事项

- **许可证**：Marker 的 GPL-3.0 可能限制商业使用，优先考虑 MinerU（Apache 2.0）
- **中文支持**：MinerU 中文最佳，Marker 需配合 LLM，Pandoc 需要 ctex
- **模板适配**：Pandoc 模板需要改造为加载 harryopo-base.sty，而非独立 KOMA-Script
- **编译引擎**：harryopo 强制 XeLaTeX，Pandoc 默认 pdfLaTeX，需通过 `--pdf-engine=xelatex` 切换
- **表格策略**：对复杂表格，建议提供"手动重建"模板，而非追求 100% 自动转换

---

## 附录：关键项目链接

| 项目 | GitHub | 语言 | 许可证 |
|------|--------|------|--------|
| Pandoc | https://github.com/jgm/pandoc | Haskell | GPL-2.0+ |
| Eisvogel | https://github.com/Wandmalfarbe/pandoc-latex-template | TeX | BSD-3-Clause |
| MinerU | https://github.com/opendatalab/MinerU | Python | Apache 2.0 |
| Marker | https://github.com/datalab-to/marker | Python | GPL-3.0 |
| Docling | https://github.com/DS4SD/docling | Python | MIT |
| docx2tex | https://github.com/transpect/docx2tex | XSLT/Java | 商业开源 |
| Word2LaTeX | https://github.com/LSZ-03/Word2LaTeX | Python | 需确认 |
| CoreTex | https://github.com/TheClazer/CoreTex | Python/JS | MIT |
| LaTeX.js | https://github.com/michael-brade/LaTeX.js | JavaScript | MIT/LGPL |
| react-latex-editor | https://www.npmjs.com/package/react-latex-editor | React/TS | 需确认 |
| make4ht | https://github.com/michal-h21/make4ht | Lua/TeX | LPPL |
| LaTeXML | https://github.com/brucemiller/LaTeXML | Perl | CC0 |
| Typst | https://github.com/typst/typst | Rust | Apache-2.0 |

---

> **报告版本**: v1.0 (2026-08-05)
> **下次更新建议**: 6个月后复查项目活跃度
