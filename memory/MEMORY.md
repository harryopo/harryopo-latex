# 项目记忆 — d:\ai\latex

> 最后更新: 2026-08-30 | 版本: 办公超级 Skill v3（阶段 3 重定义：IDE 生态+修订审阅）+ 第三轮增量调研

---

## 项目定位（2026-08-08 更新）

**办公文档 AI 生产力平台** — 以 harryopo LaTeX 模板体系为核心，扩展覆盖 Word / PDF / PPT / 流程图 全格式办公文档生成。

核心范式：**AI 产出结构化数据 → 模板引擎渲染 → 输出文档**（绝不让 AI 直接生成二进制文档）

---

## 当前文件结构

```
d:\ai\latex\
├── CLAUDE.md                   # Agent 项目规则
├── .learnings/                 # 学习日志
│   ├── 2026-07-26-harryopo-latex-4-problems.md
│   ├── 2026-07-26-harryopo-latex-fonts-fix.md
│   ├── ERRORS.md
│   ├── FEATURE_REQUESTS.md
│   └── LEARNINGS.md
├── memory/
│   └── MEMORY.md               # 本文件
├── docs/
│   ├── plans/
│   │   ├── 2026-06-20-latex-templates.md    # 原始计划
│   │   ├── 2026-08-05-harryopo-latex-skill-extension.md
│   │   ├── 2026-08-05-harryopo-latex-skill-extension-v2.md
│   │   └── 2026-08-08-office-super-skill.md # 最新：办公超级 Skill 方案
│   ├── research/
│   │   ├── 2026-08-08-ai-office-generation.md
│   │   ├── 2026-08-08-template-engines.md
│   │   └── 2026-08-08-visual-editing.md
│   ├── LaTeX-TikZ画图实战指南.md
│   ├── TikZ画图与文字转图方案深度调研报告.md
│   ├── Word-Markdown-to-LaTeX-开源方案深度调研报告.md
│   └── templates-research.md
├── templates/
│   ├── cls/
│   │   ├── harryopo-base.sty   # 共享基础包 v4.2
│   │   ├── harryopo-paper.cls  # 论文文档类 v4.0
│   │   └── harryopo-report.cls # 报告文档类 v4.0
│   ├── fonts/                  # 18个内嵌字体
│   ├── paper/
│   │   ├── showcase-paper.tex/pdf     # 单栏论文示例
│   │   └── example-paper-twocolumn.tex/pdf  # 双栏论文示例
│   ├── report/
│   │   └── showcase-report.tex/pdf    # 报告示例
│   └── build.ps1               # 编译脚本 v4.2
├── 参考资料/中文book/          # kaobook 中文书籍（独立体系）
├── opensource-reference/
│   └── fireworks-tech-graph/   # 流程图 SVG 生成器（12 风格）
├── skills/
│   └── harryopo-tikz-diagram/  # TikZ 图表生成 Skill
└── .trae/skills/
    └── harryopo-latex/         # 统一 Skill（模板 + 转换 + 编译）
        ├── SKILL.md
        ├── scripts/
        │   ├── convert.py      # MD/DOCX → .tex 转换引擎
        │   ├── html_table_to_latex.py  # HTML表格 → LaTeX
        │   ├── mineru_cli.py   # 两阶段审查 CLI
        │   └── md2latex.py
        └── templates/          # cls/sty/fonts/build.ps1 + 示例
```

---

## v4.2 修复清单（2026-06-22）

| 问题 | 根因 | 修复 |
|------|------|------|
| `Missing \begin{document}` | base.sty 重复加载 ctex | 移除 `\RequirePackage{ctex}` |
| CJK 字体族冲突 | `zhkai`/`zhfs` 与 fandol 默认重名 | 改用 `hrypkai`/`hrypfs` 等 hrp- 前缀 |
| `\crcr` 错误 (booktabs) | `strip` 环境与 booktabs 冲突 | `\twocolumn[]` 替代 `strip` |
| `\crcr` 错误 (作者) | `\and` 在 `\twocolumn[]` 中冲突 | 作者改用顿号 `、` 分隔 |
| XITSMath 字体找不到 | SizeFeatures 需要无 -Regular 后缀 | 自动复制 XITSMath-Regular.otf → XITSMath.otf |
| BoldFont 查找错误 | `*HTJW` 通配符不适用 | 显式 `FZHTJW`/`FZKTJW` |
| 读书笔记编译失败 | unicode-math 强依赖 | `nomath` 选项，用 amsmath/amssymb 替代 |
| build.ps1 多跑 1 遍 | 页数提取跑第 4 遍 xelatex | 从第 3 遍日志提取 |

---

## Skill 包说明

### harryopo-latex（统一 Skill，已合并 convert）
- 自包含：cls/sty/fonts/build.ps1 + scripts/convert.py
- 支持两种模式：手写 .tex 或 MD/DOCX 自动转换
- 使用 TEXINPUTS 环境变量发现 cls 和字体
- build.ps1 自动检查环境（xelatex/字体/cls）
- convert.py 支持 `--no-math`（读书笔记/无数学文档）
- 自动提取标题/作者/摘要/关键词
- **2026-08-05 新增**: 加粗→黑体映射（`**加粗**` → `{\fzht 加粗}`，非 `\textbf`）
- **2026-08-05 新增**: MinerU DOCX 原生解析集成（0.2秒/页，保留 colspan/rowspan）
- **2026-08-08 新增**: 两阶段审查流程（`--stage review` / `--stage convert`），用户确认后再编译
- **2026-08-08 新增**: 行内加粗精确修复——`{\fzht 文字}` 分组语法替代 `\fzht{文字}`，消除字体泄漏
- **2026-08-08 新增**: convert.py BLOCK_RAW_LATEX 块类型，透传 MinerU 清洗后的 LaTeX 环境

---

## 2026-08-05 MinerU 集成 + 加粗→黑体修复

### 加粗→黑体修复（convert.py）
- **问题**: MD 的 `**加粗**` 转为 `\textbf{}`，中文字体加粗后笔画糊
- **修复**: 统一改为 `\fzht{}`（方正黑体），符合中国学术排版规范
- **影响行**: parse_inline() 的 `**` 和 `***` 正则、表头 `_parse_table`、DOCX run 粗体
- **验证**: test-bold-heiti PDF 编译通过，xelatex EXIT=0

### MinerU DOCX 解析集成
- **版本**: MinerU 3.0.4 (Apache 2.0 开源)
- **安装**: `pip install -U "mineru[all]"` + `mineru-models-download`（选 modelscope + pipeline）
- **模型缓存**: `C:\Users\Lenovo\.cache\modelscope\models\OpenDataLab--PDF-Extract-Kit-1.0`
- **配置文件**: `C:\Users\Lenovo\mineru.json`
- **核心 API**:
  ```python
  from mineru.backend.office.docx_analyze import office_docx_analyze
  from mineru.backend.office.office_middle_json_mkcontent import union_make
  from mineru.utils.enum_class import MakeMode
  middle_json, results = office_docx_analyze(file_bytes, image_writer)
  md = union_make(middle_json['pdf_info'], MakeMode.MM_MD, img_dir)
  ```
- **性能**: 0.23 秒解析 3 表格 + 多级标题（4.3 页/秒），纯 CPU
- **输出**: Markdown + HTML 表格（保留 colspan/rowspan）+ 图片
- **CLI 问题**: `mineru -p xxx.pdf` 可能卡住（API 服务架构），建议用 Python API

### 端到端验证（DOCX → PDF 全链路）
- **测试文件**: test-mineru-complex.docx（3 表格 + 多级标题 + 加粗/斜体 + 合并单元格）
- **管线**: DOCX → MinerU 解析 → MD 清洗（简单表转MD、合并表保留HTML）→ convert.py → LaTeX → xelatex → PDF
- **结果**: ✅ PDF 41708 bytes 编译成功
- **测试脚本**: `test_e2e_pipeline.py`

### 关键发现
1. **MinerU DOCX 表格输出是 HTML 格式**（非 MD 表格），原生保留 `colspan`/`rowspan`
2. **HTML 表格 → LaTeX 是后续增强重点**（LLM 修复或脚本转换 `\multicolumn`/`\multirow`）
3. **MinerU 标题会被标记为加粗**（Word 标题样式含 bold），清洗时需去除 `# **标题**` → `# 标题`
4. **MinerU DOCX 解析速度极快**（0.2秒/页 vs PDF 路径需 OCR+布局分析）

### 方案文档
- v2 方案: `docs/plans/2026-08-05-harryopo-latex-skill-extension-v2.md`
- 开源调研: `docs/Word-Markdown-to-LaTeX-开源方案深度调研报告.md`
- 办公Agent调研: `docs/2026-08-05-办公Agent与AI文档助手文档处理与PDF生成深度调研报告.md`

---

## 2026-08-05 P0-P2 实施完成（表格转换 + mineru_cli + SKILL.md）

### 新增脚本

