# 办公 Agent 与 AI 文档助手：文档处理与 PDF 生成深度调研报告

> **调研日期**：2026-08-05
> **调研范围**：2025-2026 年主流办公 Agent、AI 文档工具、数学建模 Agent、AI Agent 框架
> **调研目标**：为 harryopo LaTeX 模板体系提供业界对照与借鉴价值评估
> **调研方法**：agent-reach 多平台路由 + WebSearch + GitHub gh CLI 并行检索

---

## 执行摘要

2026 年 AI 办公赛道经历了过去十年最剧烈的方向调整，呈现出三条清晰的工艺路线：

1. **Word/Office 路线**（微软 Copilot、WPS AI、腾讯文档、钉钉）：以 Python 代码解释器 / SDK 操作 Office 文档对象模型为主，PDF 由 Word 转 PDF 生成，**风格偏向商业文档**，公式支持弱。
2. **LaTeX 路线**（Claude Artifacts、数学建模 Agent、学术工具链）：以 LaTeX 源码 + XeLaTeX 编译为主，**风格偏向学术排版**，公式支持强，是竞赛论文的事实标准。
3. **新型排版路线**（Typst、Quarto+Typst）：Typst 作为 LaTeX 挑战者快速崛起，部分数学建模 Agent 已从 LaTeX 迁移到 Typst（如 MathModelAgent 内置 17 套 Typst 模板）。

**关键发现**：所有面向学术 / 竞赛的 AI Agent 几乎清一色走 LaTeX 或 Typst 路线，**没有一个走纯 Word 路线**（仅 XiaoMaColtAI/math-modeling-skill 提供 DOCX 输出选项）。这与 harryopo 走 XeLaTeX + ctex 的技术选型高度一致。

---

## 一、大厂办公 Agent（文档处理 + PDF 生成）

### 1.1 微软 Copilot / Microsoft 365 Copilot

| 维度 | 详情 |
|---|---|
| **技术栈** | Python 代码解释器（Copilot Studio / AI Builder）+ Power Automate + Microsoft Graph API |
| **文档生成流程** | (1) Agent 写 Python 代码操作 Word/Excel/PPT 对象模型；或 (2) Power Automate 填充 SharePoint 上的 Word 模板 → 自动转 PDF |
| **PDF 输出风格** | **Word 风格**（Office 原生渲染） |
| **公式/表格/图表** | 公式弱（依赖 Word Equation Editor），表格强（Excel 引擎），图表强（Python matplotlib/Plotly） |
| **后端 PDF 转换** | `GET /drive/items/{item-id}/content?format=pdf`（Graph API 服务端转换） |
| **开源/API** | 闭源；提供 Microsoft Graph API（商业，需 M365 许可） |
| **定价** | 需 Microsoft 365 Copilot 许可（约 $30/用户/月） |
| **借鉴价值** | ⭐⭐（2/5）— 与 harryopo 学术路线差异大，但 Power Automate 的"模板填充→编译"思路可借鉴 |

### 1.2 Google Workspace AI / Gemini

| 维度 | 详情 |
|---|---|
| **技术栈** | Gemini 应用 + 服务器端文件渲染 |
| **文档生成流程** | 2026-04-29 发布：一条 prompt 直接在对话中生成 11 种格式文件 |
| **支持格式** | Docs/Sheets/Slides、Word(.docx)、Excel(.xlsx)、**PDF**、CSV、**LaTeX**、Markdown、TXT、RTF |
| **PDF 输出风格** | **自定义**（取决于格式）；LaTeX/Markdown 输出由第三方工具（如 MarkdownTools）通过 Chromium 服务端渲染成 PDF |
| **公式/表格/图表** | 公式弱（Docs 不原生渲染 Markdown 数学），表格强（Sheets 引擎），图表中等 |
| **开源/API** | 闭源；Gemini API（商业） |
| **定价** | 基础免费；Gemini Advanced 约 ¥2,900/月 |
| **借鉴价值** | ⭐⭐⭐（3/5）— 支持 LaTeX 输出值得关注，说明 Gemini 瞄准学术 / 开发者细分 |

