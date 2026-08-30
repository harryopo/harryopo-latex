
# CLAUDE.md — d:\ai\latex 项目规则

> 本项目定位为**办公文档 AI 生产力平台**，以 harryopo LaTeX 模板体系为核心，扩展覆盖 Word / PDF / PPT / 流程图 全格式办公文档生成。以下规则适用于所有在本项目中工作的 AI Agent。

---

## 📋 项目全景（2026-08-08 更新）

### 1. harryopo LaTeX 模板体系（核心，已完成）

| 文件                    | 状态         | 说明                                        |
| ----------------------- | ------------ | ------------------------------------------- |
| `harryopo-base.sty`   | ✅ v4.2 完成 | 共享基础包：字体配置、数学引擎、中文排版    |
| `harryopo-paper.cls`  | ✅ v4.0 完成 | 论文文档类（ctexart 扩展）                  |
| `harryopo-report.cls` | ✅ v4.0 完成 | 报告文档类（ctexrep 扩展）                  |
| `harryopo-book.cls`   | ⬜ 待开发    | 书籍文档类（计划中）                        |
| `harryopo-notes.cls`  | ⬜ 待开发    | 笔记文档类（plan.md 规划中）                |
| `build.ps1`           | ✅ v4.2 完成 | 编译脚本：环境检查 + 3遍 XeLaTeX + 页数统计 |

**已验证编译通过的示例**（0 失败）：

- `showcase-paper.pdf`（单栏，8页，261KB）
- `example-paper-twocolumn.pdf`（双栏，3页，164KB）
- `showcase-report.pdf`（15页，235KB）
- `example-report.pdf`（14页，242KB）

**独立子项目（不修改架构）**：

- `templates/math-notes/` — 数理笔记系统（harryopo-mathnotes.cls，完整可用）
- `参考资料/中文book/` — kaobook 中文书籍（方正字体+XITS，39页编译通过）

### 2. harryopo-office 办公超级 Skill（已完成）

路径：`.trae/skills/harryopo-office/`（原 `harryopo-latex` 更名升级，Word + LaTeX 双格式）

**Word (.docx) 模板引擎**（`scripts/word/`）：

- `md_to_word.py` — Markdown 中间态 → .docx 主入口（AI 产出 MD → 用户可编辑 → 渲染）
- `word_template_engine.py` — 渲染引擎：方正/开源字体 JSON 配置驱动、Word 原生自动目录（COM 更新 TOC + SaveAs2 兼容 OMML）、OMML 数学公式、表格/图片/注释/参考文献规范排版
- `template/` — **docxtpl 模板填充子 skill**（用户模板 → 保真填充）：`docx_template.py`（extract schema / validate / render）、`schema_extractor.py`（占位符扫描 + jinja2 作用域类型推断）、`template_render.py`（data.json → .docx，含图片 InlineImage）
- `skills/diagram-design/` — **编辑级图表 skill（2026-08-29 内嵌）**：39 类型 × 3 变体（极简亮/暗/全编辑），白纸黑字编辑风（4px 网格 + 6 连接器规则 + 焦点色 ≤2 + 密度 4/10），自检 `self_check.py`；`scripts/diagram_design_render.py`（HTML→PNG，`--svg` 仅截 SVG / `--check` 自检）；`office.py diagram` 子命令（委托透传）。**SKILL.md 已固化"文档生成主流程"**（写文档/文章/报告推荐路径）：①AI 产出 MD 中间态 → ②用户预览确认内容 → ③AI 智能分析是否适合配图（适合则提问并给多类型选择，禁止擅自生成）→ ④diagram-design 生成 HTML→PNG→self_check→用户审核 → ⑤智能插入（图注 `![图N：xxx]` + `> 注：` 注释，图紧跟引用段落）→ ⑥office.py render → Word/LaTeX（可选 --template）
- `configs/` — `fangzheng.json`（本地方正 GBK）+ `opensource.json`（Windows 系统字体，免授权）
- `examples/example.md` — 完整示例
- **Markdown 约定**：`#`主标题 / `##`一、级 / `> 注：`注释 / `> **表N：**`表标题 / `$$...$$`公式 / `![图N：](path)`图片

