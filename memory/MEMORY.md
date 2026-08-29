# 项目记忆 — d:\ai\latex

> 最后更新: 2026-08-28 | 版本: 办公超级 Skill 方案 v2（解析端四级路由 + Word→PDF 直出 + LaTeX→Word MD 中间态）

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