### 1.3 WPS AI / 金山办公

| 维度 | 详情 |
|---|---|
| **技术栈** | 自研跨平台文档内核（KOffice Engine）+ WPS StartKit Java SDK + GPT-4 引擎（合同条款提取） |
| **文档生成流程** | 编辑 WPS 文档 → 另存为 / 导出 PDF；或 SDK 编程生成 DOCX → 转 PDF |
| **PDF 输出风格** | **Word 风格**（WPS 原生渲染） |
| **公式/表格/图表** | 公式中等，表格强（ET 引擎），图表强 |
| **特色能力** | 支持 PDF/A-2b 合规导出、数字签名、水印叠加、200+ 格式组合转换 |
| **新产品** | 2026 年发布独立 AI 原生桌面应用"灵犀专业版"（¥50-500/月） |
| **开源/API** | 闭源；WPS StartKit SDK 免费商用（禁止反向工程 / 二次分发） |
| **定价** | WPS 个人版免费；会员 / 专业版订阅制 |
| **借鉴价值** | ⭐⭐（2/5）— 商业闭源，但 Java SDK 的"文档对象模型 + 服务端 PDF 转换"架构思路可参考 |

### 1.4 飞书 AI / Lark

| 维度 | 详情 |
|---|---|
| **技术栈** | Aily 智能伙伴 + 妙搭 Agent 平台 + 多维表格 AI |
| **文档生成流程** | 云端文档协同编辑；第三方开源工具 feishu-docx 支持 Markdown 双向转换 + PDF 导出 |
| **PDF 输出风格** | 现代云文档风格（feishu-docx 支持自定义 PDF 模板、封面 logo、代码高亮主题） |
| **公式/表格/图表** | 公式弱（块级 KaTeX），表格强（多维表格），图表中等 |
| **开源生态** | **feishu-docx**（GitHub 243 stars，Python，MIT）：AI Agent 友好型飞书文档导出 / 写入工具，支持 Claude Skills |
| **重大事件** | 2026-07-30 飞书产品团队并入豆包，成立新豆包产品团队；商业化 AI 智能体 Aily 售价 10-30 万元，销售不理想 |
| **借鉴价值** | ⭐⭐⭐（3/5）— feishu-docx 的"云端文档 ↔ Markdown"双向桥接思路对 AI Agent 集成有借鉴意义 |

### 1.5 钉钉 AI 助理 / 千问办公

| 维度 | 详情 |
|---|---|
| **技术栈** | 通义千问 Qwen-VL-Max（视觉理解）+ 长文本（单次 500 页） |
| **文档生成流程** | 2026-08-03 千问办公正式公测：整合 QoderWork、MuleRun、悟空三款产品 |
| **PDF 输出风格** | Office 多形态产物一站式生成（Word/Excel/PPT/独立网页） |
| **特色** | 打通 25 项钉钉企业 IM 原生能力（群聊、审批、会议、待办）；开放式技能市场 + 行业专属套件 |
| **公式/表格/图表** | 公式弱，表格强，图表中等 |
| **开源/API** | 闭源；钉钉开放平台 API |
| **借鉴价值** | ⭐⭐（2/5）— IM 协同 + AI 生成闭环是企业级方向，与 harryopo 学术定位差异大 |

### 1.6 腾讯文档 AI / WorkBuddy