**LaTeX 转换脚本**：

- `scripts/convert.py` — Markdown → LaTeX 转换引擎
- `scripts/mineru_cli.py` — 两阶段审查：DOCX → 标准 MD（review）→ 含 LaTeX 的 MD（convert）
- `scripts/html_table_to_latex.py` — MinerU HTML 表格 → LaTeX（支持 colspan/rowspan）

**关键特性**：

- 加粗 → 方正黑体映射（`{\fzht 文字}`，非 `\textbf`，避免中文字体笔画糊）
- MinerU DOCX 原生解析（0.2秒/页，纯 CPU）
- HTML 表格 → \multicolumn/\multirow（保留 colspan/rowspan）
- 两阶段审查流程（用户确认后再编译）
- Word 流程：AI 只产出结构化 Markdown，引擎保真渲染（符合办公文档生成铁律）

### 3. 办公超级 Skill 方向（已进入实施）

**方案文档**: `docs/plans/2026-08-08-office-super-skill.md`

**核心范式**: AI 产出结构化数据（JSON/Markdown）→ 模板引擎渲染 → 输出文档（绝不直接生成 OOXML/排版代码）

**4 大需求 → 技术对策**：

| 需求                     | 对策                             |
| ------------------------ | -------------------------------- |
| AI 输出按模板来          | docxtpl（Word）+ 模板引擎（PDF） |
| Word ↔ MD ↔ LaTeX 互转 | Pandoc 为中枢                    |
| 办公文件可视化编辑       | TipTap + Yjs + inline diff       |
| 用户模板入库             | 模板注册表 + 自动 schema 提取    |

**路线图**：

- 阶段 1（立即）：docxtpl 模板填充 + 模板注册表
- 阶段 2（短期）：本地预览服务器（PDF/HTML）
- 阶段 3（中期）：React + TipTap Web 编辑器
- 阶段 4（长期）：模板市场 + 多人协作 + ONLYOFFICE 集成

### 4. 流程图/Skill 图谱体系

**flowchart-generator**（`c:\Users\Administrator\.trae-cn\skills\flowchart-generator/`）

- 自研流程图生成器，借鉴 lhr-fireworks-tech-graph 核心技巧（紧凑路由、token色系、粗箭头）
- **核心改进**：连线正交不歪斜、中文排版适配（PingFang SC/Microsoft YaHei）、布局参数精确计算
- **mono 黑白灰主题（2026-08-29）**：`meta.theme: mono`（亮色白底黑字灰边）或 `mono-dark`（纯黑底白字），全 style 生效；mono 模式**强制忽略 YAML 彩色 colors 覆盖**；色板常量 `MONO_THEME`/`MONO_DARK`（含灰度半透明 fill_front/back/db/cloud/security/bus/external + arrow_main/arrow_fb/card_bg）；渲染处硬编码彩色 rgba 全部改为 `colors.get("fill_*")`，node_box 暗色遮罩色跟随 `colors["bg"]`
- **6 种内置样式**：
  - style13 — Compact Architecture（系统架构图，多层堆叠 + 左侧标注层：USERS/GATEWAY/SERVICES 等语义色条 + 中英双语标注 + 内容区自动避让）
  - style14 — Agent Orchestration（智能体编排，6 步垂直 + 意图/源/工具扇出 + 反馈环）
  - style15 — Pipeline Flow（数据管线，横版 N 步，4 种形状：trigger/process/decision/output）
  - style16 — Data Flow（数据流图，4 类节点 + 正交边路由 + 标签背景）
  - style17 — Skill Workflow（泳道图，4 泳道 + 阶段虚线 + 任务卡自适应宽度）
  - style18 — Sequence Diagram（时序图，token 色系 + 2.4px 箭头 + dominant-baseline 居中）
- **8 个子命令**：generate / improve / validate / export / compare / archive / batch / distill
- **输出**：独立 .py（拷贝即可运行）+ SVG + PNG（playwright）
- **依赖**：Python 3.8+，PyYAML（可选 playwright，pip install playwright && playwright install chromium）

