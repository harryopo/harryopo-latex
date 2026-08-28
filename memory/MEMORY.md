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

### 下一步（按方案书 v2 路线图）
- ⬜ 模板注册表 v1（manifest.json）
- ⬜ LaTeX → Word MD 中间态链路（.tex → MD 清洗 → md_to_word）
- ⬜ docling 接入（MinerU 互为兜底）、harryopo-build-mcp、本地预览服务器