| 维度 | 详情 |
|---|---|
| **技术栈** | 腾讯文档 Skill + WorkBuddy + 混元 Hy3 模型（MoE 架构，2950 亿参数，激活 210 亿，256K 上下文） |
| **文档生成流程** | 2026-07-30 WorkBuddy V5.3.5 发布"人机双写"协同编辑：在 Word/Excel/PPT 里人和 AI 实时协作 |
| **PDF 输出风格** | 网页端导出 Word/Excel/PDF；手机 App 导出 PDF/图片；元宝支持直接生成 PPT/Word/Excel/PDF/HTML |
| **公式/表格/图表** | 公式弱，表格强（智能表格函数公式匹配），图表强（数据可视化一键生成） |
| **开放性** | 腾讯文档开放平台支持个人开发者注册接入 OpenAPI（无需企业资质） |
| **市场地位** | 2026-06 WorkBuddy 月访问量 2097 万，国内 17 款主流桌面 AI 办公智能体排名第一 |
| **借鉴价值** | ⭐⭐⭐（3/5）— "人机双写"在原文上协作的思路值得关注；开放 API 友好 |

### 大厂办公 Agent 小结

| 厂商 | 路线 | PDF 风格 | 公式 | 借鉴价值 |
|---|---|---|---|---|
| 微软 Copilot | Word + Python | Word 风格 | 弱 | ⭐⭐ |
| Google Gemini | 多格式（含 LaTeX） | 自定义 | 弱 | ⭐⭐⭐ |
| WPS AI | Word + SDK | Word 风格 | 中 | ⭐⭐ |
| 飞书 AI | 云文档 + Markdown 桥接 | 现代云文档 | 弱 | ⭐⭐⭐ |
| 钉钉 / 千问办公 | Office 全家桶 | Office 风格 | 弱 | ⭐⭐ |
| 腾讯文档 AI | 协同编辑 + 多格式 | Office 风格 | 弱 | ⭐⭐⭐ |

**统一结论**：大厂办公 Agent 几乎全部走 Word/Office 路线，**没有一个把数学公式排版作为核心能力**，公式支持普遍较弱。这恰恰是 harryopo LaTeX 路线的差异化空间。

---

## 二、AI 写作 / 文档生成工具

### 2.1 Notion AI

| 维度 | 详情 |
|---|---|
| **技术栈** | 2026-07-01 Notion 3.6：AI Agents 使用沙箱 Linux 计算机（Anthropic 托管）写代码生成文件 |
| **PDF 生成流程** | Agent 写代码 → 构建 HTML + CSS → 服务端渲染 PDF；或 Pandoc + LaTeX（xelatex）管道 |
| **原生导出** | PDF（商业版 / 企业版才支持子页面）、HTML、Markdown & CSV |
| **PDF 输出风格** | 原生导出布局常崩（动态网页转静态 PDF 的固有问题）；Agent 生成质量高 |
| **公式/表格/图表** | 公式弱（块级 KaTeX，导出丢失），数据库导出为 CSV 丢失视图和关系 |
| **痛点** | Notion 是协作工具不是文档处理器；列布局塌缩、图片链接 1 小时过期、Toggle 折叠 |
| **开源/API** | 闭源；Notion API（商业） |
| **定价** | 免费（单页 PDF）；Business 版才支持子页面 PDF 导出 |
| **借鉴价值** | ⭐⭐⭐⭐（4/5）— **"沙箱 Linux + Anthropic 托管 + 写代码生成 PDF"的架构是 AI 文档生成的事实最佳实践**，与 harryopo 的 Skill 编译流程高度契合 |

### 2.2 Typst（LaTeX 挑战者）

| 维度 | 详情 |
|---|---|
| **定位** | 2023 年创建，LaTeX 数十年来最严肃的挑战者 |
| **编译速度** | 大型论文：LaTeX 90 秒 vs **Typst 15 秒**；内容修改 **<1 秒**（实时预览） |
| **语法** | Markdown 般简洁：`*bold*` 替代 `\textbf{}`，`<=` 自动变 ≤，`1/x` 自动分数，括号自动缩放 |
| **错误信息** | 清晰可操作，直接指向行号（对比 LaTeX 的级联错误） |
| **中文支持** | 原生支持系统字体，无需额外配置（对比 LaTeX 需 xeCJK/ctex） |
| **公式** | 优秀（自动分数、符号快捷输入），但生态不及 LaTeX |
| **生态** | 100+ 包（对比 LaTeX 数千包）；期刊会议多数仍要求 .tex 源文件 |
| **典型平台** | TypeTeX（Google Docs 般界面 + AI 助手 + Typst-first + LaTeX 兼容）；typst.app 官方在线编辑器 |
| **开源** | 开源免费（MIT） |
| **借鉴价值** | ⭐⭐⭐⭐⭐（5/5）— **直接对标 harryopo 的技术选型**；Typst 的"编译速度 + 错误信息 + 中文原生"是 LaTeX 的痛点解决方案，值得评估是否作为 harryopo 的并行路线 |

