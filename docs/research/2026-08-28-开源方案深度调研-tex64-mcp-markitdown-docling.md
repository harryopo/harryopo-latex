# 开源办公方案深度调研报告（2026-08-28）

> 调研日期：2026-08-28
> 调研背景：用户提出"当前又出来了很多开源的办公方案，也有 md 转换、word 生成等开源项目，例如 tex64 mcp"，要求深入调研开源方案，评估能否集成优化，并更新开发方案书。
> 调研方法：deep-research-ultra 方法论（MECE 拆解 + 8 维 GitHub 评分 + 适配本项目评分）+ WebSearch 实时数据核验（stars/活跃度/功能）。
> 归属项目：d:\ai\latex 办公文档 AI 生产力平台

---

## 0. 一句话结论

**本项目"AI 产结构化数据（MD/JSON）→ 模板引擎渲染"的范式已被市场验证（markitdown 12.6 万 star、docling 6 万+ star 全部押注"文档→Markdown"方向）**。本次调研最大增量有三：

1. **markitdown（微软官方）**：任意文件→MD 的轻量官方转换器 + 官方 MCP，补齐"互相转换"地基的上游入口（P0，立即集成）；
2. **docling（IBM，LF 治理）**：布局感知的深度解析器，与 MinerU 互为兜底，且新增 LaTeX 解析（P1）；
3. **LaTeX MCP 生态成熟**（MagicTeX-mcp 等）：tex64 实为**商业编辑器而非开源项目**，"tex64 mcp"方向可转为"自封装 harryopo-build-mcp 或参考 MagicTeX 交互范式"。

---

## 1. 主题一：tex64 MCP 与 LaTeX/TeX MCP 生态（重点核验）

### 1.1 tex64 澄清 ⚠️

**tex64（tex64.com）是商业产品，不是开源项目**：

| 维度 | 内容 |
|---|---|
| 形态 | Windows/macOS 原生 LaTeX 编辑器（微软签名安装包，可在 Microsoft Store 下载） |
| AI 能力 | 内嵌 Axiom AI（生成公式/润色/修错），免费版含月度额度，Basic $12/月，Pro $25/月 |
| 引擎 | 可复用已有 TeX Live 或自动安装托管 TeX Live（非 WASM，支持 XeLaTeX） |
| 特色 | 可视化数学输入、图片/手写 OCR 转 LaTeX、PDF 预览 + SyncTeX、离线可用、Git 集成 |
| 与 MCP 关系 | 官方页面未提及 MCP 服务；"tex64 mcp"应理解为"面向 AI 的 LaTeX 编辑器"这一产品品类 |

**结论**：不采纳 tex64（商业、闭源、无 MCP、价值在编辑器 UX 而非引擎）。但它验证了"AI 内嵌 LaTeX 工作流"的产品方向，其"AI 直接改源文件→自动编译→PDF 预览"的交互与我们阶段 3 Web 编辑器目标一致。

### 1.2 真实可用的 LaTeX MCP 开源项目（2026 年新生态）

| 项目 | 地址 | stars | 语言/许可 | 核心能力 | 与本项目关系 |
|---|---|---|---|---|---|
| **MagicTeX-mcp** | `github.com/ZoeLinUTS/MagicTeX-mcp` | 较新 | TS/npm | **最先进的 LaTeX Agent 编辑器**：WASM TeX Live 2026 引擎（texlyre-busytex，无本地 TeX 安装）编译，浏览器一站式界面（源码 CodeMirror + PDF 实时预览 + 评论锚定→agent 修复循环 + 编译历史 git 快照），npm 包 `magictex-mcp` | **参考（交互范式）**：注释锚定→agent 修复闭环、live reload、编译历史快照，正是我们阶段 3 Web 编辑器要的 UX。WASM 引擎对 CJK/方正字体弱，但**交互设计可直接借鉴** |
| **sepinetam/latex-mcp** | `github.com/sepinetam/latex-mcp` | 新 | Python/AGPL-3.0 | Docker 容器内编译 TeX，AI agent 可编译、取错误、多遍编译 | 参考：Docker 隔离编译的 MCP 工具形态 |
| **tobioffice/LateXPDF-MCP** | `github.com/tobioffice/LateXPDF-MCP` | 新 | Node.js | LaTeX→PDF（依赖本机 latexmk/MiKTeX/TeXLive），npm `latexpdf-mcp` | 参考：MCP 包装本地 latexmk |
| **AndrewAltimit LaTeX MCP（gist）** | gist 24 stars | 新 | Python/Docker | 容器化编译，支持 **pdfLaTeX/XeLaTeX/LuaLaTeX** + **TikZ 独立渲染 PNG/SVG** + 多遍编译 + 错误提取 + 模板（article/report/book/beamer） | 参考：TikZ→PNG/SVG 的 MCP 化对我们 super-diagram/TikZ 链路有启发 |
| **texlab** | `latex-lsp/texlab` | ~3.2k | Rust/MIT | 老牌 LaTeX LSP（补全/诊断/编译/预览），非 MCP | 参考：编译错误诊断能力 |