**harryopo-tikz-diagram**（`skills/harryopo-tikz-diagram/`）

- TikZ 代码生成：架构图、流程图、时序图、组织树
- 时序图 v5.1 三阶段紧凑布局（7 参与者，1 页 PDF，0 Overfull）
- 主题系统（blue/green YAML 配置）

**全局 Skill 参考**：

- `diagram-skill` — draw.io XML 生成（交互式，从文字/手绘生成，三阶自审）
- `arch-prompter`（`c:\Users\Administrator\.trae-cn\skills\arch-prompter/`）— 自然语言 → 架构图合同 + YAML，调用 flowchart-generator 渲染
  - 支持 style13（多层架构）、style14（智能体编排）、style15（数据管线）、style16（数据流图）
  - 集成 jieba 中文分词 + 自定义词库（30+ 技术节点），防止复合词被拆分
  - 输出纸框架风格合同 + flowchart-generator YAML，用户确认后渲染

**super-diagram**（`c:\Users\Administrator\.trae-cn\skills\super-diagram/`）— 统一图表生成入口 v2.1

- 自然语言描述 → LLM 计算坐标 → render_v2.py 渲染（架构图 nodes+edges / 时序图 participants+messages）
- 两大类型自动路由：`architecture`（节点+边，正交路由+避障）与 `sequence`（时序图，防字体遮盖布局）
- 防字体遮盖：标签宽度按内容自适应、双行行高 52px/单行 40px、首行消息 `header_h+ph+30` 不遮参与者、时间戳避让
- 双主题：时序图 light（默认白底）/ dark（`#020617` 背景 + 语义色板），由 `canvas.theme` 控制
- 用法：`python scripts/render_v2.py input.json -o out.png --scale 2`（架构/时序通用）
- 示例：`testdata/sequence-agent.json`（LLM Agent 时序图）→ `output/sequence-agent-light/dark.png`
- 兼容旧 v1.0 入口：`scripts/unified.py "自然语言描述" --style 14 --theme dark -y`

---

## ⚠️ 当前状态 (2026-08-09)

**已完成**：