### 2.3 Quarto（科学出版系统）

| 维度 | 详情 |
|---|---|
| **定位** | 基于 Markdown 的现代科学出版系统，支持 LaTeX 和 Typst 双引擎 |
| **2026-07-31 Quarto 1.9** | 新增：llms.txt 输出（AI 友好）、PDF/A、PDF/UA 可访问性、Typst 书籍项目、定理样式（simple/fancy/clouds/rainbow） |
| **AI 集成** | 支持 Roo Code / VS Code 扩展 + LLM API（OpenRouter/OpenAI/Anthropic）做"科学写作助手" |
| **开源** | 开源免费 |
| **借鉴价值** | ⭐⭐⭐⭐（4/5）— Markdown → LaTeX/Typst 双引擎的架构是 harryopo 可借鉴的中间层方案 |

### 2.4 其他工具

| 工具 | 路线 | 借鉴价值 |
|---|---|---|
| **Craft** | 原生 macOS 文档工具，PDF 导出精美 | ⭐⭐ |
| **Rxiv-Maker** | Markdown → LaTeX → PDF（Python CLI，自动图表 / BibTeX） | ⭐⭐⭐⭐ |
| **autodocs-ai** | 一个 prompt → PDF/DOCX/HTML/MD（开源 AI 文档生成器，8 套模板） | ⭐⭐⭐⭐ |
| **TypeTeX** | Typst-first + LaTeX 兼容 + AI 助手 + Google Docs 般界面 | ⭐⭐⭐⭐⭐ |

---

## 三、数学建模竞赛 Agent（重点）

这是与 harryopo 定位最接近的赛道。以下是 2025-2026 年活跃的开源项目深度分析。

### 3.1 主流项目对比

| 项目 | Stars | 路线 | 模板数 | 最近更新 | 借鉴价值 |
|---|---|---|---|---|---|
| **MathModelAgent** (jihe520) | 高 | **Typst**（已从 LaTeX 迁移） | 17 套 | 活跃 | ⭐⭐⭐⭐⭐ |
| **math-modeling-skill** (XiaoMaColtAI) | 590 | **DOCX** 论文生成 | - | 2026-08-03 | ⭐⭐⭐ |
| **mathmodel-skill** (handsomeZR-netizen) | 176 | LaTeX | - | 2026-07-22 | ⭐⭐⭐⭐ |
| **math-modeling-skills** (Lupynow) | 171 | LaTeX | - | 2026-07-31 | ⭐⭐⭐⭐ |
| **ModelingPaperKit** (bosprimigenious) | - | **XeLaTeX** | 4 套赛事 | 2026-07-19 | ⭐⭐⭐⭐⭐ |
| **AutoMCM-Pro** (RealSeaberry) | - | LaTeX（3 个 Skills） | - | 2026-05-03 | ⭐⭐⭐⭐ |
| **math-modeling-single** (Yoki-cmd) | - | **LaTeX-only**（xelatex） | 国赛标准 | 2026-07-21 | ⭐⭐⭐⭐⭐ |

### 3.2 MathModelAgent（jihe520）— 标杆案例深度剖析

这是最早、最知名的数学建模 Agent，其演进路径对 harryopo 极具参考价值。