#### 1. `scripts/html_table_to_latex.py`（P0 核心）
- **功能**: MinerU HTML 表格 → LaTeX 转换器
- **支持**: 简单表(tabularx) / 水平合并(multicolumn) / 垂直合并(multirow) / 跨页表(longtable)
- **算法**: HTML 解析 → 网格构建（处理 rowspan 占位）→ LaTeX 生成
- **关键类**: `Cell`(is_rowspan_cover/is_colspan_cover) / `ParsedTable` / `generate_latex`
- **接口**: `html_table_to_latex(html, caption)` / `replace_html_tables_in_markdown(md)`
- **编译验证**: 4 种表格类型全部通过 xelatex 编译（含 colspan+rowspan 交叉）

#### 2. `scripts/mineru_cli.py`（P1 全流程封装）
- **功能**: DOCX/PDF/MD → 清洗后 Markdown（整合 MinerU + 清洗 + HTML 表格转换）
- **CLI**: `python mineru_cli.py input.docx -o output_dir/ [--backend auto|office|pipeline]`
- **清洗规则**: 去标题加粗(`# **标题**` → `# 标题`) + HTML 表格转 LaTeX + 压缩空行
- **性能**: DOCX 解析 0.2 秒/页，纯 CPU

### SKILL.md 更新
- 新增"方式A：MinerU DOCX → MD → LaTeX"完整流程
- 表格处理能力对照表（4 种类型）
- 加粗→黑体规则说明
- MinerU 安装和模型下载步骤

### 端到端验证 v2
- **测试**: DOCX 含 3 表格（简单 + 水平合并 + 垂直合并）
- **管线**: DOCX → mineru_cli.py → MD → convert.py → LaTeX → xelatex → PDF
- **结果**: ✅ PDF 30891 bytes，`\multicolumn`/`\multirow`/`\fzht` 全部正确

---

## 2026-08-08 两阶段审查流程 + 行内加粗精确修复

### 核心修复：`{\fzht 文字}` 分组语法

| 问题 | 根因 | 修复 |
|------|------|------|
| 整段文字被黑体 | `\fzht` 是声明式命令（类似 `\bfseries`），`\fzht{文字}` 的花括号结束后字体切换仍然有效 | 所有脚本统一生成 `{\fzht 文字}`（分组调用，字体切换限制在花括号内） |
| 表头自动加粗错误 | `_generate_longtable` 有 `if row_idx == 0: \fzht{}` 自动表头加粗 | 删除全部 3 处自动加粗逻辑，只保留原文 `**` 标记 |
| 英文/数字被黑体 | 自动表头加粗把 "AI" 等英文也加了黑体 | 去掉自动加粗后消除 |

**修改文件**:
- `harryopo-base.sty`: 还原 `\fzht` 为简单声明式定义
- `html_table_to_latex.py`: `_bold_replacer` 输出 `{\fzht text}` 格式
- `convert.py`: 5 处 `\fzht{...}` → `{\fzht ...}`

### 两阶段审查流程

mineru_cli.py 重构为两阶段：
1. `--stage review`: DOCX → 标准 MD（加粗用 `**`，表格保留 HTML）→ **展示给用户确认**
2. `--stage convert`: 审查 MD → 含 LaTeX 代码的 MD → 编译

### 真实文档验证

- **测试文件**: 仿生黑色素生物材料成果调研报告.docx（27行×6列表单）
- **管线**: DOCX → mineru_cli.py --stage review → 用户确认 → --stage convert → convert.py → xelatex
- **结果**: ✅ PDF 131195 bytes，4 页，15 处精确行内加粗，零溢出零错误

---

## 技术栈

| 维度 | 选择 |
|------|------|
| TeX 引擎 | XeLaTeX |
| 中文支持 | ctex/xeCJK |
| 文档类基类 | ctexart (paper)、ctexrep (report) |
| 数学字体 | XITS Math (unicode-math) 或 amsmath (nomath) |
| 英文字体 | XITS (Times 风格) |
| 中文字体 | 方正系列（书宋/黑体/楷体/仿宋/大标宋/小标宋） |
| 代码高亮 | listings |
| 算法 | algorithm2e |
| 表格 | booktabs (三线表) |
| 双栏跨栏 | \twocolumn[] (不用 cuted strip) |
| Word 模板引擎 | docxtpl（待集成） |
| PDF 模板引擎 | Jinja2 + Pandoc（待集成） |
| PPT 生成 | Marp / Presenton（待集成） |
| 流程图 | flowchart-generator（6 样式，擅长架构图/时序图，不适合复杂流程图）+ TikZ |

---

## 已验证编译通过的文件

| 文件 | 类型 | 大小 | 页数 |
|------|------|------|------|
| showcase-paper.pdf | 单栏论文 | 261KB | 8页 |
| example-paper-twocolumn.pdf | 双栏论文 | 164KB | 3页 |
| test-sample.pdf | convert.py 生成 | 97KB | 2页 |
| showcase-report.pdf | 报告 | 235KB | 15页 |
| example-report.pdf | 报告示例 | 242KB | 14页 |

全部 46 个 .tex 文件编译成功，0 失败。

---

## harryopo-tikz-diagram Skill 更新（2026-07-27）

### 时序图 v5.1 三阶段紧凑布局完成
- **核心突破**: 三阶段绘制架构（Pass1 Dry Run → Pass2 Geometry → Pass3 Labels → Final Layer）彻底解决文字遮盖问题
- **文件更新**:
  - `skills/harryopo-tikz-diagram/templates/sequence-diagram/template.tex` — v5.1紧凑版模板
  - `skills/harryopo-tikz-diagram/examples/example-sequence-diagram.tex` — 7参与者一键部署时序图
  - `skills/harryopo-tikz-diagram/SKILL.md` — 添加模板四：UML时序图完整章节
- **紧凑版间距常量**: GapMsg=0.88, GapRet=1.00, GapSelf=1.40, GapPhase=0.28, FragPad=0.15, SelfLoopH=0.50（cm）
- **编译结果**: 7参与者+alt+loop+4阶段，1页PDF，0 Overfull

## fireworks-tech-graph / flowchart-generator 流程图体系（2026-08-08 更新）

### 关系说明
- **fireworks-tech-graph**（`opensource-reference/fireworks-tech-graph/`）：原始版本，12 种风格，侧重 Web 可视化
- **flowchart-generator**（`c:\Users\Lenovo\.trae-cn\skills\flowchart-generator/`）：优化版，专为中国场景定制
  - 核心改进：连线正交不歪斜、中文排版适配、布局参数精确计算
  - 6 种样式（style13-18）+ 8 个子命令，输出独立可运行 .py
  - 暗色主题：`meta.theme: dark` → 网格背景 + JetBrains Mono + 语义色板 + 箭头遮罩层
  - HTML 导出：`--html` 参数 → 含内置 PNG/PDF 工具栏（html2canvas + jsPDF）
  - 独立 .py 新增 `--html` / `--open` 参数（离线可用）

### fireworks-tech-graph（原始版本）
- 位置: `opensource-reference/fireworks-tech-graph/`
- 风格: Style 7 — OpenAI Official（极简白底+品牌绿）
- 输出: `output/zhixing-agent-style7.svg`
- 参考: `d:\ai\claude code\微信读书\zhixing-reader\deliverables\agent编排流程图_详细说明.md`
- 紧凑化: 1200×1800 → 1200×460（高度压缩74%），自适应宽度算法
- 紧凑化关键参数：
  | 元素 | 原始值 | 最终值 | 说明 |
  |------|--------|--------|------|
  | 视图尺寸 | 1200×1800 | 1200×460 | 高度压缩74% |
  | 策略小卡片宽度 | 210（统一） | 120-130（按内容） | 内容结束后截止 |
  | 难度动作小卡片宽度 | 210（统一） | 108-170（按内容） | 内容结束后截止 |
  | 小卡片水平间距 | 84 | 18 | 紧密排列 |
  | Step卡片高度 | 46-52 | 24-28 | 减少内部空白 |
  | 小卡片高度 | 24 | 20 | 减少内部空白 |
  | 节点垂直间距 | 12 | 3-4 | 收紧流程 |
  | Section间距 | 28 | 6-8 | 减少分组空白 |

---

## 办公超级 Skill 方向（2026-08-08）

### 核心范式转变
**旧范式**: AI 直接生成 .docx/.pdf → 排版崩坏、不按模板
**新范式**: AI 产出结构化数据 → 模板引擎渲染 → 输出文档

### 四大需求 → 技术对策
| 需求 | 技术对策 |
|------|---------|
| AI 输出按模板来 | docxtpl (Word) + Jinja2 (LaTeX) |
| Word ↔ MD ↔ LaTeX 互转 | Pandoc 为中枢 |
| 办公文件可视化编辑 | TipTap + Yjs + inline diff |
| 用户模板入库 | 模板注册表 + 自动 schema 提取 |

### 分阶段路线图
- **阶段 1（立即）**: docxtpl 模板填充子 skill + 模板注册表 v1
- **阶段 2（短期）**: 本地预览服务器（PDF/HTML 自动开浏览器）
- **阶段 3（中期）**: React + TipTap Web 编辑器
- **阶段 4（长期）**: 模板市场 + 多人协作 + ONLYOFFICE 集成