- ✅ harryopo base.sty + paper.cls + report.cls（46 个 .tex 全部编译通过）
- ✅ MinerU DOCX 解析集成（0.2秒/页，纯 CPU）
- ✅ 两阶段审查流程（用户确认后再编译）
- ✅ 加粗→黑体映射修复（`{\fzht 文字}` 分组语法）
- ✅ HTML 表格 → LaTeX 转换（colspan/rowspan）
- ✅ 端到端验证：DOCX → MD → LaTeX → PDF 全链路
- ✅ fireworks-tech-graph 流程图优化（12 风格，自适应宽度）
- ✅ flowchart-generator 中文优化版（6 样式 + 8 子命令，连线正交不歪斜，lhr 风格；擅长架构图/时序图，不适合复杂流程图）
- ✅ super-diagram 统一入口 skill（自然语言→多引擎路由，暗色主题 archdiagramgen 色板+JetBrains Mono+网格背景）
- ✅ **super-diagram v2.1 时序图支持（2026-08-09）**：render_v2.py 原生 `type:"sequence"`（participants+messages），防字体遮盖四原则（标签宽度自适应/行高独立/首行不遮参与者/时间戳避让），light（默认）+/dark 双主题，质量校验扩展参与者引用检查
- ✅ flowchart-generator style14/15/16/17 暗色主题视觉升级（网格背景、语义色、JetBrains Mono）
- ✅ **flowchart-generator v0.2.0 左侧标注层（2026-08-09）**：style13 画布左侧分层语义标注（USERS/GATEWAY/SERVICES 等，语义色条 + 中英双语），内容区自动右移避让 + 超宽自动收缩；L3/L5 支持 groups 形态；新增 07-agent-architecture.yaml 复杂多智能体架构测试（6 层 + 箭头 label + 反馈环）
- ✅ tikz-diagram 时序图 v5.1（紧凑布局，7 参与者）
- ✅ 办公超级 Skill 方案调研完成
- ✅ **harryopo-office 超级 skill（原 harryopo-latex 更名升级，2026-08-09）**：Word 模板引擎（Markdown 中间态 → .docx）并入，方正/开源字体 JSON 配置驱动，原生自动目录 + OMML 公式 + 表格/图片/注释/参考文献，端到端验证通过（表格/公式/目录全对）
- ✅ **docxtpl 模板填充子 skill（2026-08-09）**：用户 Word 模板 → extract schema（占位符扫描 + jinja2 类型推断）→ AI 产 data.json → validate/render 保真填充。支持表格行循环（{%tr %}）、条件块、图片（InlineImage）、对象/数组字段。端到端验证 11 项全通过（占位符零残留、循环表格 4 行、图片插入）
- ✅ **方案书 v2 + 开源方案深度调研（2026-08-28）**：`docs/plans/2026-08-28-office-super-skill-v2.md` + 调研报告（tex64 实为商业编辑器不采纳；markitdown/docling 为解析端增量；LaTeX MCP 生态转自封装 harryopo-build-mcp）
- ✅ **markitdown 解析路由 + Word→PDF 直出（2026-08-28）**：office.py 输入扩展至 MD/DOCX/PDF/图片/pptx/xlsx/epub/html/csv 等（DOCX 四级解析 anydoc→pandoc→markitdown→python-docx，PDF/图片 MinerU 优先→markitdown 兜底）；word_template_engine.py `save(export_pdf=True)` 同会话 `ExportAsFixedFormat` 导出 PDF；CLI `--pdf` 透传（md_to_word.py / office.py render）。验证：MD→Word→PDF 294KB、pptx 全链路 128KB、DOCX 兜底回归通过
- ✅ **LaTeX→Word 反向链路（2026-08-28）**：tex2md.py 清洗 .tex 全结构（{\fzht}黑体/章节/tabular/公式/figure/参考文献）→ MD 中间态 → md_to_word 渲染 Word/PDF；office.py 新增 .tex 输入分支；md_to_word 公式解析兼容单行 `$$...$$`（修复单行公式收集吞掉后续全文的致命 bug）。端到端断言全绿：标题/两表/3 OMML 公式/2 图片，PDF 314KB
- ✅ **模板注册表 v1（manifest.json，2026-08-28）**：`template_registry.py`（纯 stdlib）实现模板入库/发现/schema 管理（add/list/describe/schema/search/remove/update-usage），manifest 白名单严格校验（未知字段拒绝，对齐 M365 Copilot）；docx 入库自动复用 schema_extractor 提取 JSON Schema；内置 4 条模板（harryopo-paper/report/notes + docxtpl-example）；office.py 接入 `--template` 路由（latex→paper/notes 链路）+ `template` 委托子命令；`seed_builtins.py` 幂等初始化。端到端验证 24 项全绿（含 docx 全链路渲染占位符零残留）
- ✅ **环境补齐 + TexLite 部署（2026-08-28）**：TinyTeX 安装（D:\Tools\TinyTeX\TinyTeX，texlive 2026，xelatex/latexmk/latexmk 4.88 + ctex 全系宏包，清华镜像）；`harryopo-base.sty` 补 `\usetikzlibrary{positioning}`（修复 `below=0.6cm of B` 报 PGF Math Error）；TexLite v0.8.1 部署于 `opensource-reference/TexLite`（npm ci + init + build，127.0.0.1:3000，dataDir=output/texlite-data，admin/harryopo2026）；**方正字体接入走"项目自包含"**：修正副本 `Path=../fonts/`→`Path=fonts/` + 项目内 fonts/ 目录（TexLite 快照 cwd 无法命中宿主相对路径）。端到端 8/8 全绿（上传 22 文件 → 编译 succeeded → PDF 235KB 与 build.ps1 产物一致）
- ✅ **TexLite × harryopo MD 中间态改造（2026-08-28）**：TexLite 原生支持 `.md` 主文档（`config.md` 段配置 convertScript 指向 harryopo convert.py + pythonBinary + convertType）；改动：compileProject 反向检测同名 .md 快照→缓存目录内 convert.py 转 .tex→latexmk 编译；compileMainFile/.md→.tex 规范化；projects.ts PATCH 与 projectFiles 重命名校验放宽 .md/.markdown。端到端 8/8 全绿（PATCH mainFile=note.md → 编译 succeeded → PDF 30KB）
- ✅ **harryopo 模板 gallery → TexLite 入库（2026-08-28）**：借鉴 Oleafly 模板契约（template.json + 自包含目录 + main.tex）；`texlite_seed_templates.py` 打包 3 个模板（harryopo-paper/report/notes 修正副本 + fonts/ + 精简示例）通过 **ZIP import 原子导入** TexLite，全部编译 succeeded（paper 33KB / report 235KB / notes 47KB）；`texlite_preview_gen.py` 用 PyMuPDF 渲染 PDF 首页生成 preview.png（Oleafly 契约 preview 字段），模板 gallery 契约完整对齐
- ✅ **阶段 3 M1：harryopo-web 可视化编辑器 MVP（2026-08-28）**：`web-editor/`（Vite + React 19 + TipTap 3.30 + @tiptap/markdown + extension-mathematics + KaTeX + RawBlock/RawInline 兜底 + Express 后端）。核心：MD 中间态双向（round-trip 幂等测试 8/8）、harryopo 单行 `$$...$$`=块级公式定制、工具栏、实时预览、导出复用 office.py。验证：构建通过 + API 端到端 8/8（Word 导出 35KB docx 可下载）。运行：后端 :8080 + 前端 :5173
- ✅ **阶段 3 M2：文件树 + 模板注册表表单 + 图表（2026-08-28）**：web-editor 升级——文件树（多文档/子目录 + 安全路径防穿越）、模板注册表对接（docx 模板 schema 动态表单 → data.json → docxtpl 渲染下载）、mermaid 前端渲染。验证：API 端到端 13/13（含模板渲染 35KB docx）。生产模式 http://127.0.0.1:8080 直接访问