| 维度 | 详情 |
|---|---|
| **愿景** | "3 天比赛时间变为 1 小时，自动完成获奖级建模论文" |
| **技术架构** | FastAPI 后端 + Vue 3 前端 + WebSocket 实时反馈 + litellm（任意模型）+ Jupyter/E2B 代码执行 |
| **多 Agent** | 建模手（问题拆解）+ 代码手（编程纠错）+ 论文手（格式编排） |
| **关键演进** | **2025 年用 LaTeX，2026 年全面转向 Typst**（内置 17 套中英文赛事模板） |
| **SKILLS 驱动** | 项目蒸馏为纯 SKILLS 层，在 Claude Code / Codex 中通过 `/1start-mathmodel` 一键启动 |
| **9 步自动验收** | 文本泄漏检测 → 数值一致性校验 → **Typst 编译** → PDF 可视化检查 |
| **四层容错** | 有限重试 → Fallback Hand Off → Evaluator Shadow Mode → Feedback Rerun |
| **HIL 人机协作** | 6 种决策动作（confirm / edit / regenerate / ask / skip / abort） |
| **开源状态** | 开源免费，接入任意模型；在线版 mathmodel.top |
| **作者洞察** | "两年前自己实现 Agent 框架，现在和未来更多基于 Harness（Codex/Claude Code）+ SKILLS 构建" |

### 3.3 ModelingPaperKit（bosprimigenious）— XeLaTeX 排版工具包

| 维度 | 详情 |
|---|---|
| **定位** | 数学建模论文排版工具包：**核心引擎 + 多赛事插件**（Core + Plugins） |
| **架构** | 一套 `core/`，四套赛事模板；公共排版进引擎，赛规差异进 `templates/` |
| **技术栈** | **XeLaTeX**（与 harryopo 完全一致） |
| **特色** | CUMCM 工作流 Skills、cleveref 修复、页序预检、五套模板预览 PDF |
| **借鉴价值** | ⭐⭐⭐⭐⭐ — **架构思路与 harryopo 的"base.sty 共享 + 多 .cls"高度同构** |

### 3.4 数学建模 Agent 技术栈统计

基于 GitHub 检索的 20+ 个活跃项目：

| 技术路线 | 占比 | 典型项目 |
|---|---|---|
| **LaTeX / XeLaTeX** | ~60% | ModelingPaperKit、mathmodel-skill、AutoMCM-Pro、math-modeling-single |
| **Typst** | ~30%（快速上升） | MathModelAgent（已迁移）、部分新项目 |
| **DOCX（Word）** | ~10% | math-modeling-skill（XiaoMaColtAI） |

### 3.5 数学建模 Agent 的通用架构模式

```
赛题输入
   ↓
[问题分析 Agent] ── 题意解析、假设建立、模型选择
   ↓
[建模 Agent] ── AHP/TOPSIS/ARIMA/GA 等模型库
   ↓
[代码 Agent] ── Python/MATLAB 执行（Jupyter/E2B 沙箱）
   ↓
[论文 Agent] ── LaTeX/Typst 模板填充 + 编译
   ↓
[验收 Agent] ── 文本泄漏 / 数值一致性 / 编译 / PDF 可视化
   ↓
PDF 论文输出
```

**公式处理**：100% 走 LaTeX/Typst 原生公式（`$...$` 或 `\[...\]`），无 Word Equation 替代方案。
**表格处理**：LaTeX booktabs / Typst table，部分支持 Excel 数据导入。
**流程图处理**：TikZ / Typst drawing / matplotlib + 插图。

---

## 四、AI Agent 框架的文档能力

### 4.1 ChatGPT Canvas / Writing Blocks

| 维度 | 详情 |
|---|---|
| **Canvas 状态** | **2026-05-28 已被 writing blocks 替代**（不再支持 GPT-5.5 默认模型） |
| **Writing Blocks** | 全屏写作块，支持论文、PRD、报告、博客；可保存到 Library；支持目录、下载、撤销重做 |
| **导出格式** | PDF、Markdown、Word(.docx)、代码文件 |
| **PDF 生成** | 通过 Data Analysis（Code Interpreter）运行 Python 生成**真正的 PDF 文件**（非聊天文本） |
| **特色** | Python 浏览器执行、React/HTML 沙箱渲染、版本历史 Diff 视图 |
| **定价** | 免费（Canvas 全功能）；Plus $20/月 |
| **借鉴价值** | ⭐⭐⭐（3/5）— "writing blocks 替代 Canvas"的产品演进值得注意 |