### 关键技术选型
| 格式 | 方案 | 说明 |
|------|------|------|
| Word | docxtpl (Python) | Jinja2 语法，.docx 即模板，Python 生态 |
| PDF | Jinja2 + XeLaTeX | harryopo 模板体系已就绪 |
| PPT | Marp 或 Presenton | 技术内容用 Marp，设计型用 Presenton |
| 流程图 | fireworks-tech-graph + TikZ | 12 风格 SVG + 精确 TikZ 渲染 |

### 关键避坑
1. **绝不让 AI 直接生成 .docx/.pdf 二进制**
2. **模板的最佳形态是用户熟悉的工具本身**
3. **AI 的角色限定为"数据生产者"**（通过 structured output 约束）
4. **让 AI 输出完整文档 + 系统自己 diff**（比操作序列可靠）
5. **中文支持是硬约束**（字体嵌入、CJK 断行）
6. **inline diff + 建议模式混合**（避免全文重生成）
7. **版本审计是差异化机会**（AI/手动标记）

---

## arch-prompter Skill（2026-08-09 完成）

路径: `c:\Users\Lenovo\.trae-cn\skills\arch-prompter/`

**核心能力**: 自然语言描述 → 架构图文档合同 + flowchart-generator YAML

**支持样式**:
- style13 — 多层架构（layers + arrows）
- style14 — 智能体编排（main_flow + intents + sources + tools）
- style15 — 数据管线（steps 横版，type: trigger/process/decision/storage/output）
- style16 — 数据流图（nodes + edges，4 类节点）

**技术要点**:
- jieba 中文分词 + 30+ 自定义技术节点词库（防止复合词拆分）
- 启发式节点类型推断（backend/db/frontend/security/bus/cloud/external）
- 多风格 YAML 格式分发（按 style ID 输出不同结构）
- 端到端验证: 3 个测试用例全部成功渲染 HTML（13/14/15 风格）

**踩坑**:
- YAML 内联映射必须用 `{key: val}` 格式，空格分隔会导致 ScannerError
- style14 要求 intents 字段非空，不足时补充默认项

---

## 办公超级 Skill v2 落地：markitdown 路由 + Word→PDF（2026-08-28 完成）

### 方案书与调研
- 方案书 v2: `docs/plans/2026-08-28-office-super-skill-v2.md`
- 调研报告: `docs/research/2026-08-28-开源方案深度调研-tex64-mcp-markitdown-docling.md`
- tex64 澄清: 商业 LaTeX 编辑器非开源，不采纳；方向转为自封装 harryopo-build-mcp

### 已实施（commit 4fd23c0）
1. **markitdown 三级/四级解析路由**（office.py）:
   - 新增 `convert_via_markitdown(path)`（微软官方 0.1.7）与 `convert_via_mineru(path, out_dir)`（调 mineru_cli.py --stage auto 读 result.md）
   - 输入扩展: `.md` / `.docx,.doc` / `.pdf,.png,.jpg,.jpeg`（MinerU 优先→markitdown 兜底）/ `.pptx,.xlsx,.epub,.html,.csv,.json,.xml,.zip,.msg,.ipynb,.txt`（markitdown 直转）
   - DOCX 四级解析: anydoc → pandoc → markitdown → python-docx（markitdown 自带 GFM 表格，tables=[] 不回填）
2. **Word→PDF 直接导出**（word_template_engine.py）:
   - `save(export_pdf=True)` → `_update_toc_com` 同会话 SaveAs2 后 `ExportAsFixedFormat(OutputFileName, ExportFormat=17, OptimizeFor=0, CreateBookmarks=1)`
   - `--no-toc` 时走独立 `_export_pdf_com`（Close(False) 只读导出）
   - CLI: md_to_word.py `--pdf`、office.py render `--pdf`
3. **验证**（低成本确定性检查）: py_compile 3 文件 ✅；MD→Word→PDF 294KB ✅；pptx→markitdown→MD→Word→PDF 128KB 全链路 ✅；DOCX 主路径回归（anydoc/pandoc 缺失时 markitdown 兜底实际生效）✅

### 环境备注
- 当前默认 Python 3.14（pythoncore-3.14-64）为新环境: 已装 markitdown[docx,pptx,xlsx] + python-docx 1.2.0 + pywin32 312；pandoc/xelatex 不在该环境 PATH（验证时 markitdown 兜底接管了 pandoc 缺失场景，恰好证明路由价值）
- 产物验证目录: `output/v2-verify/`（已 gitignore）

## 办公超级 Skill v2 落地：LaTeX→Word 反向链路（2026-08-28 完成，commit 427727e）

方案书 v2 §4 落地：`.tex → MD 清洗 → Word 引擎渲染`（不直转，统一走 MD 中间态核心范式）。

### 新增/修改
1. **tex2md.py**（新建）— LaTeX→MD 清洗，处理 harryopo 全结构:
   - `{\fzht }`/`\textbf` → `**`（黑体闭环）；`\section/subsection/subsubsection` → `#/##/###`
   - `tabularx/tabular` → GFM 表格（列定义行/`\toprule\midrule\bottomrule` 跳过；表格单元格黑体**不转 `**`**——Word 表格字体由模板样式控制，星号会原样显示）
   - `equation/align` → `$$ ... $$` 单行；`figure` → `![caption](绝对路径)`；`quote` → `> 注释`
   - table 浮动体: 消费到 `\end{table}`，空 `\caption{}` 占位丢弃、非空提取为 `> **表N：**`
2. **md_to_word.py** — 公式解析兼容单行 `$$ ... $$`（此前只支持多行，导致单行公式收集循环吞掉从 `式(3)` 到文件尾全部内容 → 表2/四/五章/参考文献静默丢失、OMML 错乱）
3. **office.py** — `.tex` 输入分支（`from tex2md import tex_to_md`）+ Word 同会话 PDF 产物提示

### 验证（端到端断言全绿）
- 中间态: 无 `\begin/\end/toprule/caption` 残留；表格 14 行（两表 8+6）；图片 2；公式 3 对
- docx: 主标题 ✓ 两表（表头无 `**`）✓ 3 个 OMML 公式 ✓ 2 张图片 ✓
- 完整入口 `office.py render input-paper.tex --format word --pdf` → docx 44KB + PDF 314KB（%PDF 头有效）
- e2e 样本缺图修复: PIL 生成 `蒸馏区/e2e-test/figures/arch.png` + `pipeline.png`（真实图片，非占位）

### 关键踩坑（tex2md/LaTeX→Word）
- 表格标题在**独立 quote 块**（`\begin{quote}{\fzht 表1：...}\end{quote}`），表格 caption 常为**空 `\caption{}`** 占位 → 必须丢弃，否则裸文本残留中间态
- 单行公式 `$$ ... $$` 与 md_to_word 多行公式收集逻辑不兼容 → 必须两端对齐（md_to_word 兼容单行）

### 下一步（按方案书 v2 路线图）
- ⬜ docling 接入（MinerU 互为兜底）、harryopo-build-mcp、本地预览服务器

## 办公超级 Skill v2 落地：模板注册表 v1（2026-08-28 完成）

方案书 v2 §7 + 调研报告 `docs/research/2026-08-28-模板注册表v1可行性调研.md` 落地。阶段 1 收尾项清零。

### 新增/修改
1. **template_registry.py**（新建，纯 stdlib）— 注册表骨架 + CLI:
   - `add`（docx 自动调 schema_extractor 提取 schema；latex/md/html 登记）、`list`（格式/分类/关键字过滤）、`describe`（详情 + schema 摘要）、`schema`（导出）、`search`、`remove`（builtin 需 --force）、`update-usage`
   - manifest 白名单严格校验：未知字段拒绝加载并报错定位（对齐 M365 Copilot 严格模式）；枚举校验（format/source/engine）+ id 唯一
   - `seed_builtins.py` 幂等初始化内置 4 条：harryopo-paper/report/notes（latex）+ docxtpl-example（docx，自动 schema）
2. **office.py** — `render --template <id>` 路由（latex→paper/notes 链路、docx→提示走 docx_template.py）+ `template` 委托子命令（argparse.REMAINDER 透传）；`run()` 捕获 FileNotFoundError 优雅失败（xelatex 缺失不再崩溃 traceback）
3. **SKILL.md** — 新增"场景D：模板注册表"章节

### 验证（端到端断言 24 项全绿）
- 内置 4 条 id 集合/来源/分类 ✓；add→schema 自动生成（8 字段、tasks=array、owner=object、need_abstract 可选，与原始提取一致）✓；重复 add 报错 ✓；未知字段拒绝加载 ✓；builtin remove 保护 ✓
- docx 全链路：注册表模板 + schema + data.json → docxtpl render → 占位符零残留、项目名/循环表格数据落盘 ✓
- office.py 路由：template list/schema 委托 ✓、不存在模板报错 ✓、--template harryopo-paper 正确追加 paper 链路 ✓