**待开发**：

- ⬜ harryopo-book.cls + harryopo-notes.cls
- ⬜ docling 接入（MinerU 互为兜底）+ harryopo-build-mcp（编译诊断闭环）
- ⬜ 阶段 3 M3（Yjs 协同 + inline diff + AI 流式插入）· office.py paper 链路排查

---

## 硬规则

### 编译

- **必须使用 XeLaTeX**，不得使用 pdfLaTeX 或 LuaLaTeX
- 编译 3 遍以确保交叉引用和目录稳定
- build.ps1 使用 TEXINPUTS 环境变量让 xelatex 在 templates/ 目录搜索 .cls/.sty

### 模板架构

- **共享体系**（report/paper/book/notes）均加载 `harryopo-base.sty`，使用 `\ifdefined\harryopo@theme` 机制传递主题
- **math-notes 是独立体系**（`templates/math-notes/`），不加载 base.sty，不修改其架构
- 新增模板必须：基于 ctexart/ctexbook/extarticle，加载 harryopo-base.sty，遵守主题中继机制

### 命名

- 模板文件前缀 `harryopo-`
- 示例文件前缀 `example-`
- 文档类 `.cls`、样式包 `.sty`

### 办公文档生成铁律

- **绝不让 AI 直接生成 .docx/.pdf 二进制** —— LLM 在语义层，文档在排版层，抽象不匹配
- AI 只产出结构化数据（JSON/Markdown），模板引擎负责渲染
- 模板的最佳形态是用户熟悉的工具本身（.docx、.tex、.html）
- 中文支持是硬约束（字体嵌入、CJK 断行、标点处理）

---

## 踩坑警示