### 4.2 Claude Artifacts

| 维度 | 详情 |
|---|---|
| **Artifacts** | 右侧专用面板显示文档 / 代码，可预览、下载、迭代 |
| **支持格式** | HTML、CSV、SVG、Markdown、文本、代码；**Pro/Max/Team/Enterprise 可直接生成 .docx/.pptx/.xlsx/PDF**（需"代码执行与文件创建"） |
| **LaTeX 工作流** | 上传手写笔记照片 → Claude 生成完整 LaTeX 文档（amsmath + tcolorbox + tikz）→ Extended Thinking 编译 PDF |
| **官方推荐** | 使用 tcolorbox 做彩色定理框；prompt "design like a premium calculus textbook from a major publisher" |
| **导出限制** | 无内置"导出 PDF"按钮（用浏览器打印或第三方扩展） |
| **借鉴价值** | ⭐⭐⭐⭐⭐（5/5）— **Claude 官方力推的 LaTeX + tcolorbox + tikz 学术文档工作流，与 harryopo 技术栈完全契合**；Projects 功能保持跨章节一致性 |

### 4.3 LangChain / CrewAI / AutoGen

| 框架 | 定位 | 文档处理能力 | 借鉴价值 |
|---|---|---|---|
| **LangChain** | 最成熟灵活的编排框架（"AI 框架的 React"） | Document 抽象（page_content + metadata）+ 加载器（PyPDFLoader 等）+ 分块 + 向量库（RAG） | ⭐⭐⭐ |
| **CrewAI** | 基于 LangChain，角色驱动（role/goal/backstory），快速原型 | 集成 LangChain 工具，适合"研究员→撰稿人→编辑"流水线 | ⭐⭐⭐⭐ |
| **AutoGen** | 微软企业级，复杂多 Agent 协调 | 强在模型生命周期管理，文档处理依赖集成 | ⭐⭐ |

**关键洞察**：这些框架是构建 Agent 的基础设施，**本身不直接生成 PDF**。它们的文档能力集中在 RAG（检索增强生成），即"读文档"而非"写文档"。"写文档"需要外接 LaTeX/Typst/Pandoc 等排版引擎。

---

## 五、技术栈对比总表