### 关键踩坑
- **office.py template 子命令 `-o` 被 argparse 拦截**：nargs='+' 不吞选项参数 → 改用 `argparse.REMAINDER` 原样透传
- **cmd_remove 错误 print 到 stdout**：check 端取 stderr 拿不到 → 统一报错写 stderr
- **docxtpl render 图片相对路径以 cwd 为基准**：验证脚本 cwd 需设为 template 目录（data.json 里 `examples/demo.png` 才能解析）
- **当前默认 Python 3.14 缺 docxtpl**：pip 补装（0.20.2，schema_extractor 已适配该版本无 get_defined_variables）；**xelatex/pandoc 不在该环境 PATH**（LaTeX 编译链路待环境补齐，注册表核心验证不依赖）

### 下一步（按方案书 v2 路线图）
- ⬜ **M2 LaTeX 模板反解**（harryopo 占位符约定 `% [harryopo:placeholder]` 规则引擎 + LLM 补语义描述）
- ⬜ docling 接入（MinerU 互为兜底）、harryopo-build-mcp、本地预览服务器
- ⬜ xelatex/pandoc 环境补齐（当前默认 Python PATH 缺失）

## 调研：TexLite / Oleafly 轻量本地实时编辑方案（2026-08-28）

用户指示调研"轻量、本地、可预览、实时编辑"开源方案（调 deep-research-ultra），指定 TexLite（SWUFE-DB-Group）与 Oleafly。已 clone 至 `opensource-reference/` 并全量源码分析，报告：`docs/research/2026-08-28-TexLite-Oleafly-轻量实时编辑调研.md`。

### 核心结论
- **TexLite v0.8.1（AGPL-3.0，Node24+Fastify+SQLite+React+CodeMirror6+Yjs+pdfjs）**：轻量 Web 工作区，**默认引擎 xelatex**；编译队列+快照隔离+增量缓存+SyncTeX+Yjs 协同+37 测试——**就是阶段 2/3 现成蓝本**，推荐为主改造对象
  - 方正字体接入：项目 latexmkrc 注入 TEXINPUTS（零改核心）
  - MD 中间态：改 compiler.ts 加转换步骤 + 多产物发布（PDF+DOCX）
  - 编译诊断 `compileDiagnostics.ts` → 包装 harryopo-build-mcp
- **Oleafly v0.3.12（AGPL-3.0-or-later，Tauri+Rust+React+TipTap3）**：本地优先研究工具链桌面应用，无多人实时编辑；EngineDescriptor 能力矩阵/模板 gallery 契约/MCP server（127.0.0.1:5323）/自研 synctex 解析器可借鉴
- **决策**：不采用"自研 ~500 行核心"（重复造轮子），改为基于 TexLite 改造（阶段 2 MVP）；Oleafly 作设计蓝本

### 前置条件
- 需 Node ≥24；**xelatex/latexmk 当前环境缺失**（与模板注册表 M1 遗留的环境问题同源，需一并补齐）
- AGPL 合规：内部自用无碍，商业化分发需评估

## 环境补齐 + TexLite 部署（2026-08-28）

用户选择开源方案（TinyTeX，Oleafly 同款）替代完整 TeX Live，落地 TexLite 本地预览（阶段 2 MVP）。

### TinyTeX（D:\Tools\TinyTeX\TinyTeX，TeX Live 2026）
- 下载：GitHub releases `TinyTeX-1-windows-v2026.08.exe`（73MB，实为 7-Zip SFX，用 `-y -o<dir>` 解压，非 `--auto-install`）
- tlmgr：先 `update --self` 再 install（否则报"please update tlmgr"）；清华镜像 `tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet`
- 宏包：ctex fandol zhnumber xecjk unicode-math fontspec dblfloatfix flushend algorithm2e booktabs tabularx multirow longtable array caption subcaption float titlesec tocloft appendix fancyhdr hyperref cleveref tikz pgf listings enumitem marginfix mdframed framed adjustbox changepage marginnote 等
- bin 加入用户 PATH（永久）

### harryopo-base.sty 修复
- 补 `\usetikzlibrary{positioning}`：`\node[below=0.6cm of B]` 相对定位语法在 TinyTeX/TeX Live 2026 下报 `PGF Math Error: Unknown operator 'of'`

### TexLite v0.8.1（opensource-reference/TexLite）
- npm ci 踩坑：better-sqlite3 原生模块需 `better_sqlite3_binary_host_mirror=https://registry.npmmirror.com/-/binary/better-sqlite3` + `disturl` 写入 `~/.npmrc`（npm 11 拒绝 config set 未知项）；`npm install-scripts approve better-sqlite3 esbuild` + `npm rebuild`（npm 11 install-scripts 保护）
- 配置：`texlite.config.json`（dataDir=output/texlite-data，latexmk 指 TinyTeX 绝对路径）；PowerShell ConvertTo-Json 写文件带 BOM → Node JSON.parse 失败，改用 Python `json.dump`
- init 需 PATH 含 pdflatex/xelatex/lualatex；`TEXLITE_INIT_*` 环境变量非交互建管理员
- 启动：`npm start` → http://127.0.0.1:3000（health: `/api/health`）
- API：登录/创建项目/upload(multipart, directory 参数)/PATCH(settings)/compile/compile/latest(latestRun.status)/pdf

### 方正字体接入（项目自包含，8/8 验证全绿）
- **关键坑**：harryopo 全部字体 `Path=../fonts/` 相对编译 cwd；build.ps1 cwd=templates/report 命中，TexLite 快照 cwd=项目根不命中；OPENTYPEFONTS 对显式 Path 无效
- 解法：`prepare_harryopo_project.py` 生成自包含项目（修正副本 cls/sty `Path=../fonts/`→`Path=fonts/` + fonts/ 19 字体 + 示例 tex），上传快照即完整
- 端到端：上传 22 文件 → 编译 succeeded → PDF 235KB（与 build.ps1 240KB 一致）
- 验证脚本：`output/registry-verify/prepare_harryopo_project.py` + `texlite_e2e.py`

### 下一步
- ⬜ TexLite × harryopo MD 中间态改造（compiler.ts 编译前置 MD→LaTeX + 多产物发布）
- ⬜ 模板注册表内置模板 → TexLite 模板 gallery（借鉴 Oleafly template.json 契约）

## TexLite × harryopo MD 中间态改造（2026-08-28 完成，8/8 全绿）

TexLite 原生支持 `.md` 主文档（调研报告方案 B 落地，阶段 2 收尾）。

### 改动（TexLite 源码，opensource-reference/TexLite）
1. **config.ts**：新增 `md` 配置段（`md.convertScript` 指向 harryopo convert.py、`md.pythonBinary`、`md.convertType`，默认关闭），校验脚本存在
2. **compiler.ts compileProject**：mainFile 校验放宽 .tex/.md；**反向检测**同名 `.md` 存在于快照（compileMainFile 已把 .md 规范化 .tex）→ 在**缓存源目录**内调 convert.py 转 .tex → latexmk 编译
3. **compileArtifacts.ts compileMainFile**：`.md` 返回同名 `.tex`（不校验存在性/documentclass）
4. **projects.ts PATCH**：mainFile 允许 .md/.markdown，md 跳过 documentclass 候选校验（需 mdConvertScript 配置）
5. **projectFiles.ts**：重命名保护放宽 .tex/.md/.markdown

### 关键踩坑
- **转换产物必须写缓存源目录（cache.sourceDir）而非快照**：prepareCompileCache 只同步 snapshot.files 清单，快照内新增的 .tex 不会被同步 → latexmk 找不到。转换时机在 prepareCompileCache 之后、spawn 之前
- **compileMainFile 提前规范化**：routes 层把 .md→.tex 后 compileProject 拿不到原始 .md，需反向检测（快照里同名 .md 存在即视为 MD 项目）
- **harryopo-paper.cls 也需修正副本**：prepare_harryopo_project.py 只做了 report，MD 默认 convertType=paper 需要 paper.cls
- **上传后缀大小写**：方正字体 `.TTF` 大写，e2e 上传过滤需 `suffix.lower()`
- **algorithm2e 依赖 ifoddpage**：TinyTeX 需 tlmgr install ifoddpage relsize

### 验证
- `texlite_md_e2e.py`：PATCH mainFile=note.md → 编译内部 MD→LaTeX 转换 → xelatex → PDF 30KB，8/8 全绿

### 下一步
- ⬜ 模板注册表内置模板 → TexLite 模板 gallery（借鉴 Oleafly template.json 契约）
- ⬜ docling 接入、harryopo-build-mcp、Web 可视化编辑器（阶段 3）

## harryopo 模板 gallery → TexLite 入库（2026-08-28 完成，3/3 编译通过）

借鉴 Oleafly 模板契约（template.json + 自包含目录 + main.tex），模板注册表与 TexLite 打通。

### 契约（template.json，Oleafly 风格）
```json
{ "id": "harryopo-report", "name": "harryopo 报告模板", "category": "报告",
  "description": "...", "main_doc": "main.tex", "engine": "xelatex",
  "layout": "single-column", "pages": "multi", "default_color": "#0c8599",
  "license": {...}, "requires": {"packages": [...], "fonts": [...]}, "order": 10 }
```

### 入库流程（texlite_seed_templates.py）
1. 打包自包含项目目录（修正副本 cls/sty `Path=../fonts/`→`fonts/` + fonts/ + main.tex 精简示例 + template.json）→ output/texlite-gallery/<id>/
2. **ZIP import 原子导入**（POST /api/projects/import）→ 自动检测 mainFile
3. PATCH engine=xelatex → 编译验证