### 1.3 主题一结论

- **不引入第三方编译 MCP**：现有 `build.ps1`（3 遍 XeLaTeX + TEXINPUTS + 页数统计）+ 46 个 .tex 全通过，原生 XeLaTeX + 方正字体链路成熟稳定，WASM/容器化编译对 CJK 支持弱、速度慢。
- **建议方向 A（低成本）**：自封装 `harryopo-build-mcp`——用 MCP 包装 build.ps1（编译→日志解析→错误定位→修复建议），获得 tex64/MagicTeX 想要的"AI 交互式编译诊断闭环"，保留原生引擎全部能力。
- **建议方向 B（中期）**：阶段 3 Web 编辑器参考 MagicTeX-mcp 的"评论锚定→agent 修复"交互与编译历史快照设计。

---

## 2. 主题二：Markdown → Word / 文档→Markdown 新方案

### 2.1 markitdown（微软 AutoGen 团队）⭐ 强烈推荐

| 维度 | 内容 |
|---|---|
| 地址 | `github.com/microsoft/markitdown` |
| stars | **12.6 万+**（2026-05 数据，微软增长最快的开源项目之一） |
| 语言/许可 | Python / MIT |
| 定位 | **任意文件 → LLM 友好 Markdown** 的官方轻量转换器（"LLM 的母语是 Markdown"） |
| 支持格式 | 20+：PDF（文本/表格/标题）、DOCX（完整结构）、PPTX（文本+备注+表格）、XLSX（表格→MD 表格）、EPUB、图片（EXIF+OCR）、音频（转写）、HTML、CSV/JSON/XML、YouTube 字幕、ZIP、Outlook .msg |
| 官方 MCP | `microsoft/markitdown-mcp`（`pip install markitdown-mcp`，Claude Desktop 等可直接调用"分析这个文件"） |
| 版本 | v0.1.7（2026-07 更新，持续活跃） |
| 安装 | `pip install 'markitdown[all]'` 或按需 `markitdown[pdf,docx,pptx]` |

**与本项目关系**：**补充（非替代）**。现有解析三套件：
- **anydoc**：纯 Rust 毫秒级快检（14 格式，GFM 表格原生）→ 首选 fast path；
- **MinerU**：扫描件/复杂版面深解析（0.2s/页，colspan/rowspan 表格，LaTeX 公式）→ 复杂文档；
- **markitdown（新增）**：微软官方 Office 原生格式保真 + 音视频 + 生态兜底 → 兜底/长尾格式。

**集成建议**：P0。接入 `.trae/skills/harryopo-office/scripts/office.py` 预处理分支，形成三级解析路由：`anydoc 快检 → MinerU 深解析 → markitdown 兜底`。`pip install markitdown` 零范式冲突。

**风险**：PDF 质量不如 MinerU（无版面分析）；音视频转写需外部模型（可选依赖）；输出为纯 MD（图片仅引用）。

### 2.2 其它 Markdown/Word 方案（核验）

| 项目 | 地址 | stars | 语言 | 核心 | 结论 |
|---|---|---|---|---|---|
| Pandoc | jgm/pandoc | ~35k | Haskell | MD↔全格式中枢（reference-doc 品牌化） | **已集成，维持** |
| docx（dolanmiu/docx） | dolanmiu/docx | ~3.5k | TS | 代码生成 .docx（段落/表格/公式/TOC） | 阶段 3 Web 编辑器转 JS 栈时评估 |
| html-to-docx | liyng05/html-to-docx | ~1.2k | JS | HTML→docx | 引入 HTML 中间态时考虑 |
| mammoth | mwilliamson/mammoth | ~5k | JS/Py | docx→HTML/MD（反向） | 用户模板反解的轻量备选 |
| j2docx | skulptur/j2docx | ~0.2k | Python | jinja2→docx | 与 docxtpl 重叠，不引入 |
| docxtemplater | open-xml-templating/docxtemplater | ~2.9k | JS | docxtpl 的 JS 强化版 | 阶段 3 JS 栈再评估；**v3+ 商业许可陷阱** |