| 方案 | 文档处理方式 | PDF 风格 | 公式支持 | 表格支持 | 开源/商业 | 适用场景 | 中文支持 | 借鉴价值 |
|---|---|---|---|---|---|---|---|---|
| **微软 Copilot** | Python + Office DOM | Word 风格 | 弱 | 强 | 商业 | 企业办公 | 好 | ⭐⭐ |
| **Google Gemini** | 服务器端多格式生成 | 自定义 | 弱 | 强 | 商业 | 通用 + 学术 | 好 | ⭐⭐⭐ |
| **WPS AI** | KOffice Engine + SDK | Word 风格 | 中 | 强 | 商业 | 国产办公 | 优秀 | ⭐⭐ |
| **飞书 AI** | 云文档 + Markdown 桥接 | 现代云文档 | 弱 | 强 | 部分开源 | 协同办公 | 优秀 | ⭐⭐⭐ |
| **钉钉 / 千问办公** | IM 协同 + Office 生成 | Office 风格 | 弱 | 强 | 商业 | 企业协同 | 优秀 | ⭐⭐ |
| **腾讯文档 AI** | 协同编辑 + 多格式 | Office 风格 | 弱 | 强 | 商业（API 开放） | 协同办公 | 优秀 | ⭐⭐⭐ |
| **Notion AI** | 沙箱 Linux + 写代码 | Agent 高质量 / 原生差 | 弱 | 中 | 商业 | 知识管理 | 中 | ⭐⭐⭐⭐ |
| **Typst** | 现代标记语言 | **学术排版** | **优秀** | 优秀 | **开源** | 学术 / 技术 | **原生** | ⭐⭐⭐⭐⭐ |
| **Quarto** | Markdown + 双引擎 | 学术排版 | 优秀 | 优秀 | **开源** | 科学出版 | 好 | ⭐⭐⭐⭐ |
| **Rxiv-Marker** | Markdown → LaTeX → PDF | 学术排版 | 优秀 | 优秀 | **开源** | 预印本 | 好 | ⭐⭐⭐⭐ |
| **MathModelAgent** | SKILLS + Typst | **竞赛论文** | **优秀** | 优秀 | **开源** | 数学建模 | 优秀 | ⭐⭐⭐⭐⭐ |
| **ModelingPaperKit** | XeLaTeX + 核心引擎 | **竞赛论文** | **优秀** | 优秀 | **开源** | 数学建模 | 优秀 | ⭐⭐⭐⭐⭐ |
| **ChatGPT Canvas** | Writing Blocks + Python | 自定义 | 中 | 中 | 商业 | 通用写作 | 好 | ⭐⭐⭐ |
| **Claude Artifacts** | LaTeX + tcolorbox + tikz | **学术排版** | **优秀** | 优秀 | 商业 | 学术 / 教育 | 好 | ⭐⭐⭐⭐⭐ |
| **LangChain/CrewAI** | RAG 框架（读非写） | N/A | N/A | N/A | 开源 | Agent 基础设施 | N/A | ⭐⭐⭐ |

---

## 六、对 harryopo 项目的借鉴价值评估

### 6.1 核心结论

harryopo 走 **XeLaTeX + ctex + 共享 base.sty + 多 .cls** 的技术路线，与业界学术 / 竞赛 Agent 的主流选型**高度一致**。具体对照：

| harryopo 设计 | 业界对照 | 评估 |
|---|---|---|
| XeLaTeX 编译 | MathModelAgent 曾用 LaTeX，ModelingPaperKit/Yoki-cmd 等仍用 XeLaTeX | ✅ 学术主流 |
| ctexart/ctexbook 基础 | 数学建模 Agent 中文模板普遍用 ctex | ✅ 中文最佳实践 |
| 共享 base.sty + 多 .cls | ModelingPaperKit 的"core 引擎 + 多赛事 templates"架构同构 | ✅ 业界验证 |
| 主题中继机制（`\ifdefined\harryopo@theme`） | 未见完全相同实现，但 Quarto 的 brand.yml 思路类似 | ✅ 创新且合理 |
| build.ps1 + TEXINPUTS | MathModelAgent 的 9 步验收、AutoMCM-Pro 的 quality_gate.py 更完善 | ⚠️ 可借鉴增强 |

### 6.2 关键借鉴点（按优先级）

#### P0 — 必须关注

1. **MathModelAgent 从 LaTeX 迁移到 Typst 的趋势**：这是 2026 年最重要的技术信号。建议 harryopo 在巩固 LaTeX 体系的同时，**评估 Typst 作为并行输出的可行性**（Typst 编译速度 15 秒 vs LaTeX 90 秒，中文原生支持）。

2. **Claude Artifacts 官方推荐 tcolorbox + tikz 学术工作流**：与 harryopo 的 tcolorbox 边框体系完全契合，可作为 harryopo 面向 Claude 用户的官方推介话术。

3. **ModelingPaperKit 的"core 引擎 + 多赛事插件"架构**：与 harryopo 的"base.sty + 多 .cls"同构，可作为架构参照和潜在合作对象。

#### P1 — 值得借鉴

4. **MathModelAgent 的 SKILLS 驱动模式**：项目蒸馏为纯 SKILLS 层，在 Claude Code / Codex 中一键启动。harryopo 可考虑提供官方 SKILL.md，让 AI Agent 直接调用 harryopo 模板编译论文。