### 模板（全部编译 succeeded）
- harryopo-paper（精简示例 33KB）· harryopo-report（showcase 235KB/15 页）· harryopo-notes（精简示例 47KB）

### 关键踩坑
- **逐文件 upload/PUT 覆盖默认 main.tex 有竞态**（项目创建后 Yjs room 初始化与连续上传冲突，覆盖不生效）→ 用 ZIP import 原子替换最可靠
- **GET /api/projects 返回顺序非创建顺序**：取"最新"项目需按 createdAt/created_at 排序，不能依赖数组顺序
- **TexLite latexmk 带 `-halt-on-error`**：非致命错误（如 example-note.tex 的 Undefined control sequence）会导致编译判失败（本地直接 xelatex 可继续）→ 模板示例必须零错误
- **showcase-paper.tex 在 TinyTeX 有 `\mathbf` 兼容问题**（完整 TeX Live 未暴露）→ gallery 用精简示例
- **mathnotes 依赖 extsizes/colortbl/zref**（TinyTeX 需 tlmgr 补装）

### 下一步
- ⬜ docling 接入、harryopo-build-mcp、Web 可视化编辑器（阶段 3）

## preview.png 自动生成（2026-08-28 完成，15/15）

`texlite_preview_gen.py`：PyMuPDF（`import pymupdf`，fitz API 已 deprecated）渲染 PDF 首页（dpi=100）→ preview.png（paper 45KB / report 32KB / notes 20KB）；更新 template.json `preview` 字段并上传 TexLite 最新项目。模板 gallery 契约与 Oleafly 完整对齐（id/name/category/description/main_doc/engine/preview）。

### 下一步
- ⬜ docling 接入、harryopo-build-mcp、Web 可视化编辑器（阶段 3）

## 阶段 3 Web 可视化编辑器方案（2026-08-28 调研完成）

方案书：`docs/plans/2026-08-28-stage3-web-editor.md`。调研（Oleafly wysiwyg 源码深析 + tiptap-markdown-react clone 分析 + 2026 竞品对比）。

### 技术选型（已定）
- **TipTap 3**（ProseMirror）+ `@tiptap/markdown`（开源双向）+ `@tiptap/extension-mathematics`（官方公式）+ KaTeX + 自研 RawBlock/RawInline 兜底
- **不采用**：@tiptap-pro（商业 Start plan）；Milkdown（备选，插件门槛高）
- 定位：办公文档（MD 中间态）可视化编辑面，与 TexLite（LaTeX 源码）并存

### 关键机制（借鉴 Oleafly，源码实证）
- **RawBlock/RawInline**：atom 节点 + attrs.source，未识别结构原样保真（呼应"AI 只产结构化数据"铁律）
- **math token 占位保护**（protectInlineSources/restore）：防解析器破坏 $ 定界符
- **preamble/body 分离**（splitLatexDocument）：preamble 收进 textarea
- **round-trip 幂等测试**：serialize(parse(serialize(parse(x)))) === serialize(parse(x))
- **AI 写并发模型**：generation 计数 + 二次校验；isolateHistory 不进 undo
- **diff 全套 @codemirror/merge**（unified/MergeView/审批卡）

### tiptap-markdown-react 参考
- `@tiptap/markdown` MarkdownManager 双向；extension-mathematics + KaTeX；CitationRef.ts 展示自定义节点 renderMarkdown/markdownTokenizer 范式（harryopo 扩展公式/表格/注释的方法）

### 路线图
- M1 MVP：Vite+React+TipTap 脚手架、MD 双向、公式/表格/图片、预览、导出 office.py、round-trip 测试
- M2：模板注册表 schema 表单、文件树、图表渲染
- M3：Yjs 协同 + @codemirror/merge inline diff + AI 流式插入

### 下一步
- ⬜ M1 脚手架实施（用户确认后）

## 阶段 3 M1：harryopo-web 可视化编辑器 MVP（2026-08-28 完成）

方案书落地。`web-editor/`（Vite + React 19 + TipTap 3.30 + @tiptap/markdown + extension-mathematics + KaTeX + RawBlock/RawInline + Express 后端）。

### 交付
- `src/lib/math.ts`：harryopo 公式定制——单行 `$$...$$`=块级（官方 BlockMath 只认多行）、`$...$`=行内，markdownTokenizer/renderMarkdown 双向
- `src/lib/raw.tsx`：RawBlock/RawInline（Oleafly 模式：atom + attrs.source 原样保真）
- `src/lib/md.ts` + extensions.ts：MarkdownManager parse/serialize 双向 + round-trip 幂等
- `server/index.js`：Express :8080（docs 列表/加载/保存/导出调 office.py render）
- 前端：编辑（TipTap + 工具栏）/预览（markdown-it + KaTeX）/导出按钮

### 验证
- round-trip 幂等测试 8/8 ✓（公式单行/多行/行内、表格、标题、引用、图片）
- 构建通过；API 端到端 8/8 ✓（Word 导出 35KB docx 可下载）
- 运行：node server/index.js（:8080）+ npm run dev（:5173，proxy /api）

### 关键踩坑
- **oxc 对 .ts 文件含 JSX 报解析错误**：含 JSX 的源文件必须 .tsx（vite 7 默认 oxc，tsc 不报但 vite transform 报）
- **@tiptap/extension-table 等 v3 是命名导出**（`import { Table } from ...`），默认导出 undefined
- **renderMarkdown 签名是直接传 node**（`renderMarkdown(node)`），不是 `{ node }` 解构（官方/tiptap-markdown-react 实证）
- **MarkdownManager 可服务端 parse/serialize**（`new MarkdownManager({ extensions })`），round-trip 测试基础
- **office.py paper 链路在部分终端环境失败**（xelatex spawn 环境差异，Word 链路正常）——web-editor 导出以 word 为主验证；paper 链路属 office.py 既有问题待查

### 下一步
- ⬜ 阶段 3 M2：模板注册表 schema 表单 + 文件树 + 图表渲染
- ⬜ 阶段 3 M3：Yjs 协同 + @codemirror/merge inline diff + AI 流式插入
- ⬜ office.py paper 链路环境问题排查

## 阶段 3 M2：文件树 + 模板表单 + 图表（2026-08-28 完成，13/13）

web-editor 升级。

