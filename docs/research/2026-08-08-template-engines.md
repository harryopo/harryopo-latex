# 模板引擎驱动的文档生成方案深度调研报告

> 调研日期：2026-08-08
> 调研主题：如何实现「用户提供模板 → AI 按模板样式输出」的文档生成
> 调研方法：全网多轮搜索（WebSearch），覆盖官方文档、GitHub、对比评测、实战案例
> 适用项目：harryopo LaTeX 模板体系 + 通用文档生成能力建设

---

## 目录

- [0. 摘要（TL;DR）](#0-摘要tldr)
- [1. 用户痛点与技术本质](#1-用户痛点与技术本质)
- [2. A. Word/docx 模板引擎方案](#2-a-worddocx-模板引擎方案)
- [3. B. LaTeX 模板系统](#3-b-latex-模板系统)
- [4. C. PDF 模板方案](#4-c-pdf-模板方案)
- [5. D. 通用文档生成框架与 AI 集成](#5-d-通用文档生成框架与-ai-集成)
- [6. 综合对比矩阵](#6-综合对比矩阵)
- [7. 最佳技术路线推荐](#7-最佳技术路线推荐)
- [8. AI 集成架构建议](#8-ai-集成架构建议)
- [9. 参考资料](#9-参考资料)

---

## 0. 摘要（TL;DR）

要实现「用户给模板 → AI 按模板输出」，本质是 **把 AI 从「直接产出文档」改为「产出结构化数据，再由模板引擎渲染」**。这是解决「AI 生成的 Word/PDF 排版很丑」的根本范式转变。

### 核心结论

| 输出格式 | 首选方案 | 备选方案 | AI 的职责 |
|---|---|---|---|
| **Word/docx** | **docxtpl（Python）** 或 **docxtemplater（JS）** | carbone、poi-tl、docx4j | 产出符合占位符 schema 的 JSON/YAML |
| **PDF（设计型）** | **HTML/CSS 模板 + WeasyPrint 或 Puppeteer** | react-pdf（组件式）、Paged.js | 产出 HTML 片段或结构化数据 |
| **PDF（学术/排版型）** | **LaTeX 模板 + Jinja2 渲染** 或 **Typst 模板** | Pandoc + reference-doc/template | 产出 LaTeX/Typst 源码或结构化数据 |
| **跨格式统一** | **Carbone**（已内置 MCP，原生支持 AI）或 **Pandoc + 多 writer 模板** | jsreport（企业级平台） | 产出 JSON 数据 |

### 关键洞察

1. **不要让 AI 直接生成 .docx 或 .pdf 二进制**——这是 Copilot/ChatGPT 文件生成「排版崩坏」的根本原因。LLM 运行在文本语义层，而 .docx 是 OOXML 压缩包，二者抽象层级不匹配。
2. **「模板」的最佳形态就是用户熟悉的工具本身**——Word 文件、LaTeX 文件、HTML 文件。让用户在 Word/LaTeX/HTML 里设计模板，插入占位符，再由引擎填充。
3. **AI 的角色应限定为「数据生产者」**——通过结构化输出（structured output / JSON schema / function calling）产出符合模板 schema 的数据，模板引擎负责保真渲染。
4. **中文支持是硬约束**——所有方案都必须验证中文字体嵌入、CJK 断行、标点处理。

---

## 1. 用户痛点与技术本质

### 1.1 痛点复述

用户的核心诉求是：「我给几个喜欢的 Word、LaTeX 模板，以后 AI 输出就按模板来」。这背后暴露的真实问题是：

- **AI 生成的 Word 排版很丑**：字体不统一、标题层级丢失、表格错位、页眉页脚缺失。
- **AI 不按模板来**：即使给了模板，AI 也常常「忽略」样式，把内容堆到文档底部。
- **格式保真不可控**：同样的提示词，每次生成的排版都不同（non-deterministic）。

### 1.2 技术成因（来自社区实证）

根据多个实战案例分析（remio.ai、CSDN、Amazon Bedrock 团队博客等），格式崩坏的根因是：

| 问题层级 | 技术成因 | 表现 |
|---|---|---|
| **抽象层不匹配** | LLM 运行在文本语义层，.docx 依赖 OOXML XML 结构 | AI「看不到」视觉布局 |
| **转换路径断裂** | AI 返回 Markdown/纯文本 → 第三方库转 .docx → 样式丢失 | 字体、缩进、标题层级全丢 |
| **样式引用断链** | 内容更新后未保留原样式 ID，新段落默认用 Normal 样式 | 全文变成同一种字体 |
| **非线性结构扁平化** | 表格、文本框、图表在 AI 处理中被压成字符串 | 布局与位置信息丢失 |
| **非确定性输出** | LLM 每次生成不同，per-token 计费放大成本 | 同一输入不同排版 |

来源：[remio.ai Copilot 排版问题分析](https://www.remio.ai/post/microsoft-copilot-won-t-create-documents-3-hacks-to-fix-formatting-and-template-issues)、[Amazon Bedrock「最后一公里」问题](https://blog.redoakstrategic.com/solving-the-genai-last-mile-problem)、[CSDN AI 保留 Word 格式技术分析](https://ask.csdn.net/questions/9004167)

### 1.3 解决范式：「数据-模板分离」

业界共识的解法是构建 **四层处理模型**：

```
用户模板（.docx/.tex/.html）
        ↓ 定义占位符 schema
AI 交互层（LLM + structured output）
        ↓ 产出 JSON/YAML 数据
渲染引擎（docxtpl / Jinja2 / WeasyPrint）
        ↓ 注入模板，保持样式继承
合成输出（保真的 .docx / .pdf）
```

| 层级 | 功能 | 关键技术 | 代表工具 |
|---|---|---|---|
| 1. 解析层 | 提取模板结构与样式元数据 | OOXML 解析、样式树重建 | python-docx、OpenXML SDK |
| 2. 映射层 | 建立内容块与样式标识的双向映射 | DOM 节点追踪、XPath 定位 | lxml、xml.etree |
| 3. AI 交互层 | 向 AI 传递 schema 并接收结构化数据 | Prompt 工程、JSON schema、function calling | LangChain、Instructor、Outlines |
| 4. 合成层 | 将 AI 输出按原结构注入并保持样式继承 | 模板填充、样式克隆 | **docxtpl、Jinja2、WeasyPrint** |

**核心原则：模板负责排版样式，AI 负责数据，引擎负责合成。三者职责清晰分离。**

---

## 2. A. Word/docx 模板引擎方案

这是本次调研的重中之重——用户最直接的诉求是「给 Word 模板 → AI 填充」。以下逐一分析主流方案。

### 2.1 docxtemplater（JavaScript）⭐ 推荐

| 维度 | 详情 |
|---|---|
| **语言/生态** | JavaScript / Node.js / 浏览器 |
| **GitHub** | [open-xml-templating/docxtemplater](https://github.com/open-xml-templating/docxtemplater) |
| **许可证** | 核心库 MIT/GPLv3 双协议（开源免费）；高级功能需付费模块 |
| **采用规模** | npm 月下载 **40 万+**，**5 万+ 公司**使用，维护 **8 年+** |
| **当前版本** | 3.69.3（2026 年活跃维护） |
| **模板定义方式** | **.docx 文件本身即模板**——在 Word 中设计排版，插入 `{tag}` 占位符 |
| **占位符语法** | `{name}` 替换、`{#users}{name}{/users}` 循环、`{#if condition}` 条件 |
| **支持格式** | docx / pptx / xlsx / odt |

**核心特性：**
- 文本替换、循环（含表格行/列循环）、条件判断（基础功能免费）
- 付费模块（19 个）：图片插入 `{%image}`、HTML 内容 `{~html}`、图表 `{$chart}`、表格 `{:table}`、脚注、水印、样式控制等
- 模块可单独购买或购买 PRO（4 模块包）/ ENTERPRISE（全模块）套餐
- **非程序员可编辑模板**——业务人员用 Word 设计，开发者集成代码
- 提供 Docker 版本，支持 Python/PHP/Ruby/C 等多语言调用

**优点：**
- 模板即 Word 文件，所见即所得，业务人员可维护
- 生态成熟、测试充分、文档完善、社区活跃
- 同时覆盖 Word/PPT/Excel，一套语法

**缺点：**
- 图片、HTML、图表等关键能力需付费（单模块约几百欧元，ENTERPRISE 约 12250 欧元一次性）
- 付费模块按 Instance（实例）数计费，SaaS 场景需注意授权
- 中文支持依赖模板本身的字体设置（引擎不干预字体）

**适用场景：** 已有 JS/Node 技术栈、需要商业级稳定、愿意为图片/HTML 等能力付费的团队。

### 2.2 docxtpl / python-docx-template（Python）⭐ 推荐（Python 生态首选）

| 维度 | 详情 |
|---|---|
| **语言/生态** | Python（基于 python-docx + Jinja2） |
| **GitHub** | [elapouya/python-docx-template](https://github.com/elapouya/python-docx-template) |
| **许可证** | LGPL-2.1（开源免费） |
| **当前版本** | 0.20.2（2025-11-13 发布） |
| **模板定义方式** | **.docx 文件本身即模板**——在 Word 中插入 Jinja2 风格标签 |
| **占位符语法** | `{{ var }}`、`{% for item in items %}`、`{%p tag %}`（段落级）、`{%tr tag %}`（表格行级）、`{%tc tag %}`（表格列级） |

**核心特性：**
- **完整 Jinja2 语法**——变量、循环、条件、过滤器、注释全支持
- **特殊标签扩展**（解决 Word XML 结构问题）：
  - `{%p %}` 段落级操作（删除/复制整段）
  - `{%tr %}` 表格行级循环（动态生成表格行）
  - `{%tc %}` 表格列级操作
  - `{%r %}` run 级（保留内联样式）
- **RichText / RichTextParagraph**——动态控制加粗、斜体、颜色、字号、超链接
- **InlineImage**——动态插入图片（支持超链接）
- **Sub-documents**——嵌入子文档（嵌套模板）
- **替换 docx 图片/媒体/嵌入对象**
- **获取模板已定义变量**（`get_undeclared_template_variables`，便于生成 AI schema）
- **多轮渲染**、**命令行执行**、**脚注变量支持**
- 跨平台（Windows/macOS/Linux），**无需安装 Microsoft Word**

**优点：**
- Python 生态首选，与 AI/数据科学工具链天然契合
- Jinja2 语法表达力强，社区熟悉度高
- 完全开源免费（LGPL），图片/富文本等核心能力零成本
- 跨平台纯 Python 实现，部署简单
- 中文支持：模板里用什么字体，输出就保留什么字体

**缺点：**
- 单维护者项目（Eric Lapouyade），更新节奏依赖作者
- 无法动态创建全新文档结构（依赖模板预设的结构骨架）
- Jinja2 标签不能跨段落/run（需用 `{%p %}` 等扩展语法规避）

**适用场景：** Python 技术栈、需要免费方案、需要图片/富文本能力、AI 数据科学团队。**这是 AI 集成场景的最优解之一。**

**典型用法：**
```python
from docxtpl import DocxTemplate
doc = DocxTemplate("order_template.docx")
context = {
    "customer_name": "张三",
    "items": [{"name": "无线耳机", "quantity": 2}, ...]
}
doc.render(context)
doc.save("张三_订单.docx")
```

### 2.3 poi-tl（Java）⭐ Java 生态推荐

| 维度 | 详情 |
|---|---|
| **语言/生态** | Java（基于 Apache POI） |
| **GitHub** | [Sayi/poi-tl](https://github.com/Sayi/poi-tl)（deepoove.com/poi-tl） |
| **许可证** | Apache-2.0（开源免费） |
| **当前版本** | 1.9.1 |
| **模板定义方式** | **.docx 文件本身即模板**——`{{tag}}` 占位符 |
| **设计哲学** | *logic-less* 模板引擎（类似 Google CTemplate 理念） |

**核心特性：**
- 标签类型：文本 `{{name}}`、图片 `{{@image}}`、表格 `{{#table}}`、列表 `{{?list}}`、条件 `{{?condition}}`、循环、嵌套
- **完美保留模板样式**——标签的样式会应用到替换后的文本
- 自定义函数（插件）——「Do Anything Anywhere」理念
- 极简 API：`XWPFTemplate.compile("template.docx").render(dataMap).writeToFile("out.docx")`

**优点：** Apache 2.0 开源、Java 企业生态成熟、样式保真度高、API 极简
**缺点：** 仅 Java、生态较 docxtemplater 小、中文文档为主

### 2.4 docx4j（Java）—— 企业级 OOXML 操作

| 维度 | 详情 |
|---|---|
| **语言/生态** | Java（JAXB 直接映射 OOXML） |
| **GitHub** | [plutext/docx4j](https://github.com/plutext/docx4j)（**2.4K stars**） |
| **许可证** | Apache-2.0 |
| **定位** | Word 操作的「专家」（Apache POI 是 Excel 的王者，docx4j 是 Word 的王者） |

**核心特性：**
- 完整 OOXML 结构访问（JAXB 绑定 XML → Java 对象）
- **OpenDoPE 模板注入**——支持占位符 Word 模板 + 内容控件数据绑定
- **HTML → DOCX 导入**（ImportXHTML 模块）、Markdown → HTML → DOCX
- **PDF 转换**（三种策略：XSL-FO、documents4j via Word、Microsoft Graph 云服务）
- 文档合并/比较、数字签名、MathML 公式、字体嵌入

**优点：** 对 Word 结构控制最深、支持 PDF/HTML 导出、企业级稳定
**缺点：** 学习曲线陡（需理解 OOXML schema）、依赖较重（100+ MB）、仅支持 OpenXML（不支持旧 .doc）

### 2.5 OpenXML SDK（C#/.NET）—— 微软官方

| 维度 | 详情 |
|---|---|
| **语言/生态** | .NET（C#/VB.NET） |
| **维护方** | **Microsoft 官方** |
| **许可证** | MIT（开源免费） |
| **定位** | 强类型 OOXML 操作库（低层级 API） |

**核心特性：**
- 直接操作 .docx/.xlsx/.pptx 的 XML 结构（LINQ to XML）
- 微软官方维护，与 Office 标准对齐

**优点：** 官方支持、免费、跨平台（.NET Core/.NET 5+）
**缺点：** **低层级 API，无内置模板引擎**——需自己实现占位符替换逻辑；无 PDF 渲染能力（需第三方）；适合简单操作，复杂模板场景需大量样板代码

**与商业库对比：** Aspose.Words 官方对比指出，OpenXML SDK 适合「简单 DOCX 操作」，而 Aspose 提供邮件合并、PDF 转换、查找替换、TOC 更新等 OpenXML SDK 缺失的高级功能。

### 2.6 Aspose.Words / Spire.Doc（商业）

| 方案 | 语言 | 定位 | 关键优势 | 价格 |
|---|---|---|---|---|
| **Aspose.Words** | .NET / Java / C++ / Python | 商业全能型 | 功能最全：DOC/RTF/HTML/多格式互转、邮件合并、PDF 渲染、TOC、字段更新、打印 | 按开发者/订阅计费（较贵） |
| **Spire.Doc** | .NET / Java | 商业 Word API | 独立 API（无需 Office）、支持 Word 97-2019、水印/签名/书签 | 免费版有限制，商业版按许可 |

**适用场景：** 企业级、预算充足、需要「一个库搞定一切」（生成 + 转 PDF + 合并 + 安全）。**对个人/开源项目成本过高。**

### 2.7 Carbone（JavaScript）⭐ AI 集成友好

| 维度 | 详情 |
|---|---|
| **语言/生态** | JavaScript / Node.js |
| **官网** | [carbone.io](https://carbone.io) |
| **许可证** | 开源（核心）+ Cloud/On-premise 商业版 |
| **采用规模** | **800+ 付费客户**，40+ 国家，**1.81 亿+ 文档**自 2021 生成 |
| **模板定义方式** | **文档本身即模板**——在 Word/Excel/PPT/HTML/Markdown 中插入 `{d.variable}` 标记 |
| **支持格式** | PDF / DOCX / XLSX / PPTX / ODS / ODT / HTML / Markdown / CSV / PNG / JPEG |

**核心特性（对 AI 场景极为友好）：**
- 类 JSON 标记 `{d.companyName}`，语法直观，无需学 Handlebars/Jinja
- 强大的格式化器：`{d.date:date('yyyy-mm-dd')}`、`{d.price:number('$#,##0.00')}`
- 循环 `{#d.products}...{/d.products}`、条件 `{?d.isVIP}...{/d.isVIP}`
- **Smart conditional blocks**：`:drop(row)` / `:keep(col)` 一行标记删除/保留表格行列段落
- **原生 AI 集成**：
  - 官方 **MCP Server**（Model Context Protocol）——AI agent 可直接调用渲染
  - 官方 **Carbone Skill**——教 ChatGPT/Claude/Copilot/Gemini 写 Carbone 标签
  - 支持 ChatGPT、Claude、Copilot、Gemini、DeepSeek、Llama、Cursor、Grok 等
- 「一个模板 + 一个 JSON = 字节级一致的输出」，确定性可预测
- 多格式输出（同一模板可输出 PDF/DOCX/XLSX）

**优点：** AI 集成最深的方案、多格式、确定性输出、企业级稳定（7 年生产验证）
**缺点：** 高级功能（smart conditions、pagination 等）需 Enterprise 授权；Cloud 版按量计费

**适用场景：** 想要开箱即用的 AI 文档生成、需要 MCP 集成、跨多种 Office 格式。**Carbone 是「AI + 模板引擎」组合中工程化程度最高的方案。**

### 2.8 其他 Word 方案

| 方案 | 语言 | 特点 |
|---|---|---|
| **docx-templates**（guigrpa） | JS/TS | 在模板里写 QUERY（GraphQL 风格）、EXEC、IMAGE、LINK、HTML、FOR/END-FOR，支持 Node/浏览器/Deno |
| **DocxTemplater**（Amberg） | C#/.NET | 支持变量替换、集合绑定、条件块、图片、图表、**Markdown 转 OpenXML** |
| **DocStencil** | Kotlin/Java | 新兴项目，主打比 docx4j/Apache POI 更简洁的 API（3 行代码） |
| **docxtplrs** | Rust | docxtpl 的 Rust 实现，**比 Python 版快 6-14 倍**，零 Python 依赖，PyO3 提供 Python 绑定 |
| **Apache POI** | Java | Excel 王者，Word（XWPF）操作较繁琐，适合批量处理 |

### 2.9 Word 方案对比矩阵

| 方案 | 语言 | 许可证 | 模板形态 | 占位符语法 | 图片/富文本 | AI 集成友好度 | 中文支持 | 推荐度 |
|---|---|---|---|---|---|---|---|---|
| **docxtpl** | Python | LGPL（免费） | .docx 文件 | Jinja2 `{{}}` | ✅ 免费 | ⭐⭐⭐⭐⭐ | ✅（模板字体） | ★★★★★ |
| **docxtemplater** | JS | MIT（核心）+ 付费模块 | .docx 文件 | `{tag}` | 💰 付费 | ⭐⭐⭐⭐ | ✅ | ★★★★☆ |
| **Carbone** | JS | 开源 + 商业 | 多格式文件 | `{d.tag}` | ✅ | ⭐⭐⭐⭐⭐（MCP） | ✅ | ★★★★☆ |
| **poi-tl** | Java | Apache-2.0 | .docx 文件 | `{{tag}}` | ✅ | ⭐⭐⭐ | ✅ | ★★★★☆ |
| **docx4j** | Java | Apache-2.0 | .docx + 内容控件 | OpenDoPE | ✅ | ⭐⭐ | ✅ | ★★★☆☆ |
| **OpenXML SDK** | C# | MIT | 代码定义 | 需自实现 | 需自实现 | ⭐⭐ | ✅ | ★★☆☆☆ |
| **Aspose.Words** | 多语言 | 商业 | 多种 | 邮件合并 | ✅ | ⭐⭐ | ✅ | ★★★☆☆（预算足时） |

**结论：**
- **Python 团队 → docxtpl**（免费、Jinja2、AI 生态契合）
- **JS/Node 团队 → docxtemplater**（成熟）或 **Carbone**（AI 集成最深）
- **Java 企业团队 → poi-tl**（简洁）或 **docx4j**（深度控制）
- **想要开箱即用 AI 集成 → Carbone**（MCP Server 现成）

---

## 3. B. LaTeX 模板系统

LaTeX 本身就是「模板引擎」的祖宗——`\documentclass` + `\usepackage` 就是模板继承机制。本节聚焦如何让 AI 按用户提供的 LaTeX 模板输出。

### 3.1 LaTeX 原生模板机制

LaTeX 的模板能力体现在三个层级：

| 层级 | 机制 | 示例 |
|---|---|---|
| **文档类** | `\documentclass{ctexart}` / `{report}` / `{book}` / 自定义 `.cls` | harryopo-paper.cls |
| **样式包** | `\usepackage{...}` / 自定义 `.sty` | harryopo-base.sty |
| **主题** | beamer 主题 `\usetheme{Madrid}`、ctex 字体主题、moderncv 主题 | beamer themes |

**模板继承最佳实践（与 harryopo 项目一致）：**
- 共享体系通过 `harryopo-base.sty` 统一加载，用 `\ifdefined\harryopo@theme` 传递主题
- 各文档类（paper/report/book/notes）加载 base.sty
- 用户只需 `\documentclass{harryopo-paper}` 即继承全部样式

**优点：** 排版质量天花板最高、学术生态完善、版本控制友好
**缺点：** 学习曲线陡、编译慢、报错晦涩、宏包冲突

### 3.2 Pandoc + 自定义模板 ⭐ 跨格式枢纽

Pandoc 是文档格式转换的「瑞士军刀」，其模板机制是连接 AI 与多种输出格式的关键枢纽。

| 维度 | 详情 |
|---|---|
| **官方** | [pandoc.org](https://pandoc.org) |
| **许可证** | GPL-2.0（开源免费） |
| **核心机制** | Reader（解析）→ AST（抽象语法树）→ Writer（输出）|

**两种模板机制（关键区分）：**

1. **`--reference-doc`（参考文档，用于 docx/odt/pptx）**
   - 指定一个 .docx 作为样式来源
   - 继承其字体、标题样式、页边距、页眉页脚
   - 命令：`pandoc input.md -o output.docx --reference-doc=custom_template.docx`
   - 生成默认模板：`pandoc --print-default-data-file reference.docx > reference.docx` 再修改
   - **样式映射**：LaTeX `\section{}` → Word Heading 1 样式，确保结构化转换

2. **`--template`（模板文件，用于 LaTeX/HTML/typst/epub 等）**
   - 指定一个文本模板文件（含变量占位符）
   - 生成默认模板：`pandoc -D latex > template.tex` 或 `pandoc -D typst > template.typ`
   - 模板内可用 `$title$`、`$body$`、`$for$` 等变量
   - 支持 Lua filter 自定义转换逻辑

**限制：**
- Pandoc 的 AST 表达力 < LaTeX，复杂 LaTeX 命令会丢失（「plain pandoc 能到 90%，最后 10% 需手动」）
- 自定义样式名映射需用 `custom-style` 属性或修改 docx template（Pandoc 3.2.1+ 支持）
- 数学公式、复杂表格、浮动体可能转换不完美

**适用场景：** AI 产出 Markdown/结构化文本 → Pandoc 按用户模板转 docx/pdf/html。**这是「一份内容，多格式输出」的最佳枢纽。**

### 3.3 从结构化数据（YAML/JSON）→ LaTeX 的生成器 ⭐ AI 友好

这是 AI 场景下最优雅的 LaTeX 方案：**AI 产出 YAML/JSON，生成器渲染成 LaTeX**。

#### 代表项目

| 项目 | 说明 |
|---|---|
| **Jinja2 + LaTeX** | 用 Jinja2 模板化 .tex 文件，AI 填充 YAML 数据。论文级方案：`Jinja2 负责排版，LLM+RAG 负责内容，YAML 负责结构化` |
| **RenderCV** | [rendercv/rendercv](https://github.com/rendercv/rendercv)——从 YAML 生成高质量 LaTeX 简历 PDF，支持 Markdown、完全控制 LaTeX 代码 |
| **cv-tool** | [wbthomason/cv-tool](https://github.com/wbthomason/cv-tool)——YAML/TOML/JSON → LaTeX/PDF/Markdown/HTML 简历 |
| **thesis-generator** | [davidcurie/thesis-generator](https://github.com/davidcurie/thesis-generator)——Pandoc + Makefile 自动化论文生成 |

#### 典型架构（AI + YAML + LaTeX）

```
meta.yaml（结构化数据）
  ├─ thesis: title/author/supervisor
  ├─ chapters: [{id, name, prompts}]
  ├─ figures: [{label, path, caption}]
  └─ tables: [{label, path, caption}]
        ↓ LLM 按 prompts 生成章节内容
        ↓ Jinja2 渲染 template.tex
build/thesis.tex
        ↓ xelatex 编译
thesis.pdf
```

**优点：** 内容与排版完全分离、Git 友好、AI 只需产出结构化数据、可复用学术模板
**缺点：** 需自己搭建生成管线、LaTeX 编译环境配置复杂

**这正是 harryopo 项目可以采纳的架构**——用户提供 harryopo 模板，AI 产出 YAML，Jinja2 渲染成 .tex，XeLaTeX 编译。

### 3.4 Typst 作为 LaTeX 替代品 ⭐ 值得关注

Typst 是用 Rust 编写的现代排版系统，定位为 LaTeX 的强力竞争者。

| 维度 | Typst | LaTeX |
|---|---|---|
| **学习曲线** | 平缓（类 Markdown 语法） | 陡峭（命令式语法） |
| **编译速度** | **毫秒级**（增量编译） | 秒级（全量重编译） |
| **语法简洁性** | `= 标题`、`*加粗*`、`+ 列表` | `\section{}`、`\textbf{}`、`\begin{itemize}` |
| **2000 页编译** | **~1 分钟** | ~18 分钟（LuaLaTeX） |
| **错误提示** | 友好精确（代码位置定位） | 晦涩难懂（TeX 底层错误） |
| **样板代码** | 0 行（合理默认值） | ~30 行（documentclass + 大量 usepackage） |
| **脚本能力** | 一等公民函数（`#let f(x) = x+1`） | 宏（`\newcommand`） |
| **数据解析** | 内置 TOML/JSON | 需 datatool 等包 |
| **生态** | Typst Universe（**1300+ 包**，2025） | CTAN（数十年积累） |
| **学术接受度** | 增长中（arXiv 提交增长） | 事实标准 |

**Typst 的模板能力：**
- 官方模板仓库：[typst/templates](https://github.com/typst/templates)
- 模板教程：[typst.app/docs/tutorial/making-a-template](https://typst.app/docs/tutorial/making-a-template/)
- Typst Universe：[typst.app/universe](https://typst.app/universe/)
- **Pandoc 原生支持**：`pandoc input.md --to=typst --pdf-engine=typst`（迁移成本极低）

**优点：** 速度快 10-100 倍、语法现代、错误清晰、模板能力强、Pandoc 集成
**缺点：** 生态远小于 LaTeX、出版商接受度待提升、中文支持仍在完善（CJK 已支持但不如 ctex 成熟）

**适用场景：** 新项目、追求速度与现代体验、愿意尝试新生态。**对 harryopo 这种已有 LaTeX 沉淀的项目，Typst 可作为并行试验，不建议立即替换。**

---

## 4. C. PDF 模板方案

PDF 是最终交付物，生成路径主要有三条：HTML/CSS → PDF、LaTeX → PDF、组件式 PDF。

### 4.1 HTML/CSS → PDF（设计型 PDF 首选）

#### WeasyPrint（Python）⭐

| 维度 | 详情 |
|---|---|
| **官网** | [weasyprint.org](https://weasyprint.org) |
| **许可证** | BSD-3-Clause（开源免费） |
| **引擎** | **自有 CSS 引擎**（非浏览器内核） |
| **JS 支持** | ❌ 不执行 JavaScript |
| **CSS** | 现代 CSS（CSS3 属性、媒体查询） |
| **Paged Media** | ✅ 支持 W3C 分页媒体（页眉页脚、页码） |
| **评分**（综合评测） | 渲染 4/5、CSS 3/5、Python 集成 5/5、安装 5/5、性能 3/5 |

**优点：** 纯 Python、无外部二进制依赖、CSS 标准合规、pip 安装、持续维护
**缺点：** 不执行 JS、Flexbox 支持不全、无 Grid、z-index 定位偶有问题、批量性能一般

**适用场景：** Python 技术栈、模板是 HTML/CSS、需要分页媒体支持、无需 JS。**与 Jinja2 模板搭配是 Python 生态的经典组合。**

#### Paged.js

| 维度 | 详情 |
|---|---|
| **官网** | [pagedjs.org](https://pagedjs.org) |
| **定位** | W3C 分页媒体标准的 **polyfill**（让浏览器支持 print CSS） |
| **引擎** | 浏览器（Chromium） |
| **JS 支持** | ✅ |
| **架构** | chunker（分页）+ polisher（样式处理）+ previewer（预览编排） |

**优点：** 让 Web 设计师用熟悉工具做印刷品、支持完整 W3C paged media、可预览可调试
**缺点：** 依赖浏览器环境、相对小众、Chromium 131+ 已原生支持部分 margin-box（未来可能被浏览器原生替代）

#### Puppeteer / Playwright（Headless Chromium）⭐ 像素完美

| 维度 | 详情 |
|---|---|
| **引擎** | Headless Chromium（真实浏览器内核） |
| **CSS 支持** | **5/5**（完整现代 CSS：Flexbox、Grid、动画） |
| **JS 支持** | ✅（完整） |
| **渲染质量** | **5/5**（与 Chrome 显示一致） |
| **依赖** | ~170MB Chromium 二进制 |
| **性能** | 2-3 秒/页 |

**优点：** 像素完美、支持所有现代 Web 技术（web fonts、flexbox、grid、canvas、SVG）
**缺点：** 依赖重、性能不如 WeasyPrint、需管理浏览器生命周期

**适用场景：** 模板用了现代 CSS（Flexbox/Grid）、需要像素完美、有图表/Canvas。**社区评测结论：长期应从 WeasyPrint 迁移到 Playwright 以获得更好渲染质量。**

#### 其他 HTML→PDF

| 方案 | 语言 | 特点 | 状态 |
|---|---|---|---|
| **wkhtmltopdf** | CLI | WebKit 内核 | ⚠️ **2020 年已归档，停止维护，不推荐新项目** |
| **OpenHTMLtoPDF + PDFBox** | Java | 企业级 HTML→PDF，支持加密/水印/权限控制 | 活跃，需手动加载中文字体 |
| **xhtml2pdf** | Python | 轻量，内置 CJK 字体（STSong-Light 等） | 适合简单场景 |
| **boxpdf-html** | JS | 基于 boxpdf，提供 **MCP server** 供 AI agent 调用 | AI 友好 |
| **Gotenberg** | Docker | 包装 Chromium 的微服务 API | 适合微服务架构 |

### 4.2 LaTeX → PDF 模板化

这是 harryopo 项目的核心路径。关键点：
- 用户提供 `.cls`/`.sty` 模板（如 harryopo-paper.cls）
- AI 产出 LaTeX 源码或结构化数据（经 Jinja2 渲染）
- XeLaTeX 编译成 PDF
- **编译必须 3 遍**以保证交叉引用和目录稳定

详见第 3 节 LaTeX 模板系统。

### 4.3 组件式 PDF（React-based）

#### react-pdf ⭐

| 维度 | 详情 |
|---|---|
| **官网** | [react-pdf.org](https://react-pdf.org) |
| **GitHub** | [diegomura/react-pdf](https://github.com/diegomura/react-pdf) |
| **定位** | 用 React 组件声明式构建 PDF |

**核心特性：**
- 组件化：`<Document>`、`<Page>`、`<View>`、`<Text>`、`<Image>`
- StyleSheet API（类 React Native）：`StyleSheet.create()`、inline style、media queries
- 支持 Flexbox、变换、边框、字体注册
- **不基于 HTML/CSS**——是 React 组件直出 PDF 的独立渲染层

#### Tailwind + react-pdf 生态（新兴）

| 库 | 特点 |
|---|---|
| **react-pdf-tailwind** | 将 Tailwind 类转成 react-pdf 样式对象，**已支持 Tailwind v4** |
| **tw-pdf** | react-pdf fork，原生 Tailwind className 支持 |
| **tailwind-to-react-pdf** | Tailwind 类 → react-pdf 样式，支持 Recharts 图表转换 |
| **windy-pdf** | 改 import 即可用 className |

**优点：** 前端开发者熟悉、组件可复用、设计系统化、Tailwind 生态
**缺点：** 生态较新、不依赖浏览器但需 Node、中文需手动注册字体

**适用场景：** React/前端团队、需要组件化设计系统、发票/收据/报告等结构化 PDF。

### 4.4 PDF 方案对比矩阵

| 方案 | 路径 | 模板形态 | CSS 支持 | JS | 中文 | 性能 | 推荐度 |
|---|---|---|---|---|---|---|---|
| **WeasyPrint** | HTML/CSS→PDF | HTML+CSS | 现代CSS（无Grid） | ❌ | 需配字体 | 中 | ★★★★☆（Python） |
| **Puppeteer/Playwright** | HTML/CSS→PDF | HTML+CSS | **5/5** | ✅ | ✅ | 慢 | ★★★★☆（像素完美） |
| **Paged.js** | HTML/CSS→PDF | HTML+CSS+paged | 完整 | ✅ | ✅ | 中 | ★★★☆☆ |
| **react-pdf** | 组件→PDF | React组件 | 子集 | N/A | 需注册字体 | 快 | ★★★★☆（前端） |
| **LaTeX→PDF** | .tex→PDF | .cls/.sty | N/A | N/A | ✅（ctex） | 慢 | ★★★★★（学术） |
| **Typst→PDF** | .typ→PDF | .typ模板 | N/A | N/A | 改进中 | **极快** | ★★★★☆（新兴） |

---

## 5. D. 通用文档生成框架与 AI 集成

### 5.1 jsreport —— 企业级报告平台 ⭐

| 维度 | 详情 |
|---|---|
| **官网** | [jsreport.net](https://jsreport.net) |
| **许可证** | 开源（核心）+ 商业版 |
| **定位** | 基于 JavaScript 的**企业级报告设计与渲染平台** |

**核心架构（engine + recipe 分离）：**
- **Engine**（模板引擎）：Handlebars、JS Render、EJS、pug、docxtemplater、nunjucks、none
- **Recipe**（输出配方）：chrome-pdf、phantom-pdf、weasyprint、html-to-xlsx、docxtemplater、pptx 等
- **Studio**：Web 图形化设计器，非技术人员可创建报告
- **功能**：用户管理、权限控制、REST API、定时任务、邮件发送、版本控制、子报告、备份

**优点：** 一站式平台、可视化设计器、多引擎多格式、企业级功能完善
**缺点：** 需部署独立服务、学习曲线、对个人项目偏重

**适用场景：** 企业级批量报告生成、需要可视化设计器、多格式输出。

### 5.2 DocuSeal —— 开源文档签署与填充平台

| 维度 | 详情 |
|---|---|
| **官网** | [docuseal.co](https://www.docuseal.co) |
| **GitHub** | [docusealco/docuseal](https://github.com/docusealco/docuseal) |
| **许可证** | AGPLv3（开源） |
| **定位** | 开源电子签名 + PDF 表单填充平台 |

**核心特性：**
- WYSIWYG PDF 表单构建器（12 种字段类型：签名、日期、文件、复选框等）
- 多签署方、签名验证、移动优化、审计跟踪
- Docker 一键部署，数据完全自主
- REST API + Webhooks

**定位澄清：** DocuSeal 主打**签署工作流**，而非「模板渲染」。它适合「PDF 表单 → 填充 → 签署」场景，不完全匹配「AI 按模板生成文档」诉求，但其表单填充能力可借鉴。

### 5.3 Papermerge —— 文档管理系统

| 维度 | 详情 |
|---|---|
| **官网** | [papermerge.com](https://papermerge.com) |
| **许可证** | Apache-2.0 |
| **定位** | 扫描文档**管理**系统（DMS） |

**核心特性：** OCR（Tesseract，100+ 语言）、版本控制、自定义字段、分类、页面管理
**定位澄清：** Papermerge 是**文档归档与检索**系统，非文档生成工具。与本调研诉求关联度低，列出仅供区分。

### 5.4 AI 集成的关键技术：结构化输出

要让 AI 可靠地产出「符合模板 schema 的数据」，核心是 **结构化输出（Structured Output）**技术：

| 方法 | 说明 | 代表 |
|---|---|---|
| **Structured Outputs**（API 原生） | 定义 JSON schema，模型保证合规 | OpenAI、Anthropic、Gemini |
| **Function Calling** | 模型调用预定义函数，参数结构化 | OpenAI、Claude |
| **JSON Mode** | 强制输出合法 JSON | OpenAI |
| **PydanticOutputParser** | Pydantic 模型 → 格式指令 → 解析验证 | LangChain |
| **Instructor** | 基于 Pydantic 的结构化输出库 | instructor |
| **Outlines** | 模型级强制结构化（grammar 约束） | outlines |

**典型流程：**
```
1. 从模板提取占位符 schema（docxtpl.get_undeclared_template_variables()）
2. 将 schema 注入 LLM prompt（structured output / function calling）
3. LLM 产出符合 schema 的 JSON
4. 模板引擎渲染（docxtpl.render(json)）
5. 输出保真文档
```

来源：[IBM JSON prompting for LLMs](https://developer.ibm.com/articles/json-prompting-llms/)、[Agenta structured outputs guide](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)、[LangChain 格式化生成](https://github.com/qinxingkun/all-in-rag/blob/main/docs/chapter5/16_formatted_generation.md)

### 5.5 「最后一公里」问题的实战解法

Amazon Bedrock 团队的实战方案（被广泛引用的最佳实践）：

```
LLM 强制输出 Markdown
    ↓ Regex 清洗标准化
标准化 Markdown
    ↓ python-docx + 映射规则
保真 .docx（# → Heading 1，** → bold，表格 → Word 表格）
```

**映射规则示例：**
- `# 标题` → Word Heading 1（保证文档大纲与导航）
- `**加粗**` → bold run
- Markdown 表格 → Word 表格（保持列宽）
- 列表 → Word 列表样式

**优点：** 简单、快速、可审计、高度一致
**缺点：** 仍是「先生成再转换」，不如「模板填充」保真度高

来源：[Red Oak Strategic - Solving the Gen AI Last Mile Problem](https://blog.redoakstrategic.com/solving-the-genai-last-mile-problem)

---

## 6. 综合对比矩阵

### 6.1 全方案横向对比（按输出格式分组）

| 输出 | 方案 | 语言 | 模板形态 | AI 职责 | 保真度 | 成本 | 中文 |
|---|---|---|---|---|---|---|---|
| **Word** | docxtpl | Python | .docx | JSON 数据 | ★★★★★ | 免费 | ✅ |
| **Word** | docxtemplater | JS | .docx | JSON 数据 | ★★★★★ | 核心免费+模块付费 | ✅ |
| **Word** | Carbone | JS | 多格式 | JSON + MCP | ★★★★★ | 开源+商业 | ✅ |
| **Word** | poi-tl | Java | .docx | Map 数据 | ★★★★★ | 免费 | ✅ |
| **LaTeX** | Jinja2+LaTeX | Python | .cls/.sty+.tex | YAML/JSON | ★★★★★ | 免费 | ✅（ctex） |
| **LaTeX** | Pandoc+template | 多 | .tex/.docx | Markdown | ★★★★☆ | 免费 | ✅ |
| **LaTeX** | Typst | 多 | .typ | Typst源码/数据 | ★★★★☆ | 免费 | 改进中 |
| **PDF** | WeasyPrint | Python | HTML+CSS | HTML/数据 | ★★★★☆ | 免费 | 需配字体 |
| **PDF** | Puppeteer | JS | HTML+CSS | HTML/数据 | ★★★★★ | 免费 | ✅ |
| **PDF** | react-pdf | JS | React组件 | 组件props | ★★★★☆ | 免费 | 需注册 |
| **PDF** | LaTeX→PDF | 多 | .cls/.sty | LaTeX/数据 | ★★★★★ | 免费 | ✅ |

### 6.2 「用户提供模板 → 保持原样式输出」能力对比

| 能力 | docxtpl | docxtemplater | Carbone | Pandoc | WeasyPrint | LaTeX |
|---|---|---|---|---|---|---|
| 用户用熟悉工具设计模板 | ✅ Word | ✅ Word | ✅ Word/Excel/PPT | ✅ Word(ref-doc) | ✅ 任意HTML编辑器 | ✅ TeX编辑器 |
| 模板即文件本身 | ✅ .docx | ✅ .docx | ✅ 多格式 | ✅ .docx | ✅ .html | ✅ .tex |
| 非程序员可维护模板 | ✅ | ✅ | ✅ | ⚠️ 部分 | ⚠️ 需懂CSS | ❌ |
| 占位符保真渲染 | ✅ | ✅ | ✅ | ⚠️ 样式映射 | ✅ | ✅ |
| AI 产出数据即可 | ✅ JSON | ✅ JSON | ✅ JSON+MCP | ⚠️ Markdown | ✅ HTML/JSON | ✅ JSON |
| 字体/样式继承 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 中文支持 | ✅ | ✅ | ✅ | ✅ | 需配置 | ✅ |
| 免费 | ✅ | 核心免费 | 核心免费 | ✅ | ✅ | ✅ |

---

## 7. 最佳技术路线推荐

### 7.1 总体推荐：「数据-模板分离」三件套

针对用户诉求「给几个喜欢的 Word、LaTeX 模板，AI 按模板输出」，**最佳技术路线是：**

```
┌─────────────────────────────────────────────────┐
│  用户模板层：用户在 Word/LaTeX/HTML 中设计模板    │
│  （插入 {{占位符}} / {d.tag} / Jinja2 标签）      │
└────────────────────┬────────────────────────────┘
                     ↓ 提取 schema
┌─────────────────────────────────────────────────┐
│  AI 层：LLM + Structured Output                  │
│  （function calling / JSON schema / Pydantic）   │
│  产出：符合模板 schema 的结构化数据              │
└────────────────────┬────────────────────────────┘
                     ↓ JSON/YAML
┌─────────────────────────────────────────────────┐
│  渲染层：模板引擎保真渲染                         │
│  docxtpl / Jinja2+LaTeX / WeasyPrint / Carbone  │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  输出层：保持模板原样式的 .docx / .pdf            │
└─────────────────────────────────────────────────┘
```

### 7.2 按输出格式的具体推荐

#### 📄 Word 输出

| 场景 | 首选 | 理由 |
|---|---|---|
| **Python/AI 团队** | **docxtpl** | 免费、Jinja2 表达力强、与 AI 生态契合、图片富文本免费 |
| **JS/Node 团队** | **docxtemplater** 或 **Carbone** | docxtemplater 成熟；Carbone 有现成 MCP，AI 集成最深 |
| **Java 企业** | **poi-tl** | Apache-2.0、API 极简、样式保真 |
| **想开箱即用** | **Carbone** | 官方 MCP Server + Skill，ChatGPT/Claude 直接调用 |
| **预算充足企业** | **Aspose.Words** | 一个库搞定生成+PDF+合并+安全 |

#### 📑 PDF 输出

| 场景 | 首选 | 理由 |
|---|---|---|
| **学术/论文/书籍** | **LaTeX 模板（harryopo）+ Jinja2** | 排版质量天花板、harryopo 已有沉淀 |
| **设计型/商务报告** | **HTML/CSS 模板 + WeasyPrint（Python）或 Puppeteer（JS）** | 设计灵活、现代 CSS；WeasyPrint 适合 Python，Puppeteer 像素完美 |
| **新兴/追求速度** | **Typst 模板** | 编译快 10-100 倍、语法现代、Pandoc 支持 |
| **前端/组件化** | **react-pdf + Tailwind** | 组件复用、设计系统化 |

#### 🔀 跨格式（一份模板多输出）

| 场景 | 首选 | 理由 |
|---|---|---|
| **AI 原生集成** | **Carbone** | 一个模板 → PDF/DOCX/XLSX/PPTX，MCP 现成 |
| **内容为中心** | **Pandoc + 多 writer 模板** | Markdown → docx/pdf/html/epub，reference-doc + template |
| **企业级平台** | **jsreport** | 可视化设计器、多引擎多格式、调度与权限 |

### 7.3 针对 harryopo 项目的具体建议

鉴于 harryopo 已是 LaTeX 模板体系，且项目规则要求 XeLaTeX 编译：

1. **LaTeX 路径（核心）**：
   - 用户提供 harryopo `.cls`/`.sty` 模板
   - AI 产出 YAML/JSON 结构化数据（章节、图表、参考文献）
   - Jinja2 渲染 `template.tex` → `thesis.tex`
   - XeLaTeX 编译 3 遍 → PDF
   - **已有参考实现**：论文级方案「Jinja2 负责排版，LLM+RAG 负责内容，YAML 负责结构化」

2. **Word 路径（补充）**：
   - 用 **docxtpl**（Python，与 AI 生态契合）
   - 用户提供 .docx 模板（含 `{{占位符}}`）
   - AI 产出 JSON → docxtpl 渲染
   - 可用 `get_undeclared_template_variables()` 自动提取模板 schema 喂给 AI

3. **PDF 设计型路径（补充）**：
   - HTML/CSS 模板 + WeasyPrint（若需现代设计感）
   - 或直接走 LaTeX（若需学术排版质量）

4. **试验性**：关注 **Typst**，作为 LaTeX 的现代补充，但暂不替换现有体系。

---

## 8. AI 集成架构建议

### 8.1 推荐架构：模板 schema 驱动的 AI 文档生成

```
┌──────────────────────────────────────────────────────────┐
│ Step 1: 模板注册                                          │
│ 用户上传模板（.docx / .tex / .html）                      │
│ 系统自动提取占位符 schema                                 │
│   - docxtpl: get_undeclared_template_variables()          │
│   - LaTeX: 解析 \command{} 与 Jinja2 {{}} 标签            │
│   - HTML: 解析 {{}} / data-* 属性                         │
└────────────────────┬─────────────────────────────────────┘
                     ↓ schema
┌──────────────────────────────────────────────────────────┐
│ Step 2: AI 生成（Structured Output）                      │
│ System Prompt:                                           │
│   "根据以下 schema 产出 JSON，字段缺失返回 null，禁止幻觉" │
│ 方法: function calling / JSON schema / Pydantic          │
│ 输出: 符合 schema 的 JSON/YAML                            │
└────────────────────┬─────────────────────────────────────┘
                     ↓ JSON
┌──────────────────────────────────────────────────────────┐
│ Step 3: 模板渲染（保真）                                  │
│   - Word: docxtpl.render(json) → .docx                   │
│   - LaTeX: Jinja2 render → .tex → XeLaTeX → .pdf         │
│   - PDF: Jinja2 render → HTML → WeasyPrint/Puppeteer     │
│ 输出: 保持模板原样式的文档                                │
└──────────────────────────────────────────────────────────┘
```

### 8.2 关键实现要点

1. **模板 schema 提取自动化**——让 AI 知道该填什么
   - docxtpl: `doc.get_undeclared_template_variables()`
   - LaTeX: 解析 `\title{}`、`\author{}`、Jinja2 `{{ var }}`
   - 输出 JSON Schema 喂给 LLM 的 structured output

2. **强制结构化输出**——杜绝 AI 自由发挥
   - 优先用 API 原生 structured output / function calling
   - 备选用 Pydantic + Instructor / Outlines 做约束

3. **Prompt 模板化**——「你是一个文档数据提取引擎，接收 X，按 schema 产出 JSON，字段缺失返回 null，禁止幻觉」

4. **渲染与 AI 解耦**——AI 永远不碰二进制格式，只产出数据；模板引擎负责保真

5. **中文字体显式配置**——所有渲染层（WeasyPrint、react-pdf、OpenHTMLtoPDF）都需手动加载中文字体，不能依赖系统字体

### 8.3 避免「让 AI 直接生成文档」的陷阱

根据多个实战案例（remio.ai、Azure AI Foundry 社区、Amazon Bedrock 团队）：

| ❌ 错误做法 | ✅ 正确做法 |
|---|---|
| 让 AI 直接产出 .docx 二进制 | AI 产出 JSON，docxtpl 渲染 |
| 让 AI 产出 Markdown 再转 Word（样式全丢） | AI 产出结构化数据，模板引擎保真填充 |
| 让 AI 操作 OOXML | AI 产出数据，专用引擎处理 OOXML |
| 让 Copilot 在 Word 侧边栏填充模板 | 用独立 AI（ChatGPT/Claude）+ structured output + 外部渲染 |
| 期望 AI「理解」视觉布局 | 把布局编码为 schema，AI 只填数据 |

**唯一例外：HTML + Jinja2 法**（remio.ai 推荐的「黄金修复」）——把 Word 模板转成 HTML + Jinja2 占位符，AI 产出 HTML 片段，再转 Word/PDF。适合 Copilot 等受限场景。

---

## 9. 参考资料

### Word/docx 模板引擎

- docxtemplater 官方：https://docxtemplater.com/
- docxtemplater GitHub：https://github.com/open-xml-templating/docxtemplater
- docxtemplater FAQ（定价）：https://docxtemplater.com/faq/
- docxtpl 官方文档：https://docxtpl.readthedocs.io/
- docxtpl PyPI：https://pypi.org/project/docxtpl/
- docxtpl GitHub：https://github.com/elapouya/python-docx-template
- docxtpl 全面指南（CSDN）：https://blog.csdn.net/liaoqingjian/article/details/156860640
- Carbone 官网：https://carbone.io/
- Carbone ChatGPT 集成：https://carbone.io/integration/chatgpt.html
- Carbone Markdown 模板：https://carbone.io/documentation/design/template-formats/markdown.html
- Carbone Smart Conditions：https://carbone.io/documentation/design/conditions/smart-conditions.html
- poi-tl GitHub：https://github.com/Sayi/poi-tl
- docx4j GitHub：https://github.com/plutext/docx4j
- docx4j 示例（DeepWiki）：https://deepwiki.com/plutext/docx4j/5-examples-and-use-cases
- Apache POI vs docx4j vs OpenXML SDK：https://blog.fileformat.com/ja/word-processing/apache-poi-vs-docx4j-vs-openxml-sdk-which-one-should-you-use/
- Aspose.Words vs OpenXML SDK：https://docs.aspose.com/words/net/aspose-words-or-open-xml-sdk/
- Aspose.Words 缺失功能：https://docs.aspose.com/words/net/missing-features-in-openxml/
- OpenXML SDK vs Spire.Doc：https://qiita.com/Codingll/items/367478616fd25b66074a
- docx-templates（npm）：https://www.npmjs.com/package/docx-templates
- docxtplrs（Rust）：https://crates.io/crates/docxtplrs

### LaTeX / Pandoc / Typst

- Pandoc 用户手册：https://pandoc.org/MANUAL.html
- Pandoc 自定义 docx 样式：https://wenku.csdn.net/answer/4rfp3vsq63ss
- Pandoc LaTeX→docx 自定义样式（GitHub 讨论）：https://github.com/jgm/pandoc/discussions/10045
- tex-to-docx 实战：https://github.com/berendgort/tex-to-docx
- Typst 官网：https://typst.app/
- Typst 学术综述论文：https://reunir.unir.net/server/api/core/bitstreams/5d0a591f-e527-4a5d-afdf-ea54fc7de526/content
- Typst with Pandoc：https://slhck.info/software/2025/10/25/typst-pdf-generation-xelatex-alternative.html
- LaTeX vs Typst：https://www.advancedmath.org/LaTeX/LaTeX_vs_Typst.html
- AI 辅助毕业设计（YAML+LaTeX）：https://blog.csdn.net/2600_94959957/article/details/157564830
- RenderCV：https://github.com/rendercv/rendercv
- cv-tool：https://github.com/wbthomason/cv-tool
- thesis-generator：https://github.com/davidcurie/thesis-generator

### PDF 生成

- HTML→PDF 开源库大全：https://github.com/transformyio/html-to-pdf-libraries
- Paged.js 介绍：https://pagedjs.org/posts/en/paged.js-next-an-introduction/
- WeasyPrint vs 传统 PDF 工具：https://blog.csdn.net/gitblog_00132/article/details/152068997
- PDF Renderer 评测：https://github.com/athola/simple-resume/wiki/PDF-Renderer-Evaluation
- OpenHTMLtoPDF + PDFBox 实战：https://blog.csdn.net/qq_41520636/article/details/154959906
- react-pdf 样式：https://react-pdf.org/styling
- react-pdf-tailwind：https://github.com/aanckar/react-pdf-tailwind
- boxpdf-html（MCP）：https://www.npmjs.com/package/boxpdf-html

### AI 集成与通用框架

- AI 保留 Word 格式（CSDN）：https://ask.csdn.net/questions/9004167
- Copilot 排版修复（remio.ai）：https://www.remio.ai/post/microsoft-copilot-won-t-create-documents-3-hacks-to-fix-formatting-and-template-issues
- GenAI 最后一公里（Amazon Bedrock）：https://blog.redoakstrategic.com/solving-the-genai-last-mile-problem
- Azure AI Foundry 填充 Word 模板：https://learn.microsoft.com/en-ca/answers/questions/5534699/ai-foundry-populate-a-microsoft-word-template
- JSON prompting for LLMs（IBM）：https://developer.ibm.com/articles/json-prompting-llms/
- 结构化输出指南（Agenta）：https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms
- LangChain 格式化生成：https://github.com/qinxingkun/all-in-rag/blob/main/docs/chapter5/16_formatted_generation.md
- AI 表单填充工具（IBM）：https://developer.ibm.com/tutorials/generative-ai-form-filling-tool/
- Power Platform 文档提取填充：https://community.powerplatform.com/forums/thread/details/?threadid=4a1b650b-5ec1-f011-bbd3-000d3a110039
- jsreport 官网：https://jsreport.net/
- DocuSeal GitHub：https://github.com/docusealco/docuseal
- Papermerge：https://papermerge.com/

---

> **报告完**
> 本报告基于 2026-08-08 的全网调研。建议在采用任何方案前，用真实模板做小规模 POC 验证中文支持、样式保真、AI 集成难度。对 harryopo 项目，优先深化 LaTeX + Jinja2 + YAML 路径，并行试验 docxtpl（Word）与 Typst（现代排版）。