5. **MathModelAgent 的 9 步自动验收**：文本泄漏检测 → 数值一致性 → 编译 → PDF 可视化检查。harryopo 的 build.ps1 可增强为类似的预检流水线。

6. **Notion 的"沙箱 Linux + 写代码生成 PDF"架构**：这是 AI 文档生成的事实最佳实践。harryopo 作为 Skill 被 AI Agent 调用时，本质上就是这个架构的本地化版本。

7. **Quarto 的双引擎（LaTeX + Typst）+ llms.txt 输出**：harryopo 可考虑输出 AI 友好的结构化元数据，让 AI Agent 更容易理解模板能力。

#### P2 — 可选增强

8. **autodocs-ai 的"一个 prompt → 多格式"思路**：harryopo 可提供 prompt 模板库，引导 AI Agent 正确使用 harryopo 模板。

9. **feishu-docx 的"云端文档 ↔ Markdown"双向桥接**：若 harryopo 需要接入云端协同场景，可参考此模式。

10. **AutoMCM-Pro 的 quality_gate.py / security_check.py**：硬性门禁脚本，harryopo 的编译流程可引入类似的质量门禁。

### 6.3 差异化定位建议

基于调研，harryopo 的差异化定位应聚焦：

1. **学术 / 技术文档赛道**：避开大厂办公 Agent 的 Word 红海，聚焦 LaTeX/Typst 学术排版。
2. **中文优化**：ctex + 方正字体 + XITS 数学的中文组合是国产大厂未覆盖的细分。
3. **AI Agent 友好**：提供 SKILL.md、llms.txt、prompt 模板，让 AI Agent（Claude/Codex）能直接调用。
4. **主题中继机制**：`\ifdefined\harryopo@theme` 是独特创新，可作为卖点。
5. **Typst 并行评估**：作为 LaTeX 体系的有益补充，而非替代。

---

## 附录 A：关键开源项目清单（2025-2026 活跃）

| 项目 | GitHub | 路线 | Stars | 用途 |
|---|---|---|---|---|
| MathModelAgent | jihe520/MathModelAgent | Typst | 高 | 数学建模全流程 Agent |
| math-modeling-skill | XiaoMaColtAI/math-modeling-skill | DOCX | 590 | CUMCM/MCM/ICM 三阶段 |
| mathmodel-skill | handsomeZR-netizen/mathmodel-skill | LaTeX | 176 | 三竞赛 + 10 阶段 |
| math-modeling-skills | Lupynow/math-modeling-skills | LaTeX | 171 | 完整工具链 |
| ModelingPaperKit | bosprimigenious/ModelingPaperKit | XeLaTeX | - | 核心引擎 + 多赛事 |
| AutoMCM-Pro | RealSeaberry/AutoMCM-Pro | LaTeX | - | 三 Skills 零到论文 |
| math-modeling-single | Yoki-cmd/math-modeling-single | XeLaTeX | - | LaTeX-only 国赛标准 |
| feishu-docx | leemysw/feishu-docx | Markdown | 243 | 飞书文档 ↔ Markdown |
| autodocs-ai | makieali/autodocs-ai | 多格式 | - | Prompt → PDF/DOCX |
| rxiv-maker | PyPI | Markdown→LaTeX | - | 预印本自动生成 |

## 附录 B：调研方法与数据来源

- **agent-reach**：13 平台路由器，体检 GitHub（完整可用）、Web（Jina Reader）、B站搜索等通道
- **WebSearch**：覆盖中英文关键词，聚焦 2025-2026 年产品
- **GitHub gh CLI**：`gh search repos "数学建模 论文" --sort stars` 等多组检索
- **数据时效**：截至 2026-08-05，涵盖 2026 年 7-8 月最新动态（飞书并入豆包、千问办公公测、WorkBuddy 人机双写等）

---

*本报告由 harryopo 项目调研任务生成，归档于 `d:\ai\latex\docs\`。*