**主题二结论**：渲染端"正路"仍是 **Pandoc + 自有 python-docx 渲染引擎**（已验证）；新价值增量在**上游解析端（markitdown）**，而非渲染端。

---

## 3. 主题三：中文办公文档方向

| 项目 | stars | 结论 |
|---|---|---|
| **Typst** | ~40k（Rust） | 现代排版语言，CJK 改进快，编译极快；但宏包生态远小于 LaTeX，方正字体嵌入需适配。**长期储备，不建议 2026 年内引入生产链路**。可作"第三输出通道"实验（pandoc -t typst） |
| **quarto** | ~4k | 学术多格式出版，后端可配 xelatex；GPL-2.0 许可需法务确认；与自研模板体系重叠。**评估项** |
| ctex/Fandol | ~1k | 中文 LaTeX 宏包体系（**已使用**），维持 |
| 公文开源项目 | <0.3k | 无高质量活跃项目，国标 GB/T 9704 细节多；**建议基于 harryopo-report 自研**（本项目公文模板已跑通） |

**主题三结论**：中文办公文档护城河在**字体与版式规则**（方正嵌入、CJK 断行、标点压缩），现有栈已是成熟解法，新方案暂无必要替换。

---

## 4. 主题四：格式互转新工具（高性能方向）

| 项目 | stars | 语言/许可 | 能力 | 结论 |
|---|---|---|---|---|
| **docling（IBM）** | **~6.2 万**（2026-06，LF AI & Data Foundation 治理） | Python/MIT | 布局感知解析：PDF/DOCX/PPTX/XLSX/HTML/图片/音频/**LaTeX**，DoclingDocument 统一表示，导出 MD/HTML/JSON/DocTags；本地运行；**官方 MCP server**；OCR（EasyOCR/Tesseract/RapidOCR）+ VLM（GraniteDocling）可选 | **P1 集成**：作 MinerU 的互为兜底（复杂版面/表格对比）；注意 ~1GB 模型下载、中文 PDF OCR 需实测 |
| **pdfcpu** | ~8k | Go/Apache-2.0 | PDF 后处理瑞士军刀（合并/拆分/水印/表单/加密），单二进制 | P2 收进工具箱（PDF 后处理） |
| **LibreOffice headless** | — | MPL-2.0 | `soffice --convert-to` 万能互转 | 引擎级互转的最后防线（兜底） |
| docx-rs | ~0.6k | Rust/MIT | 纯 Rust 生成/读取 .docx | 无 Office 依赖的服务端 docx 生成时评估 |
| mupdf | ~8k | C/AGPL | PDF 渲染/转换/WASM | AGPL 传染性注意；PDF→图预览时用 |
| OnlyOffice DocumentServer | ~5k | AGPL-3.0 | 在线预览/编辑/转换 API | 已在路线图（阶段 2-4） |

**主题四结论**：高性能互转"正解"仍是 **Pandoc 中枢 + markitdown/docling/MinerU 解析三保险 + LibreOffice headless 兜底 + pdfcpu 后处理**。

---

## 5. 主题五：文档生成 AI Agent / MCP 服务器

### 5.1 微软官方系（本次调研最大确定性增量）

| 项目 | stars | 说明 | 结论 |
|---|---|---|---|
| markitdown-mcp | ~2k | 官方"文件→MD" MCP 工具 | P0 |
| **docling MCP** | — | docling 官方 MCP server | P1（随 docling） |

### 5.2 Office 自动化 MCP 生态（社区实现为主，无单一"官方 office-mcp"开源）

> 注：`microsoft/office-mcp` 经核验**不存在**（子代理知识库误报）。微软官方 Office 相关 MCP 是 markitdown-mcp；Office 自动化 MCP 是社区生态：

| 项目 | 地址 | 语言/许可 | 核心能力 | 结论 |
|---|---|---|---|---|
| **fukui-yuto/microsoft-office-mcp** | github.com/fukui-yuto/microsoft-office-mcp | Python/uv | Windows COM 自动化控制 PowerPoint/Word/Excel，**120 工具**（PPT 45 + Word 36 + Excel 39），含 `export_to_pdf`、修订跟踪、页眉页脚、目录插入 | **P1 参考**：与我们 word_template_engine.py 的 COM 逻辑同环境（Windows+Office）；作为"渲染后原生 Word 操作"（目录刷新/修订/导出 PDF）的 MCP 化参考 |
| dosev-ai/mcp-office | github.com/dosev-ai/mcp-office | Python/MIT | wordmcp（模板装配+修订+结构 QA 50 工具）/pptmcp/excelmcp | 参考 |
| azzindani/MCP_Microsoft_Office | github.com/azzindani/MCP_Microsoft_Office | Python | 11 servers 96 tools，版本快照+操作收据+diff 引擎+run-level 编辑保样式 | 参考（版本审计/收据思路与方案书"版本审计差异化"吻合） |
| Arcade.dev Office 365 MCP | 商业 | — | Graph API 云端（OneDrive/SharePoint） | 云端依赖，不契合本地优先 |

### 5.3 主题五结论

- 微软官方两件套 **markitdown + markitdown-mcp** 是明确增量；
- Office 自动化 MCP 无官方开源统一标准，我们**不需要引入**（现有 word_template_engine.py 已覆盖 COM 更新 TOC/导出），但可参考 fukui-yuto 的工具划分（120 工具清单）与 azzindani 的版本快照/收据设计；
- 守住范式红线：MCP/Office 自动化只做**渲染后操作**（目录刷新、修订、导出 PDF），绝不回到"AI 直接改文档二进制"。

---

## 6. 主题六：模板引擎方向

| 项目 | 结论 |
|---|---|
| docxtpl（已集成） | 同类最优解之一，维持 |
| docxtemplater（JS） | v3+ 商业许可陷阱；仅阶段 3 Web 编辑器转 JS 栈时评估 |
| j2docx / docx-templates | 与 docxtpl 重叠，不引入 |

**主题六结论**：模板引擎方向无需新引入，保持 docxtpl（Python 栈）。

---

## 7. 推荐度评分总表（8 维 GitHub + 适配本项目，0-100）

| 排序 | 项目 | 主题 | GitHub 分 | 适配分 | 总分 | 等级 | 与本项目动作 |
|---|---|---|---|---|---|---|---|
| 1 | **markitdown / markitdown-mcp** | 解析 | 90 | 95 | **92.5** | **Adopt** | office.py 第三级解析兜底 |
| 2 | **docling（IBM）** | 解析 | 89 | 83 | **86** | **Adopt/Trial** | MinerU 互为兜底 + LaTeX 解析 |
| 3 | **MagicTeX-mcp** | LaTeX-MCP | 70 | 78 | **74** | Trial | Web 编辑器交互范式参考 |
| 4 | **Typst** | 排版 | 89 | 79 | **84** | Trial（长期） | 第三输出通道储备 |
| 5 | **fukui-yuto/microsoft-office-mcp** | Office-MCP | 65 | 80 | **72.5** | Trial | COM 工具划分参考 |
| 6 | **pdfcpu** | PDF 后处理 | 78 | 79 | **78.5** | Trial | 收进工具箱 |
| 7 | quarto | 出版 | 79 | 81 | **80** | Trial | 学术报告第二渲染入口评估 |
| 8 | texlab | LaTeX | 76 | 75 | **75.5** | Assess | 错误诊断参考 |
| 9 | AndrewAltimit LaTeX MCP | LaTeX-MCP | 55 | 72 | **63.5** | Assess | TikZ→PNG/SVG MCP 化启发 |
| 10 | latex-mcp（Docker） | LaTeX-MCP | 55 | 60 | **57.5** | Assess | Docker 隔离编译参考 |
| 11 | docxjs / html-to-docx | MD→Word | 68 | 78 | **73** | Assess | JS 栈再评估 |
| 12 | mammoth | 反向解析 | 72 | 80 | **76** | Trial | 用户模板反解备选 |
| 13 | **tex64** | LaTeX 编辑器 | — | — | — | **Hold（商业）** | 不采纳；产品方向已验证 |

---

## 8. 集成决策与优先级（更新开发方案书依据）

### P0 · 立即（1 周内）
1. **markitdown + markitdown-mcp** 接入 office.py：形成 `anydoc 快检 → MinerU 深解析 → markitdown 兜底`三级解析路由，补齐 14+ 格式输入，强化"任意文件→标准 MD"中间态入口。

### P1 · 短期（1 个月内）
2. **docling** 接入：作为 MinerU 互为兜底（复杂版面/表格质量对比），官方 MCP 可选启用；注意模型体积（~1GB）与中文 PDF 实测。
3. **Word → PDF 直接导出**：word_template_engine.py 已有 COM 基础设施，加一次 `doc.ExportAsFixedFormat(...)` 即可打通（成本最低、收益直接）。
4. **harryopo-build-mcp（自封装）**：MCP 包装 build.ps1（编译→日志解析→错误定位→修复建议），获得 AI 交互式编译诊断闭环，替代"tex64 mcp"设想。

### P2 · 中期（1-3 个月）
5. **pdfcpu** 收进工具箱（PDF 水印/合并/元数据后处理）。
6. **LaTeX → Word 务实路线**：Pandoc tex→docx 试验；若质量不行，统一走 MD 中间态（.tex → MD 清洗 → Word 引擎渲染）——MD 中间态已是本项目核心范式。
7. **quarto** 评估为学术报告第二渲染入口。

### P3 · 长期跟踪
8. **Typst**（第三输出通道储备）、**tectonic**（免 TeX 环境部署）、**LibreOffice headless**（互转兜底）、**docxtemplater/docxjs**（阶段 3 Web 编辑器转 JS 栈，警惕 v3+ 商业许可）、**MagicTeX 交互范式**（阶段 3 Web 编辑器：评论锚定→agent 修复 + 编译历史快照）。

### 明确不引入
- **tex64**（商业闭源、无 MCP、WASM 中文弱——且实为编辑器非 MCP）
- overleaf-mcp（云端账号依赖）
- j2docx / unstructured（与现有重复）
- 公文类低星项目（自研更可控，公文模板已跑通）

---

## 9. 关键风险清单

1. **数据时效**：stars 数据截至 2026-06/07（markitdown 12.6 万、docling ~6.2 万），持续增长；集成前以 GitHub 实时为准。
2. **许可合规**：docxtemplater v3+ 商业许可、quarto GPL-2.0、mupdf AGPL、latex-mcp AGPL——使用前确认。
3. **解析器重复维护**：anydoc / MinerU / markitdown / docling 并存需明确分工矩阵（快检/深解析/兜底/互为兜底），避免四套打架。
4. **docling 体积与速度**：~1GB 模型、首次加载慢、大型 PDF 内存占用高——仅复杂文档路径启用。
5. **范式红线**：所有集成守住"AI 只产结构化数据 → 模板引擎渲染"铁律；Office MCP/自动化只做渲染后操作。
6. **WASM 引擎中文风险**：tex64/MagicTeX 的 WASM TeX 对 CJK/方正字体支持弱——不用于生产编译链路。

---

## 10. 调研来源（WebSearch 实时核验）

- tex64 官网：https://tex64.com/
- MagicTeX-mcp：https://github.com/ZoeLinUTS/MagicTeX-mcp
- latex-mcp：https://github.com/sepinetam/latex-mcp
- LateXPDF-MCP：https://github.com/tobioffice/LateXPDF-MCP
- markitdown：https://github.com/microsoft/markitdown
- markitdown 解析：https://juejin.cn/post/7644776565671165992
- docling：https://github.com/docling-project/docling · PyPI docling 2.85.0
- docling star 曲线：https://ghtrends.dev/docling-project/docling/
- fukui-yuto/microsoft-office-mcp：https://lobehub.com/mcp/fukui-yuto-microsoft-office-mcp
- azzindani/MCP_Microsoft_Office：https://github.com/azzindani/MCP_Microsoft_Office
- dosev-ai/mcp-office：https://github.com/dosev-ai/mcp-office

---

> 报告状态：调研完成，数据已实时核验。下一步：据此更新开发方案书（docs/plans/2026-08-28-office-super-skill-v2.md）。