### 交付
- **文件树**：`/api/tree`（递归目录）+ 新建/删除 + `safeRel` 安全路径（防 `..` 穿越）；前端 FileTree 组件（子目录展开/选中高亮/删除）
- **模板注册表对接**：`/api/templates`（读 manifest.json）+ `/api/templates/:id/schema` + `/api/templates/:id/render`（调 docx_template.py render → docx 下载）；前端 TemplateModal（模板列表 → schema 动态表单 string/object/array → 渲染下载）
- **图表**：Preview 集成 mermaid（前端渲染 ```mermaid 代码块）+ `/api/diagram` 后端 super-diagram 接口
- 生产模式：后端 express.static(dist) → http://127.0.0.1:8080 直接访问 M2 版前端

### 关键踩坑
- **重复路由拦截**：追加的 GET/PUT /api/doc 被 M1 旧版（只认 name）先命中 → path 参数被忽略 → 404。修复：删重复路由、扩展 M1 版支持 path
- **Express 路由按注册顺序匹配**，同名路由只有第一个生效
- **docx_template 校验把空字符串当缺失**：表单必填字段必须给非空值

### 下一步
- ⬜ 阶段 3 M3：Yjs 协同 + @codemirror/merge inline diff + AI 流式插入
- ⬜ office.py paper 链路环境问题排查

## 2026-08-29：diagram-design 内嵌 + 文档生成主流程固化 + 图表四问题修复

### 1. diagram-design 编辑级图表 skill 内嵌 harryopo-office
- 来源：cathrynlavery/diagram-design（39 类型 × 3 变体：极简亮/暗/全编辑），clone 于 `opensource-reference/diagram-design/`；源码分析报告 `docs/research/2026-08-29-diagram-design-analysis.md`
- 安装：`.trae/skills/harryopo-office/skills/diagram-design/`（209 文件）；新增 `scripts/diagram_design_render.py`（HTML→PNG：`--svg` playwright 仅截 SVG 区域、`--check` 自检）+ `office.py diagram` 子命令（REMAINDER 透传）
- 范式：规范驱动（AI 按规范手写 HTML/SVG，脚本只负责渲染）；4px 网格 + 6 连接器规则 + 焦点色≤2 + 密度 4/10；生成 HTML 必须补中文字体 fallback（Microsoft YaHei）；渲染 PNG 依赖 playwright chromium

### 2. SKILL.md 固化"文档生成主流程"
①AI 产出 MD 中间态 → ②用户预览确认内容 → ③AI 智能分析适合配图则提问（多类型给选择，禁止擅自生成）→ ④diagram-design 生成→PNG→self_check→用户审核 → ⑤智能插入（图注 `![图N：xxx]` + `> 注：` 注释，图紧跟引用段落）→ ⑥office.py render → Word/LaTeX（可选 --template）。验证：flow-doc.md → docx 181KB / paper PDF 223KB。

### 3. 图表/参考文献四问题修复（convert.py / word_template_engine.py / harryopo-base.sty）
| 问题 | 根因 | 修复 |
|------|------|------|
| 图注重复"图1图1" | convert.py caption 保留 alt 的"图1："前缀 + LaTeX 自动编号 | `_strip_caption_num()` 去 `^(图\|表\|式)\s*\d+[：:...]` 前缀 |
| caption 黑体不居中 | base.sty `\captionsetup{labelfont=bf,format=hang}` | `{\fzkt}` 楷体 + `justification=centering` + 全角冒号分隔符 |
| 注释位置/字体/序号 | convert.py figure 分支不消费注、Word 注释无字体控制 | figure 后 `> 注：` → `{\fzkt\footnotesize}`；add_annotation 加 font_key='heading3' |
| 参考文献 [1] 重复 | `\bibitem{refN} [1] xxx` 保留字面 [1] | 去 `^\[\d+\]\s*` 前缀 |

顺带修复：表标题正则 `^表` 不匹配 `**` 开头（改 `^\*{0,2}表`）；BLOCK_QUOTE 前块为 TABLE/FIGURE 且以注开头则跳过（for 循环 enumerate 固化的 i+=1 无效导致注释渲染两次）。验证 fix-test.md：PDF 文本"图1: 系统架构示意""表1: 组件职责说明""[1] 智能体系统设计实践"各一次，嵌入 FZKTJW 楷体。

### 4. 其他今日落地（详见记忆系统 project_memory.md #40-58）
- office.py `_find_project_root()` 漏跳 `.trae` 复发修复（修通用问题必须 grep 全部模块）
- paper 链路 xelatex 失败根因 = PATH 快照过期 → `_ensure_tex_on_path()` 探测 prepend（幂等）
- 公式乱码标准解法：latex2mathml + Office MML2OMML.XSL（坑：XSLT 根元素可能就是 m:oMath）
- 行内公式 `$...$` 补全（_add_inline_runs，表格单元格同走）
- 表格注释统一"下方" + Word 三线表
- 网页方案废弃（TexLite/web-editor 清理）→ IDE LaTeX Workshop 10.13.1 实时编译预览（settings.json latexmk xelatex + TEXINPUTS）
- 流程图"改良坏"根因分析（形状语言/装饰元素/语义色三要素）+ 方案 A yaml2ir 转原版 IR
- flowchart-generator mono 黑白灰主题（强制忽略 YAML 彩色覆盖）

## 2026-08-29：示例文档整理 + 双链路修复 + templates 清理

用户要求：整理 `harryopo-office/templates`，用最新 skill 生成示例文档，"有问题的修复，不要的删去"。

### 1. 环境卡点解决：flushend.sty（双栏末页栏平衡）
- **现象**：双栏示例 `! LaTeX Error: File 'flushend.sty' not found.`；tlmgr install sttools 后报 `Missing \begin{document}`
- **根因**：清华 tlnet 镜像的 sttools 下载返回 404 HTML 页面被 tlmgr 当包内容写入 `texmf-dist/tex/latex/flushend/flushend.sty`（内容为 `<html><head><title>404...`），LaTeX 加载"sty"时把 `<html>` 当 LaTeX 命令 → Runaway/Missing begin
- **正确来源**：`https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/archive/sttools.tar.xz`（12916B，含 tex/latex/sttools/flushend.sty v4.3）
- **修复**：TinyTeX 目录受 shell 权限保护无法直接覆盖 → **项目自包含**：flushend.sty 放入 `templates/cls/`（TEXINPUTS 前缀目录优先于 texmf-dist 命中），skill 内嵌 templates/cls 同步一份

### 2. 静默数据丢失 bug：parse_inline 不转义特殊字符（严重）
- **现象**：双栏 `Runaway argument ... \abstractcontent{随着...32%...`；showcase 摘要"92.3% 的分割准确率"**被静默截断**（`%` 注释到行尾吞掉内容），PDF 看着"编译成功"实为缺字
- **根因**：`_escape_latex()` 定义了但**从未被调用**；`parse_inline()` 只做 markdown 语法转换不转义 `&%$#_~{}^`。正文/摘要/关键词里的 `%` 直接进 LaTeX → 注释符吞行
- **修复**：parse_inline 在公式保护后、链接/代码/粗斜体转换**之前**调用 `_escape_latex()`（顺序关键：`_escape_latex` 会转义 `{}`，必须在生成 `\href{}` 等命令前执行，否则破坏命令结构；公式已保护为占位符不受影响）

### 3. 双链路同步修复
- **convert.py**：`\abstractcontent{}`/`\keywordscontent{}`/`\begin{abstract}`/`\keywords{}` 全部经 `parse_inline()` 转义；BLOCK_QUOTE meta 跳过正则 `^副标题` → `^(副标题|作者|单位|学校|日期)`（作者/单位/日期 blockquote 不再渲染进正文）；入口剥离 HTML 注释 `<!--[\s\S]*?-->`
- **office.py**：render_notes pandoc 缺失时回退 `md2latex.py --engine python`（纯 Python 引擎，无外部依赖）
- **report-showcase.md**：旧 `> **摘 要**` blockquote → `**摘要：**` 段落；`<h1 class="chapter">` → `# 第X章`（共 5 处）；删手工目录（report 类型自动 `\tableofcontents`）；伪 mermaid（ASCII 箭头）→ 合法 flowchart TD

### 4. templates 清理（skill 内嵌 + 项目根）
- **skill 内嵌**：paper/ 删除 demo-e2e/final-test/fzht-test/公文模板tmp/mermaid-test/showcase/example-paper 全部 pdf/tex/aux/log/out；report/ 清空删除；math-notes 删除 e2e 残留 + mermaid 示例图；补全 math-notes（md2latex.py/ps1、build.ps1、README.md、example-note.md、fonts/ 10 字体）；cls/ 补 flushend.sty
- **项目根**：templates/paper 删 demo-paper + 6 个 e2e；report/ 删 demo-report；math-notes 删 main.pdf/tex（保留官方 example-note.pdf）

### 5. 示例产物（output/examples/，5+1 全绿）
| 示例 | Word | PDF | 说明 |
|------|------|-----|------|
| paper-single-column | 36KB | 148KB | 论文单栏 |
| paper-twocolumn | 36KB | 164KB | 论文双栏（flushend 修复后） |
| paper-showcase | 41KB | 196KB | 论文全特性（摘要不再截断） |
| report | 42KB | 213KB | 报告章节式（--type report） |
| report-showcase | 85KB | 363KB | 报告全特性 + mermaid（--type report） |
| example-note | — | 105KB | math-notes（python 回退引擎） |

- 产物命名：`{stem}-word.docx` / `{stem}-paper.pdf`（report 类型 PDF 名固定 `-paper.pdf`，tex 为 `-report.tex`）
- 两个 README：`templates/previews/README.md`（示例清单 + 生成命令 + 元信息约定 + 修复点）、`output/examples/README.md`（产物说明）
- SKILL.md 架构树同步更新（previews/ + flushend.sty + math-notes 补全）

### 6. 经验沉淀
- **tlmgr 装出的坏文件排查**：LaTeX 加载 .sty 报奇怪错误（Runaway/Missing \begin{document}）时，先 `Get-Content <sty> -TotalCount 2` 看是否 404 HTML 污染
- **`%` 静默截断是隐形杀手**：`%` 注释到行尾，编译"成功"但内容缺失；凡含百分比的文档必须验证摘要/正文完整
- **parse_inline 转义顺序铁律**：公式保护 → 特殊字符转义 → markdown 语法转换 → 恢复公式（`_escape_latex` 转义 `{}`，不能在 `\href{}` 生成后执行）
- **并行 Edit 同一文件有竞态**：一次消息内多个 Edit 修改同一文件可能丢失其中一处（本次第三章标题 Edit 丢失），关键修改应串行执行
- **Edit 工具与 shell 权限**：D:\Tools（TinyTeX）不在 shell 写入白名单 → 项目自包含（flushend.sty 放 TEXINPUTS 前缀目录）是最优雅解法

---

## 2026-08-30：第三轮增量调研 + 方案书 v3（阶段 3 重定义）

### 1. 增量调研（40+ 新项目核验，报告 `docs/research/2026-08-30-开源方案增量调研-文档MCP与生成转换生态.md`）
- **生态信号 1**：2026 夏季 Word 工具主战场从"创建"转向"修订/审阅"（word-mcp-live 198★/docx-mcp/docx npm 9.7 图片级修订/Python-Redlines 全部主打 tracked changes）
- **生态信号 2**：微软官方 Word MCP 只做云侧（OneDrive/Graph），本机 COM 空档由社区填补——验证我们 Windows+COM 路线差异化正确
- **生态信号 3**：解析端走"0.9-1B 专用小模型 + Rust 快速核"（PaddleOCR-VL-1.5 94.5%、kreuzberg/office_oxide），我们的四级路由架构不变、候补按需插入
- 关键发现：Python-Redlines（MIT，docx→原生修订红线稿，免 Word）；markitdown v0.1.7 修复 omml 公式 bug；docx-preview（2.1k★，浏览器核对 docx）；kreuzberg v4（唯一覆盖 .doc/.xls/.ppt 老格式）；中文公文生成开源界仍是空白（仅可校准 GB/T 9704 参数：三号仿宋 16pt/28 磅/37-35-28-26mm 页边距）

### 2. 方案书 v3（`docs/plans/2026-08-30-office-super-skill-v3.md`，v2 已加取代指针）
- **阶段 3 重定义**（web-editor 废弃后）：MD 确认=VS Code 预览+方正 CSS；LaTeX=LaTeX Workshop；docx 核对=docx-preview 静态 HTML；权威=Word COM 出 PDF；改稿对比=Python-Redlines 红线稿
- **修订审阅升级 P0**：Python-Redlines（MVP：生成版 vs 用户修改版 diff 出红线稿）→ 二稿带修订记录（蓝本 docx npm 9.7 w:ins/w:del）→ 进阶 word-mcp-live COM 实时修订会话（适配器封装）
- **PPT/Excel 正式立项**：COM 路线参考 dosev-ai/mcp-office（Output Contract 机器可验证输出规格范式优先移植）、ykuwai/ppt-mcp
- **P0 三项**：①markitdown≥0.1.7+MinerU 3.4.5 升级 ②Python-Redlines 接入 ③docx-preview 核对页

### 3. Hold 清单（许可）
- AGPL 传染：SuperDoc/pullmd/O2OA；许可缺失或不透明：kimi-skills/ComPDFKit/OfficeDoc；非商业仅可参考规则：docformat-gui（PolyForm）

### 4. 2026-08-30 补充：示例按主流程重生成 + 图表静默降级修复
- 示例问题根因：8/29 深夜重生成时未走主流程图表环节（paper/report-showcase 架构图是 ASCII 字符画、全文零图注）；super-diagram 渲染失败因 playwright 装在别的解释器（本机默认 python=D:\Miniconda3，缺 python-docx/latex2mathml/pywin32/playwright，已补齐；chromium 走 npmmirror 镜像）
- **静默降级 bug 修复（office.py 图表预处理）**：图表块渲染失败原先打印"[OK] 渲染了 N 个图表"继续编译 → JSON 源码进 PDF；已改为统计失败数，>0 即 sys.exit(1) 硬失败。教训：**管线失败宁可中断不可静默降级**
- paper-showcase：ASCII 架构图 → super-diagram 契约（三层 B/S）；report-showcase：ASCII 四层图 → super-diagram（10 边，中间两"调度"标签有轻微堆叠可接受）+ 用户画像表加表注；两示例双链路重渲染全绿（paper PDF 291KB / report PDF 475KB / Word 141KB/195KB）
- 图表微调经验：横条→多个子节点的边若出口拥挤，**加宽画布 + 拉开节点间距**让端口扇出分散（中间节点边仍可能标签堆叠，属 render_v2 已知限制）
- .gitignore 调整：output/* + !output/examples/（官方示例产物入库展示）

---

## 2026-08-30：全库隐私脱敏 + git 历史重写 + 完整安全扫描

### 隐私清除（用户要求，两层三处全清）
- 污染面：28 个文本文件 + 2 个 docx（公文模板/知行读书，zip 内 XML 脱敏）+ 8 个 PDF 产物 + 简历目录 + math-notes main.pdf + 4 个 tmp-e2e PDF
- 替换映射：张子涵→张三、陈子航→李四、2503010345→2025000101、2503020108→2025000102、25计算机应用技术3-3班→计算机应用技术专业、深圳信息职业技术大学→示例大学
- 产物重生成：examples 三示例重渲染、蒸馏区参赛模板 PDF 用 pwsh（非 powershell 5.1，UTF-8 编码问题）跑 build.ps1 重编译（27 页）
- **git filter-repo 两轮**：①--replace-text（6 字符串映射全文本 blob）+ --invert-paths（蒸馏区 e2e-test/distill-images/两个 docx/参赛 PDF/output/examples 整目录）；②补漏（简历、templates/math-notes/main.pdf、glob *tmp-e2e.pdf）。验证：pickaxe -S 六个字符串全 0；force push 两次覆盖远程
- **filter-repo 大坑**：--invert-paths 会把文件从工作区一并删除（包括刚脱敏的版本）→ 需从 origin 旧历史恢复再重新脱敏提交；每次运行都会删除 origin remote 配置需重新 add
- **pickaxe 验证注意**：fetch origin 后 --all 包含 origin/main 旧引用会误报，须先 force push 再验 origin/main
- bash 双引号内 `~$xxx` 的 $r 会被变量展开导致 rm 删不掉 Word 锁文件，用单引号
- build.ps1 必须用 pwsh 7 跑（UTF-8），powershell 5.1 按 GBK 解析中文注释报语法错误

### Mimosa deep 扫描（scan-2026-08-30T05-58-12.774Z，seal sha256:c4a78b0c...）
- 69 findings，**自研代码（harryopo-office skill / shared / templates）零发现**
- 分布：opensource-reference 参考仓库（anydoc/fireworks-tech-graph/Oleafly/diagram-design）与 output 生成产物——均不入库（.gitignore 已排除），风险不随仓库传播
- 蒸馏区 convert.py/distill-docx.py 的"路径穿越"为本地 CLI 接受 ../ 路径的常规模式，无网络暴露，低风险
- 依赖：1120 包扫描，3 包命中 6 条离线 advisory；run status inconclusive（静态分析覆盖声明）

---

## 2026-08-30：全面代码审查 + 全量修复（17 项）

用户要求对 harryopo-office skill 做流程/代码/稳定性/输出真实性全面审查。实测驱动（output/review-test/ 样例），发现 3 严重 + 6 中等 + 8 轻微问题，全部修复并回归全绿。

### 严重问题（已修复）
1. **未闭合 `$$` 静默吞全文**（md_to_word.py）：多行公式收集到 EOF 未闭合 → 后续章节/参考文献全丢无报错。修复：抛 ValueError 带行号，CLI 层转 [ERROR] exit 1。与 `%` 截断同类的隐形杀手，实测验证
2. **COM 异常 taskkill 杀全部 Word**（word_template_engine.py 两处）：失败分支 `taskkill /f /im WINWORD.EXE` 会杀用户未保存文档 → 删除，只留警告
3. **subprocess 无 encoding 中文崩溃**（office.py 5 处 + diagram_render + mermaid_render）：Windows GBK 默认解码子进程输出 → UnicodeDecodeError，错误详情丢失（实测 `[WARN] 渲染失败:` 后空白）。统一 `encoding='utf-8', errors='replace'`

### 中等问题（已修复）
4. 产物命名污染：图表预处理临时文件 `*.processed.md` 的 stem 泄漏进产物名 → 三渲染函数加 `out_stem` 参数，cmd_render 预处理前记录 `base_stem`
5. xelatex 2 遍 → 3 遍（paper/notes 均改，与 build.ps1 对齐）
6. `_ensure_pandoc_on_path()` 新增（探测 %LOCALAPPDATA%\Pandoc 等，与 TeX 探测同源）
7. **md2latex.py 纯 Python 回退引擎五缺陷**：①表格分隔行检测正则永假（`'|'.join` 后匹配 `^[\s:\-]+$` 含 `|` 必败）→ 逐单元格 fullmatch；②正文 `%`/`&`/`#`/`_` 未转义 → 转义顺序铁律（公式保护→URL 保护→转义→语法转换）；③图片变非法 `!\href` → 独立行图 → figure 环境 + 行内 → \includegraphics；④标题只认 YAML frontmatter → `_extract_harryopo_meta` 提取 `# ` 主标题/`> 作者：`/`> 日期：`；⑤verbatim 双重转义 → 原样写入
8. docx_clean.extract_docx_tables python-docx 缺失静默返回空表 → 改抛 ImportError，office.py 捕获硬失败

### 轻微问题（已修复）
9. convert.py 链接 URL `%20` 被转义破坏 \href → URL 占位符保护（转义前抽出，生成 \href 时还原）；实测 `\href{...docs%20v2}` 正确
10. convert.py `code_escaped` 死代码 ×2 删除（lstlisting verbatim 语义）
11. **列表支持补齐**：convert.py 嵌套列表（解析器允许缩进 + `_render_nested_list` 按 2 空格层级开关 itemize/enumerate，paper/report 两处）；md_to_word.py **从零补列表**（此前 `- item` 当正文渲染出字面 "- "）：`add_list_item` 引擎 API + 解析（•/◦ 层级、有序保留编号）
12. tex2md.py `\textbf{a{b}c}` 嵌套花括号切坏 → 平衡括号扫描器 `_strip_braced_cmd`（深度计数，迭代至不动点，未闭合保留原文）
13. diagram_render.py 硬编码 `c:\Users\Lenovo\` 删除
14. office.py cmd_texlite 死代码删除（引用已废弃脚本且未注册）
15. docstring SyntaxWarning ×3 修复（raw docstring）

### SKILL.md 流程升级
- **新增 ⑤ 图描述确认环节**（用户要求）：图表类型选定后，AI 先产出**图描述 MD**（图类型/节点清单表格/连线关系/布局意图）→ 用户确认 → 才写 HTML。主流程 ④→⑧ 重编号；图表章节插入第 3 步（含示例模板）+ 硬约束"图描述未确认不得写 HTML"
- 表标题位置澄清：实测 Word/LaTeX 两链路**都渲染在表格下方**（一致），MD 写法在表格上方——修 SKILL.md 描述（原"表格上方"误导）
- 约定表补列表行 + MD→LaTeX 映射表列表行更新为嵌套

### 环境补齐
- Anaconda 3.13 装 markitdown 0.1.7（恰为 P0 升级目标版本）+ firecrawl-anydoc + docxtpl（`python -m pip`，注意裸 `pip` 可能指向别的环境）
- **pandoc 3.11 winget 安装**（notes 链路主引擎；`_ensure_pandoc_on_path` 解决新装后终端 PATH 快照过期）

### 回归结果（全绿）
- 三链路：word 33KB / paper 89KB / notes 112KB（notes 从失败→成功）
- Word 产物：3 OMML 公式、方正四字体、列表 3+2 嵌套、三线表、图注表注、链接
- paper tex：itemize 2/2 + enumerate 1/1 平衡、\href %20 保持
- 纯 Python 引擎 9/9 检查项通过
- 故障路径：未闭合 $$ → [ERROR]+exit 1；坏图 → exit 1 + 中文错误详情完整（编码修复生效）
- 产物命名：`review-diagram-word.docx`（.processed 不再泄漏）

### 经验沉淀
- **审查先实测再下结论**：表标题位置最初判断"两链路不一致"，实测 docx body 元素顺序后发现一致——段落文本序列不含表格，会误判相对位置
- **fail-fast 检查清单**：未闭合定界符（$$/```/环境）、静默返回空集合、异常分支里的破坏性操作（杀进程/删文件）、子进程编码——这四类是本项目反复出现的隐形杀手
- **heredoc 传 Python 检查脚本不可靠**：反斜杠/引号会被 shell 层失真，断言脚本写成 .py 文件跑
- **re 替换串陷阱**：`r'...\linewidth...'` 中 `\l` 是非法转义，替换串的字面反斜杠要 `\\`
- **pip vs python -m pip**：多 Python 环境（Miniconda/系统/3.14）并存时裸 pip 不可信，一律 `python -m pip`

---

## 2026-08-31：图表引擎内嵌 + ASCII 字符画拦截（"其他 AI 画图不生效"根治）

### 用户痛点
其他 AI 调用本 skill 时图表能力不生效，配图以 MD 里的 ASCII 字符画形式出现（8/29 示例问题同根复发）。

### 根因（三查）
1. **super-diagram 未内嵌**：`diagram_render.py` 只探测 `~/.trae-cn/skills/super-diagram/`（Trae 全局目录）——其他 AI 平台/其他机器没有该路径，架构图引擎直接不可用
2. **无"禁止 ASCII 字符画"约束**：SKILL.md 没有铁律，AI 画不了图就降级画字符画，管线不拦截直接进文档
3. diagram-design 已内嵌 ✓，但 super-diagram 依赖链断裂使"三引擎"实际只有两条可用

### 修复
1. **super-diagram 内嵌**（878K）：`skills/super-diagram/`（SKILL.md 契约 + scripts/render_v2.py + testdata/ 样例；unified.py 旧脚本与 output/ 不嵌）。render_v2.py 纯标准库 + playwright，质量校验库探测打补丁：硬编码 `d:/ai/latex` 删除 → 从 `__file__` 向上找 `shared/diagram_geometry.py`（跳 `.trae`，与 office.py `_find_project_root` 同理）
2. **探测顺序**（diagram_render.py）：环境变量 `SUPER_DIAGRAM_SCRIPT` → **内嵌副本** → 全局 `~/.trae-cn`；实测命中内嵌
3. **ASCII 拦截双层**：
   - SKILL.md 硬约束："禁止 ASCII 字符画——任何图必走三引擎之一渲染 PNG，画不了走图描述环节沟通，不许降级"
   - office.py 运行时护栏：非三引擎代码块盒线字符 ≥10 或 `+---+` 框线 ≥3 → `[WARN] 疑似 ASCII 字符画图`（不硬失败——目录树等合法场景防误报）
4. SKILL.md 同步：架构树补 super-diagram【内嵌，自包含】、依赖章节探测顺序说明

### 验证（全绿）
- 内嵌探测命中：`_find_super_script()` → `harryopo-office/skills/super-diagram/scripts/render_v2.py`
- 内嵌独立渲染：testdata/microservice.json → PNG 73KB + 质量校验通过
- 全链路：super-diagram 块 → `[OK] 渲染了 1 个图表` + ASCII 块 → `[WARN] 疑似字符画` 同场触发，Word 生成成功
- 质量校验价值实证：布局过挤的 JSON（canvas 420/节点 y=340）被校验拦下，调整后通过——坏图宁可失败不进文档

### 经验沉淀
- **skill 自包含原则**：凡是管线依赖的外部脚本/引擎必须内嵌进 skill（参考 8/29 diagram-design 内嵌先例），全局目录依赖 = 其他环境必然失效
- **AI 降级行为要用“约束+护栏”双保险**：只写约束（SKILL.md）AI 可能不遵守；只写护栏（代码）覆盖不全；约束定方向、护栏给提醒
- **质量校验拦截是特性不是 bug**：排查时先确认是自己的测试数据布局问题还是引擎问题（单独跑渲染器二分）

---

## 2026-09-02：Word 质量 AI 味修复（text_norm）+ super-diagram 移除

用户反馈三问题：①Word 产物 AI 味浓（英文引号/标点未转中文）；②排版空格多（中英间半角空格透传）；③图表 skill 两个并存（super-diagram 与 diagram-design）。用户决策：空格全删（中英间不留，公文风格）；删内嵌 super-diagram 保留 diagram-design + mermaid 双引擎。

### 1. text_norm.py 护栏层（两引擎共享）
- 标点转换（仅 CJK 上下文）：`, : ; ? !` 前邻 CJK → `，：；？！`；`(`/`)` 按另一侧邻 CJK 转 `（）`；直双引号按开闭配对转 `“”`（段落含 CJK 时）；直单引号仅两侧邻 CJK 才转（`don't` 不动）；数字语境（`10:30`/`1,000`）不动
- 空格删除：任一侧为 CJK 的半角空格全删（含中英/中数之间），`_strip_cjk_spaces` 迭代到不动点
- 保护：围栏代码块/多行公式块（`$$` 单独成行状态机）/行内公式代码/URL（markdown `](...)` 含空格路径 + 裸 http）/行首 markdown 标记（`# > - * + 1.`）→ 占位符机制
- 接入：`md_to_word.py build_document` 入口 + `convert.py convert_md_to_tex`（HTML 注释剥离后）统一 `normalize_markdown()`；SKILL.md 新增“中文标点与空格（输出硬约束）”约束层，双保险

### 2. super-diagram 移除（收敛双引擎）
- 删 `skills/super-diagram/` 内嵌目录（SKILL.md/render_v2.py/testdata 4 个 JSON）
- `diagram_render.py`：删 SUPER_DIAGRAM_CANDIDATES/_find_super_script/render_super_diagram/_extract_title；SUPER_RE 保留仅拦截，render_one 对 super-diagram 块报错返回 False（“引擎已移除，请改用 diagram-design 或 mermaid”）
- `office.py`：ASCII 警告文案“三引擎”→“双引擎”；第 551 行 super-diagram 块检测条件保留（触发报错 → n_fail → sys.exit(1)，与 8/30 fail-fast 修复联动）
- SKILL.md：description/架构树/主流程/引擎表/依赖段全面改双引擎表述
- 示例 MD 连带处理：paper-showcase / report-showcase 含 ```super-diagram 块，引擎移除后重渲染会硬失败 → 改为直接引用已渲染 PNG（figures/super-diagram-00-*.png 已存在）
- C 盘全局 super-diagram 副本不在范围（skill 自包含后不再依赖）

### 3. 验证（全绿）
- text_norm 单测 18/18（含奇数引号兑底/纯英文段/表格/行首标记）
- 双链路产物断言 38/38（test-norm.md：英文标点消失+全角出现+CJK 空格清除+代码/公式/URL 原样，tex 与 docx 双侧）
- 三示例回归：paper-showcase 292KB / report-showcase 475KB（mermaid 1 块渲染 OK）/ paper-twocolumn 157KB，Word+PDF 双格式
- super-diagram 块拦截：EXIT=1 + 明确报错文案

### 踩坑
- URL 保护正则 `\]\([^)\s]*\)` 遇含空格图片路径失效 → 改 `\]\([^)]*\)`（`[^)\s]` 会把路径内空格排除在保护外）
- 断言脚本误报三例：tex `\author{## 一…}` 的空格是行首标记语法空格（应保留）、Word“目 录”是自动目录页固有字距、代码块在 tex 中是 verbatim 无围栏标记
- 删引擎后示例 MD 里的引擎块要同步改写，否则 fail-fast 会拦住回归验证（先 grep 确认 PNG 存在再改引用）