1. **不要在 math-notes 中引入 base.sty**——mdframed 边框体系与 tcolorbox 冲突，字体配置也不兼容
2. **不要用 multicol 做双栏**——ctexart 原生 twocolumn 选项配合 cuted+flushend 是最优解
3. **不要在 .sty 中用 kvoptions**——主题通过 `\def\harryopo@theme{}` 在加载 base.sty 前设定
4. **algorithm2e 需要 \newcounter{chapter}**——ctexart 无 chapter 计数器
5. **marginfix 必须加载在 geometry 之后**
6. **`\hfuzz` 对显式 `\hbox to` 命令无效**——仅对段落自动断行产生的溢出敏感，对 TeX 原语级别的 `\hbox to <dimen>` 溢出无能为力
7. **`silence` 包无法过滤 Tex 原语级别的 Overfull \hbox**——`silence` 仅处理 LaTeX 层次的警告，需用 `\rlap` 等调整内容宽度来消除
8. **超出 `\textwidth` 的图片/内容用 `\rlap{}` 包裹**——让内容向右延伸到页边距而不产生 overfull box
9. **不要在 base.sty 中重复加载 ctex**——cls 已通过 ctexart/ctexrep 加载，重复加载导致 `Missing \begin{document}` 致命错误
10. **CJK 字体族名不要与 ctex 默认集冲突**——`zhkai`/`zhfs`/`zhhei` 是 fandol 默认定义的，用 `\newCJKfontfamily` 创建独立族（如 `hrypkai`）
11. **`\and` 在 `\twocolumn[]` 中会触发 `\crcr` 错误**——改用中文顿号 `、` 分隔作者
12. **`strip` 环境 (cuted) 与 booktabs 冲突**——改用 `\twocolumn[]` 替代
13. **unicode-math 的 SizeFeatures 需要 XITSMath.otf（无 -Regular 后缀）**——必须从 XITSMath-Regular.otf 复制一份
14. **fontspec BoldFont/ItalicFont 不可用 `*` 通配符**——黑体/楷体是独立文件，必须显式指定
15. **longtable 的 \endfirsthead/\endhead 前面不能放 \multicolumn 内容行**——只能放 \hline
16. **MinerU DOCX 表格输出是 HTML 格式**——保留 colspan/rowspan，可直接映射到 \multicolumn/\multirow
17. **MinerU 会给 Word 标题标记加粗**——清洗时需去掉 `# **标题**` 中的 `**`
18. **`\fzht{文字}` 的花括号不会限制字体切换范围**——必须用 `{\fzht 文字}` 分组语法（所有字体快捷命令均适用）
19. **绝不让 AI 直接生成 .docx/.pdf**——AI 只产出结构化数据，模板引擎负责渲染
20. **让 AI 输出完整文档 + 系统自己 diff**——比让 AI 输出"操作序列"可靠得多
21. **踩坑**: **YAML 内联映射必须用 `{key: val, key2: val2}` 格式**——直接用空格分隔 key value 会导致 `ScannerError: mapping values are not allowed here`，flowchart-generator 的 gen.py 用 yaml.safe_load 解析，格式错误会直接报错
22. **踩坑**: **暗色主题下 SVG `<defs>` 不能双层嵌套**——flowchart-generator 的 gen.py 在暗色主题时先 append grid pattern 的 `<defs>`，再 append markers 的 `<defs>`，会产生 `<defs><defs>` 双层嵌套导致 XML 解析失败；必须合并到单个 `<defs>` 块中
23. **踩坑**: **`resolve_colors(data)` 必须用于所有 style 函数**——`data["colors"]` 在暗色主题时是空 dict `{}`，必须用 `resolve_colors(data)` 才能正确填充 DARK_THEME 默认色板
24. **踩坑**: **style15 使用 `steps` 数据，style16 使用 `nodes+edges` 数据**——不同 style 的数据格式不同，gen.py 通过 `build_svg_by_style` 路由，不共享同一数据结构
25. **踩坑**: **docxtpl 的 `{%tr for %}` 与 `{%tr endfor %}` 必须各自独占一行**——docxtpl 按"整行含标签"机制处理：for 行被替换为 for 语句、endfor 行被替换为 endfor 语句，中间的数据行（`{{ task.xxx }}`）在渲染时被循环复制；若把 for/endfor 塞进同一行不同单元格，整行会被吞掉导致 jinja2 `Encountered unknown tag 'endfor'`
26. **踩坑**: **docxtpl 占位符不能跨 run**——Word 中对占位符做加粗/改色会拆成多个 run 导致无法识别；模板中占位符必须连续
27. **踩坑**: **新版 docxtpl（0.20+）已移除 `get_defined_variables()`**——schema 提取需自己扫描 docx XML 的 `<w:t>` 节点用正则提取占位符，并模拟 jinja2 作用域栈推断类型；`{%tr`/`{%p`/`{%tc` 前缀标签在正则中需用 `(?:(?:tr|tc|p|r)\s+)?` 处理
28. **踩坑**: **docxtpl 图片字段在 data.json 中写 `{"image": "path", "width_mm": 30}`**——渲染器识别含 `image` 键的 dict 自动转 InlineImage，校验器 string 分支也需放行此类 dict
29. **踩坑**: **flowchart-generator style13 箭头坐标必须写"内容坐标"（不含 sx 左侧标注层偏移）**——渲染时自动 +sx；曾误把 sx=120 估算值写进 YAML，实际 sx=116（"API GATEWAY" 含空格宽度小），导致箭头偏离组中心 ~120px。对齐方法：箭头 x = 目标组/卡的内容中心（组 `x:30 w:395` → 中心 `227.5`）。**改 items 行数后需同步检查下方层 y**：组高内容驱动后（L4 3行=184 vs 旧固定 120），下方层需留足间隙；**卡片尺寸必须内容驱动**——显式 `h: 240` 等固定约束会导致"卡片大文字空"，组高按 items/sub_items 行数自动算（`20+行数×52+8`），组宽按最长文本自动算（CJK≈1.0×字号，ASCII≈0.58×字号）
30. **踩坑**: **skill 生成产物不能落 C 盘**——Trae 全局 skill 目录在 `c:\Users\Administrator\.trae-cn\skills\`（C 盘），若生成器把 output/generated/archive 默认写到 skill 目录旁会持续吃 C 盘空间。flowchart-generator 通过 `_OUT_ROOT`（默认 `d:\ai\latex\output\flowchart-generator`，可用环境变量 `FLOWCHART_OUT_DIR` 覆盖）重定向所有产物到 D 盘项目目录；测试脚本同样需指向 D 盘，否则 `shutil.rmtree`/`--out-dir` 会重新在 C 盘建目录

---

## 项目事实

- **位置**: `d:\ai\latex\`
- **项目定位**: 办公文档 AI 生产力平台（LaTeX + Word + 流程图 + PPT）
- **核心模板**: `templates/cls/` — harryopo-base.sty + paper.cls + report.cls
- **字体目录**: `templates/fonts/` — 18 个内嵌字体（方正+XITS+TeX Gyre Heros）
- **编译脚本**: `templates/build.ps1`
- **转换 Skill**: `.trae/skills/harryopo-office/`
- **记忆系统**: `memory/MEMORY.md`
- **学习日志**: `.learnings/`
- **方案设计**: `docs/plans/` 和 `docs/research/`
- **流程图参考**: `opensource-reference/fireworks-tech-graph/`（原始12风格）
- **架构图参考**: `opensource-reference/archdiagramgen/`（暗色主题 + 箭头遮罩 + HTML 导出工具栏）
- **流程图生成器**: `c:\Users\Administrator\.trae-cn\skills\flowchart-generator/`（6 样式，擅长架构图/时序图；产物输出到 `d:\ai\latex\output\flowchart-generator/`，默认 D 盘避免占用 C 盘）
- **TikZ 图表**: `skills/harryopo-tikz-diagram/`
- **数理笔记**: `templates/math-notes/`（独立体系）
- **kaobook**: `参考资料/中文book/`（独立体系）

## 协作流程

1. 修改 .cls/.sty 后，编译所有示例验证
2. 新增文件后更新 `memory/MEMORY.md`
3. 遇到新踩坑后追加到 `.learnings/LEARNINGS.md` 和本文
4. 删除文件前确认无引用
5. 大方案先写 `docs/plans/` 下计划文档，再实施
