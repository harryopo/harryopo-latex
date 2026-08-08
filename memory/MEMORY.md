# 项目记忆 — d:\ai\latex

> 最后更新: 2026-08-05 | 版本: MinerU 集成 + 加粗→黑体修复 + 端到端验证

---

## 项目定位

harryopo LaTeX 通用模板体系 —— 面向中文场景（学术论文、报告、读书笔记）的专业 LaTeX 模板集合。附带 Trae AI Skill 包，支持一键生成和编译。

---

## 当前文件结构

```
d:\ai\latex\
├── CLAUDE.md                   # Agent 项目规则
├── .learnings/                 # 学习日志
├── memory/MEMORY.md            # 本文件
├── templates/
│   ├── cls/
│   │   ├── harryopo-base.sty   # 共享基础包 v4.2
│   │   ├── harryopo-paper.cls  # 论文文档类 v4.0
│   │   └── harryopo-report.cls # 报告文档类 v4.0
│   ├── fonts/                  # 18个内嵌字体（方正+XITS+TeX Gyre Heros）
│   ├── paper/
│   │   ├── showcase-paper.tex/pdf     # 单栏论文示例
│   │   └── example-paper-twocolumn.tex/pdf  # 双栏论文示例
│   ├── report/
│   │   └── showcase-report.tex/pdf    # 报告示例
│   └── build.ps1               # 编译脚本 v4.2
├── 参考资料/中文book/          # kaobook 中文书籍（独立体系）
└── .trae/skills/
    └── harryopo-latex/         # 统一 Skill（模板 + 转换 + 编译）
        ├── SKILL.md
        ├── scripts/convert.py  # MD/DOCX → .tex 转换引擎
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
- **2026-08-05 新增**: 加粗→黑体映射（`**加粗**` → `\fzht{加粗}`，非 `\textbf`）
- **2026-08-05 新增**: MinerU DOCX 原生解析集成（0.2秒/页，保留 colspan/rowspan）

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
  - `skills/harryopo-tikz-diagram/templates/sequence-diagram/template.tex` — v5.1紧凑版模板（含完整文档+铁律）
  - `skills/harryopo-tikz-diagram/examples/example-sequence-diagram.tex` — 7参与者一键部署时序图（智配桌面安装器）
  - `skills/harryopo-tikz-diagram/SKILL.md` — 添加模板四：UML时序图完整章节
- **紧凑版间距常量**: GapMsg=0.88, GapRet=1.00, GapSelf=1.40, GapPhase=0.28, FragPad=0.15, SelfLoopH=0.50（cm）
- **编译结果**: 7参与者+alt+loop+4阶段，1页PDF，0 Overfull
- **已清理旧文件**: demo-seq-compact.*、demo-seq-final.*、旧example-sequence-diagram.*

## fireworks-tech-graph 流程图优化（2026-07-27）

### 项目位置
`d:\ai\latex\opensource-reference\fireworks-tech-graph\`

### 核心调整
- **风格**: Style 7 — OpenAI Official（极简白底+品牌绿）
- **输出文件**: `output/zhixing-agent-style7.svg`
- **生成脚本**: `scripts/gen-style7.py`
- **参考文档**: `d:\ai\claude code\微信读书\zhixing-reader\deliverables\agent编排流程图_详细说明.md`

### 紧凑化关键参数
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

### 自适应宽度算法
```python
# 每个chip卡片独立指定宽度
br_items = [
    ('knowledge_query', 'direct_answer', 'L1', 130),
    ('deep_discussion',   'socratic',      'L3', 120),
    ('teaching_practice', 'feynman',       'L2', 126),
    ('casual_chat',       'direct_answer', 'L1', 130),
]
# 根据总宽度和间隙自动居中
br_total = sum(w for _,_,_,w in br_items) + br_gap * (len(br_items) - 1)
br_start_x = (W - br_total) // 2
```

### 预览地址
`http://localhost:9999/zhixing-agent-style7.svg`（本地HTTP服务）
