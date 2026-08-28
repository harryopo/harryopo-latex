---
name: "harryopo-office"
description: "harryopo 办公文档超级 skill：Word / LaTeX 全格式。Word：Markdown 中间态 → 公文/学术 .docx（方正/开源字体一键切换，原生自动目录、OMML 数学公式、表格/图片/注释/参考文献规范排版）。LaTeX：论文/报告/笔记 PDF，支持从 Markdown/Word 自动转换，或手写 .tex。单双栏、蓝/黑主题、方正字体、XITS 数学、三线表。内置图表融合：super-diagram 架构图/时序图 + Mermaid 流程图自动渲染插入三条链路。触发词：写word、生成word、word文档、docx、公文模板、学术论文word、word转换、latex、论文、报告、PDF、tex、md转latex、word转latex、docx转pdf、markdown转tex、文档转换、架构图、流程图、时序图、框架图、画个图。"
---
# harryopo-office

harryopo 办公文档超级 skill —— 覆盖 **Word (.docx)** 与 **LaTeX (PDF)** 两大格式：

- **Word 流程**：AI 产出 Markdown 中间态（用户可直接编辑）→ `md_to_word.py` 渲染成规范 .docx
- **LaTeX 流程**：手写 .tex 或 MD/DOCX 自动转换（Pandoc + Lua Filter 或纯 Python），编译生成专业 PDF

## 项目架构

```text
harryopo-office/
├── SKILL.md                              # 本文件
├── scripts/
│   ├── convert.py                        # MD/DOCX → paper/report .tex（纯 Python）
│   ├── tex2md.py                         # .tex → MD 中间态（反向链路：LaTeX→Word/PDF）
│   ├── diagram_render.py                 # 图表统一渲染器（super-diagram 架构图/时序图 + mermaid）
│   ├── md2latex.py                       # MD → math-notes .tex（Pandoc 优先 + Python 回退）
│   ├── mineru_cli.py                     # DOCX/PDF → MD（MinerU 解析 + 清洗 + HTML表格转LaTeX）
│   ├── html_table_to_latex.py            # HTML 表格 → LaTeX（colspan/rowspan → multicolumn/multirow）
│   ├── test-sample.md                    # 测试用 Markdown
│   └── word/                             # Word (.docx) 模板引擎体系
│       ├── md_to_word.py                 #   Markdown 中间态 → .docx（主入口）
│       ├── word_template_engine.py       #   Word 模板引擎（渲染 API + OMML 公式）
│       ├── template/                     #   docxtpl 模板填充子 skill
│       │   ├── docx_template.py          #     主入口 CLI（extract/validate/render）
│       │   ├── schema_extractor.py       #     模板占位符 → JSON Schema（类型推断）
│       │   ├── template_render.py        #     data.json → 保真 .docx（含图片 InlineImage）
│       │   └── examples/
│       │       ├── make_example_template.py  # 生成示例模板（占位符/循环表格/图片）
│       │       ├── template.docx / schema.json / data.json / output.docx
│       ├── configs/
│       │   ├── fangzheng.json            #   方正字体方案（本地，GBK）
│       │   └── opensource.json           #   开源字体方案（Windows 系统字体）
│       └── examples/
│           └── example.md                #   完整示例（标题/摘要/表格/公式/图片/注释/参考文献）
└── templates/                            # 完整 LaTeX 模板包（自包含）
    ├── build.ps1                         # 编译脚本（环境检查 + TEXINPUTS + xelatex×3）
    ├── cls/                              # 文档类/样式
    │   ├── harryopo-base.sty             #   共享基础包 v4.3
    │   ├── harryopo-paper.cls            #   论文文档类（单/双栏 + nomath）v4.1
    │   └── harryopo-report.cls           #   报告文档类（封面 + 目录）v4.1
    ├── fonts/                            # 内嵌字体（18个文件，无需系统安装）
    ├── paper/                            # 论文目录
    │   ├── showcase-paper.tex/pdf        #   全功能展示
    │   └── example-paper-twocolumn.tex/pdf  # 双栏示例
    ├── report/                           # 报告目录
    │   ├── showcase-report.tex/pdf       #   全功能展示
    │   └── example-report.tex/pdf        #   简单示例
    └── math-notes/                       # 数理笔记目录（独立体系）
        ├── harryopo-mathnotes.cls        #   笔记文档类（独立，不加载base.sty）
        ├── md2latex.py                   #   MD→LaTeX 统一脚本（Pandoc 引擎 + Python 回退）
        ├── example-note.md               #   示例 Markdown（高等数学笔记）
        ├── main.tex                       #   手写示例
        ├── build.ps1                     #   编译脚本
        ├── fonts/                        #   专用字体（XITS + TeX Gyre Heros）
        └── pandoc/                       #   Pandoc 集成
            ├── mathnotes-template.latex  #     自定义 LaTeX 模板
            └── mathnotes-table.lua       #     智能表格 Lua Filter
```

---

## 工作流程

### 触发词识别

当用户输入包含以下关键词时，进入对应流程：

| 用户意图 | 关键词示例 | 处理流程 |
|----------|-----------|----------|
| 生成 Word 文档 | "写word"、"生成word"、"word文档"、"docx"、"公文"、"学术论文word" | **先出 MD 中间态 → md_to_word.py 渲染** |
| 按用户模板填充 | "按模板"、"模板填充"、"套用模板"、"docxtpl"、"填写模板"、"根据模板生成" | **extract schema → AI 产 data.json → render（docxtpl 保真）** |
| 总结报告/总结文档 | "总结报告"、"总结文档"、"写总结"、"生成总结" | **先总结后转换** |
| 输出 PDF | "输出 PDF"、"生成 PDF"、"转 PDF" | 确认源材料后转换编译 |
| 输出 LaTeX | "输出 LaTeX"、"生成 LaTeX"、"转 latex"、"写 tex" | 确认源材料后转换 |
| MD/DOCX 转 LaTeX | "md转latex"、"docx转pdf"、"markdown转tex" | 直接转换 |
| 手写 LaTeX | "写论文"、"写报告"、"写笔记" | 提供骨架模板 |
| 生成框架图 | "框架图"、"架构图"、"流程图"、"时序图"、"画个图"、"配图" | **先提问是否生成 → 产出 super-diagram JSON 代码块 → 自动渲染插入三条链路** |

### Word 生成流程（Markdown 中间态 → .docx）

**核心原则：AI 只产出结构化 Markdown（中间态），引擎负责保真渲染。**

```
用户需求 → [AI 产出 Markdown 中间态] → [用户查看/修改 MD] → [md_to_word.py 渲染] → .docx
```

#### 第1步：产出 Markdown 中间态

AI 按以下约定生成 .md（**必须呈现给用户确认/编辑，用户可直接改文本**）：

| Markdown 写法 | Word 效果 |
|---------------|-----------|
| `# 主标题`（文档第一个 `# `） | 大标题（方正大标宋，居中） |
| `> 副标题：xxx` | 副标题（紧随主标题，可空行分隔） |
| 主标题后第一段裸文本（如 `张三 计算机学院 2025000101`）或 `> 作者：xxx` | 作者（居中楷体四号 14pt） |
| `**摘要：** 内容` | 摘要（"摘要："黑体 + 内容楷体） |
| `**关键词：** 词1；词2` | 关键词（"关键词："黑体 + 内容楷体） |
| `# 一、引言`（后续 `# `） | 一级标题 Heading 1（进目录） |
| `## 2.1 小节` | 二级标题 Heading 2 |
| `### 3.1.1 小节` | 三级标题 Heading 3 |
| `#### 3.1.1.1 小节` | 四级标题 Heading 4 |
| 普通段落 | 正文（方正书宋，首行缩进，1倍行距） |
| 段落内 `**加粗**` | 黑体片段（中文字体加粗用黑体而非加粗样式） |
| `> 注：xxx` | 注释段落（仿宋，五号，灰色） |
| `> **表1：xxx**`（表格上方） | 表格标题（楷体居中） |
| `\| a \| b \|` 表格 | 表格（表头黑体居中，内容居中） |
| `> 注：xxx`（表格下方） | 表格注释 |
| `![图1：xxx](path.png)` | 图片（图注下方；文件缺失自动占位） |
| ` ```super-diagram ` + JSON 代码块 | 框架图（架构图/时序图，自动渲染 PNG 插入并带图注） |
| ` ```mermaid ` + 代码块 | 流程图（Mermaid，自动渲染 PNG 插入） |
| `$$ C_i = C_0 \cdot \alpha^i $$` | 行间公式（Word 原生 OMML） |
| `> 式(1)：xxx`（公式下方） | 公式编号（楷体居中） |
| `## 参考文献` + `[1] 条目` | 参考文献列表 |

支持的 LaTeX 数学子集：上下标（`^` `_`）、`\frac{}{}`、`\sqrt{}`、希腊字母（`\alpha` 等）、常用运算符（`\cdot` `\times` `\sum` 等）、`\left( \right)`。

**注意**：目录自动放第一页（`# 主标题` 前），正文从第二页开始，无需手动标记。

#### 第2步：用户确认/编辑 MD

用户查看中间态 Markdown，直接修改文本、补充数据、调整结构。

#### 第3步：渲染 .docx

```powershell
cd .trae/skills/harryopo-office/scripts/word

# 方正字体版（本地，GBK，默认）
python md_to_word.py input.md

# 开源字体版（Windows 系统字体，免授权）
python md_to_word.py input.md -c configs/opensource.json

# 指定输出路径 / 不自动更新目录
python md_to_word.py input.md -o output.docx
python md_to_word.py input.md --no-toc
```

渲染自动完成：
- 配置驱动字体（切换方正/开源只需换 `-c` 配置）
- 自动目录（第一页）+ 用 Word COM 自动更新 TOC 域（`SaveAs2` 处理 OMML 兼容）
- 公式转 Word 原生 OMML（可用 Word 公式编辑器继续编辑）

**依赖**：`python-docx`、`lxml`、`pywin32`（后两者 TOC 更新需要，无 COM 时自动跳过并提示手动更新域）。

### docxtpl 模板填充流程（用户模板 → 保真 .docx）

**核心原则：用户用 Word 设计好的模板，AI 只产出结构化 JSON 填充，格式 100% 保留模板。**

解决"AI 不按用户模板来"的根本方案——用户先把喜欢的样式做进 Word 模板（所见即所得），AI 只需填空。

```
用户模板 template.docx（含 {{ 占位符 }}）
  → [extract] 自动提取占位符 → schema.json（字段清单 + 类型推断）
  → [AI 阅读 schema 确认字段含义 → 产出 data.json]
  → [用户可编辑 data.json]
  → [render --check] 校验后渲染 → 保真输出 .docx
```

#### 第1步：用户准备模板

用户用 Word 编辑模板（任意复杂：封面/表格/页眉页脚/样式），在动态内容处插入占位符：

| 占位符语法 | 作用 | 示例 |
|-----------|------|------|
| `{{ project_name }}` | 普通变量（正文/单元格直接写） | `项目名称：{{ project_name }}` |
| `{{ owner.name }}` | 对象字段 | `负责人：{{ owner.name }}` |
| `{% if need %}...{% endif %}` | 行内条件（不填则整句隐藏） | `{% if need_abstract %}包含摘要{% endif %}` |
| `{%tr for task in tasks %}...{%tr endfor %}` | 表格行循环（for/endfor **各自独占一行**，中间行被复制） | 见示例模板 |
| `{%tc for c in cols %}...{%tc endfor %}` | 表格列循环 | 动态列 |
| `{%p for x in xs %}...{%p endfor %}` | 段落循环 | 动态列表 |
| `{% hm %}` / `{% vm %}...{% endvm %}` | 水平/垂直合并单元格 | 合并表格 |
| `{{ logo }}` + data 图片对象 | 插入图片 | data: `{"image":"a.png","width_mm":30}` |

**占位符硬规则**：必须连续、不要加粗/改色/拆分 run（Word 会把样式变化拆成多个 run，导致占位符无法识别）。

#### 第2步：提取 schema

```powershell
cd .trae/skills/harryopo-office/scripts/word/template
python docx_template.py extract 模板.docx -o schema.json
```

自动完成：
- 扫描正文/页眉/页脚/脚注全部占位符
- jinja2 作用域分析：`{% for x in items %}` → items 为数组；`obj.field` → object；`{% if %}` → 可选字段
- 排除 jinja2 内建变量（loop/range 等）
- 输出字段清单（名称/类型/必填性），**AI 据此向用户确认每个字段含义**，再产 data.json

#### 第3步：AI 产出 data.json（用户可编辑）

AI 按 schema 填写内容（中间态 JSON，用户可直接修改），支持图片字段：

```json
{
  "project_name": "知行读书·多智能体知识服务平台",
  "owner": {"name": "张三", "phone": "138-0000-0000"},
  "need_abstract": true,
  "tasks": [
    {"name": "架构设计", "owner": "张三", "status": "已完成"},
    {"name": "引擎开发", "owner": "李四", "status": "进行中"}
  ],
  "logo": {"image": "examples/demo.png", "width_mm": 30}
}
```

#### 第4步：校验 + 渲染

```powershell
# 校验（对照 schema：必填缺失 / 类型错误）
python docx_template.py validate data.json -s schema.json

# 渲染（--check 渲染前自动校验；--force 校验失败仍渲染）
python docx_template.py render 模板.docx -d data.json -o 输出.docx --check
```

渲染自动完成：
- 所有占位符按模板样式填充，**格式 100% 保留用户模板**
- 表格行循环/条件块/合并单元格原生支持
- 图片字段自动转 docxtpl InlineImage（缺省尺寸按原图比例）
- 必填字段缺失会报错（--force 可强制渲染便于排查）

**依赖**：`docxtpl`（自动带 python-docx + jinja2）。示例见 `template/examples/`（`make_example_template.py` 生成模板 → extract → data.json → output.docx 全链路）。

### 图表融合流程（super-diagram 框架图 + mermaid 流程图）

**核心：文档涉及架构/流程/时序时，AI 先提问用户是否生成框架图；确认后产出结构化图表数据嵌入 MD，渲染器自动转 PNG 并插入三条链路（Word/paper/notes）。**

#### 第1步：提问用户（关键）

产出 MD 中间态时，若内容涉及以下场景，**必须主动提问**："文档涉及 XX 架构/流程，是否需要生成一张框架图？"

| 文档内容 | 建议图表 |
|----------|----------|
| 系统架构、模块划分、技术栈层次 | 架构图（super-diagram `architecture`） |
| 业务/数据流程、编排流水线 | 流程图（super-diagram `architecture` 线性布局） |
| 调用链、消息交互、时序 | 时序图（super-diagram `sequence`） |
| 简单流程、类图式说明 | Mermaid（````mermaid`） |

用户确认后 → 第2步；用户不需要 → 跳过。

#### 第2步：产出图表数据代码块（AI 嵌入 MD）

在文档对应位置插入图表代码块，渲染器（`office.py render` 自动执行）会把代码块替换为 `![图注](figures/xxx.png)`：

**架构图**（````super-diagram` + architecture JSON，AI 按契约算坐标）：

````markdown
```super-diagram
{
  "type": "architecture",
  "canvas": {"width": 960, "height": 480, "theme": "light"},
  "title": "图1：智能体编排系统总体架构",
  "subtitle": "用户 → 网关 → 服务 → 数据库",
  "nodes": [
    {"id": "user", "en": "User", "zh": "用户", "x": 400, "y": 80, "w": 160, "h": 64, "type": "frontend"},
    {"id": "gw", "en": "API Gateway", "zh": "API 网关", "x": 400, "y": 220, "w": 160, "h": 64, "type": "backend"},
    {"id": "svc", "en": "Agent Service", "zh": "智能体服务", "x": 400, "y": 360, "w": 160, "h": 64, "type": "backend"}
  ],
  "edges": [
    {"from": "user", "to": "gw", "label": "对话"},
    {"from": "gw", "to": "svc", "label": "请求"}
  ]
}
```
````

**时序图**（````super-diagram` + sequence JSON）：

````markdown
```super-diagram
{
  "type": "sequence",
  "canvas": {"width": 1100, "height": 760, "theme": "light"},
  "title": "图2：多轮对话调用时序",
  "participants": [
    {"id": "user", "en": "User", "zh": "用户", "kind": "user"},
    {"id": "llm", "en": "LLM", "zh": "大模型", "kind": "db"}
  ],
  "messages": [
    {"from": "user", "to": "llm", "en": "POST /chat", "zh": "发送问题", "time": "0ms"},
    {"from": "llm", "to": "user", "en": "LLMOutput", "zh": "生成回复", "async": true, "time": "1.2s"}
  ]
}
```
````

**图注规则**：`title` 字段就是图片下方的图注（如 `图1：xxx`），AI 写完整编号与文案，渲染器原样使用。

#### 第3步：坐标布局铁律（AI 计算架构图坐标时必须遵守）

1. **网格对齐**：所有 `x, y` 必须是 **20 的倍数**
2. **层间垂直间距 ≥ 120px**（如 y=100 → y=220 → y=360）
3. **同层水平间距 ≥ 150px**（节点中心到中心）
4. **画布留边 ≥ 40px**：所有节点必须在 `canvas.width × height` 内
5. **体现拓扑语义**：星型分发（源居中扇开）、线性流水（左→右一字排开）、分层架构（上→下垂直）
6. **节点尺寸**：标准 160×64，数据库 160×56

#### 第4步：自动渲染（无需手动操作）

`office.py render` 自动完成：识别 ````super-diagram` / ````mermaid` 代码块 → 渲染 PNG 到 `figures/` → 替换为图片引用 → Word/paper/notes 三条链路自动带图带注。渲染失败保留代码块便于排查。

**依赖**：super-diagram skill 渲染脚本（`c:\Users\Lenovo\.trae-cn\skills\super-diagram\scripts\render_v2.py`，可用 `SUPER_DIAGRAM_SCRIPT` 环境变量覆盖）；PNG 导出需 `playwright`（含 chromium）。mermaid 需 `mmdc`。

#### 第5步：渲染后展示确认（关键闭环）

渲染出 PNG 后，**必须先把图展示给用户确认是否满意**：
- 满意 → 继续生成 Word / paper / notes 三条链路
- 不满意 → 按用户反馈调整 JSON 拓扑/坐标/图注，重新渲染，**直到用户满意再继续**（禁止未确认直接进入文档链路）

> 图表属于视觉产物，用户是否认可必须人工确认——内容确认优先于格式转换，图确认优先于文档生成。

### 先总结后转换流程（关键）

**核心原则：内容确认优先于格式转换。**

#### 场景C：用户有 LaTeX 源文件（.tex）→ Word

1. **反向转换**：调用 `tex2md.py` 将 .tex 清洗为标准 Markdown（MD 中间态）
   - 处理 `{\fzht }`/`\textbf` 黑体、`\section/subsection/subsubsection` 标题层级、`tabularx/tabular` 表格、`equation/align` 公式、`figure` 图片、`thebibliography` 参考文献
2. **内容确认**：将 .md 呈现给用户确认
3. **Word 渲染**：`md_to_word.py` 渲染 .docx（可选 `--pdf` 同会话导出 PDF）
   - 完整入口：`office.py render input.tex --format word --pdf`

**注意**：表格单元格内的 `{\fzht }` 不转 `**`（Word 表格字体由模板样式控制，星号会原样显示）；表格标题独立 `quote` 块（`> **表N：**`）与表格相邻；空 `\caption{}` 占位自动丢弃。

#### 场景A：用户有现有源材料（Word/MD/文本）

1. **材料转换**：将 Word/MD 转换为标准 Markdown（.md）
2. **内容确认**：将 .md 呈现给用户，请其确认内容或提出修改意见
3. **LaTeX 转换**：用户确认 .md 后，调用 `convert.py` 转换为 .tex
4. **编译输出**：使用 xelatex 编译生成 PDF

**为什么 Word 也要先转 MD？**
- Word 转 LaTeX 虽然技术上可行，但内容细节（标题层级、表格结构、图片位置）需要人工确认
- 先转 MD 让用户看到纯文本内容，确认无误后再转 LaTeX，避免反复编译调试
- MD 是中间态，用户可直接编辑修改，比编辑 .tex/PDF 方便得多

#### 场景B：用户无源材料（只提需求）

1. **内容调研与总结**
   - 先用通用大模型能力总结用户所需报告/文档的内容
   - 生成一份结构化的 **Markdown 文档**（.md）
   - 包含：标题、摘要、章节结构、关键要点、表格/数据建议

2. **用户确认**
   - 将生成的 .md 文档呈现给用户
   - 明确告知："这是根据你的需求总结的内容，请确认或提出修改意见"
   - **等待用户确认后再进行 LaTeX 转换**

3. **LaTeX 转换与编译**
   - 用户确认 .md 内容后，调用 `convert.py` 转换为 .tex
   - 使用 xelatex 编译生成 PDF
   - 输出最终文件

**为什么先出 MD？**
- 用户可直接编辑 .md 修改内容，比编辑 .tex/PDF 更方便
- 避免一次性转换后用户发现内容有误，需要反复转换编译
- MD 是中间态，兼顾可读性和可转换性
- 特别是"总结报告"类需求，内容本身需要先确定，格式是其次

### 方式A：MinerU DOCX → MD → LaTeX（DOCX 首选，两阶段审查流程）

适用场景：用户上传 Word 文档（.docx），需要保留表格结构（含合并单元格）和行内加粗。

**MinerU 优势**：0.2 秒/页极速解析，原生 DOCX 支持，表格合并单元格（colspan/rowspan）精确保留为 HTML，行内加粗保留为 `**` 标记。

#### 前提

```powershell
# 安装 MinerU（首次）
pip install -U "mineru[all]"
# 下载模型（首次，选 modelscope + pipeline，约 2-3GB）
@("modelscope","pipeline") | mineru-models-download
```

#### 两阶段流程（关键！）

**阶段1：DOCX → 审查 MD（展示给用户确认）**

```powershell
python scripts/mineru_cli.py input.docx -o output/ --stage review
```

生成 `output/review.md`——标准 Markdown，加粗用 `**` 标记，表格保留 HTML 结构。**必须展示给用户确认。**

**阶段2：审查 MD → LaTeX MD → 编译（用户确认后执行）**

```powershell
# 审查 MD → 含 LaTeX 代码的 MD
python scripts/mineru_cli.py output/review.md -o output/ --stage convert

# MD → LaTeX
python scripts/convert.py output/converted.md --type paper --no-math

# 编译
cd templates/paper && xelatex result.tex
```

#### 处理流程

```
DOCX → [MinerU 解析] → raw_mineru.md（含 ** 加粗 + HTML 表格）
         → [阶段1 clean_markdown_review] → review.md（标准 MD，用户审查）
         → [用户确认]
         → [阶段2 clean_markdown_convert] → converted.md（含 LaTeX 表格代码）
         → [convert.py] → paper/report .tex
         → [xelatex ×3] → PDF
```

#### 为什么需要两阶段？

1. **用户审查**：MinerU 解析可能有误差，用户需要确认内容、加粗位置、表格结构
2. **中间可编辑**：review.md 是标准 Markdown，用户可直接增删 `**` 标记调整加粗范围
3. **避免反复编译**：确认内容后再转 LaTeX，避免"编译→发现问题→修改→重新编译"循环

#### 表格处理（核心能力）

| 表格类型 | MinerU 输出 | LaTeX 生成 |
|----------|------------|-----------|
| 简单表 | HTML `<table>` | tabularx + booktabs 三线表 |
| 水平合并 | `colspan="N"` | `\multicolumn{N}{c}{...}` |
| 垂直合并 | `rowspan="N"` | `\multirow{N}{*}{...}` |
| 跨页长表（>20行） | HTML `<table>` | longtable + \endhead/\endfoot |

**注意**：multirow 与 tabularx 冲突，含合并单元格的表自动切换为固定列宽 tabular。

#### 加粗→黑体规则（精确行内加粗）

中文排版规范：MD 的 `**加粗**` 统一转为 `{\fzht 文字}`（方正黑体分组调用），而非 `\textbf{}`（中文字体加粗后笔画糊）。

**关键语法**：必须用 `{\fzht 文字}`（声明式+分组），**不能用** `\fzht{文字}`（会被解析为全局字体切换，花括号结束后字体仍然有效，导致后续文字也被强制黑体）。

| 写法 | 效果 | 说明 |
|------|------|------|
| `{\fzht 加粗}正常` | 只有"加粗"是黑体 | ✓ 正确 |
| `\fzht{加粗}正常` | "加粗"和"正常"都是黑体 | ✗ 字体泄漏 |

此规则在 convert.py（正文加粗）和 html_table_to_latex.py（表格单元格加粗）中均已实现。加粗完全依赖原文 `**` 标记，不做自动推断（如自动表头加粗）。

### 方式B：Pandoc MD → LaTeX（math-notes，推荐）

适用场景：数理笔记、讲义、读书笔记。Pandoc 引擎提供最优 MD 兼容性。

#### 一键转换

```powershell
cd templates/math-notes
python md2latex.py example-note.md --engine pandoc --clean
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--engine pandoc` | Pandoc 引擎（推荐） | pandoc |
| `--engine python` | 纯 Python 引擎（Pandoc 不可用时自动回退） | - |
| `--tex-only` | 仅生成 .tex，不编译 PDF | - |
| `--clean` | 编译后清理 .aux/.log 等临时文件 | - |
| `-o output.tex` | 自定义输出路径 | 自动 .md→.tex |

**Pandoc 引擎特性：**
- **加粗/斜体/代码**：AST 级解析，100% 准确
- **表格**：Lua Filter 智能处理——比例 X 列 + booktabs 三线表 + caption 下方 + `\|` 数学保护
- **列表**：支持嵌套有序/无序列表
- **LaTeX 数学**：原生 `\(...\)` 保留，零破坏
- **引用/脚注**：完整支持

**模板内置特性（harryopo-mathnotes.cls）：**
- 节编号：`一、`（section，中文编号+顿号）、`1.1`（subsection，阿拉伯数字）
- 智能页眉：奇数页=subsection，偶数页=section
- 表格 caption 默认在下方
- 方正字体 + XITS 数学 + TeX Gyre Heros 无衬线
- 每节结束无下划线分割

#### 直接使用 Pandoc 命令

```powershell
pandoc input.md \
  --template=pandoc/mathnotes-template.latex \
  --lua-filter=pandoc/mathnotes-table.lua \
  --standalone -o output.tex
xelatex -interaction=nonstopmode output.tex
xelatex -interaction=nonstopmode output.tex
xelatex -interaction=nonstopmode output.tex
```

### 方式B：MD/DOCX → paper/report（convert.py）

收到用户上传的 `.md` / `.docx` 后，使用纯 Python 脚本转换。

#### 第1步：确认需求

| 确认项 | 选项 | 默认值 |
|--------|------|--------|
| **输出类型** | 论文(paper) / 报告(report) | 论文 |
| **栏数** | 单栏 / 双栏（报告仅单栏） | 单栏 |
| **主题** | 蓝(blue) / 深紫(dark) | 蓝 |
| **标题** | 自动提取 / 手动填写 | 自动 |
| **作者** | 自动提取 / 手动填写 | 自动 |
| **日期** | 自动 / 手动 | 当天 |
| **无数学** | 是/否（读书笔记用） | 否 |

#### 第2步：执行转换

```powershell
cd scripts

# 论文（双栏 + 无数学公式）
python convert.py input.md --type paper --twocolumn --no-math

# 报告
python convert.py input.md --type report --no-math

# 论文（有数学公式，默认加载 unicode-math）
python convert.py input.md --type paper --twocolumn
```

完整参数：
```
--type paper|report     文档类型
--title "标题"           覆盖自动提取
--author "作者"          覆盖自动提取（多作者用逗号/分号分隔，自动转顿号）
--date "2026年6月22日"   覆盖默认日期
--subtitle "副标题"      仅 report
--institute "机构"       仅 report
--abstract "摘要..."     覆盖自动提取
--keywords "kw1；kw2"    覆盖自动提取
--dark                  深紫主题
--twocolumn             双栏（仅 paper）
--no-math               禁用 unicode-math（读书笔记/无数学文档用）
--output / -o path      自定义输出路径
```

#### 第3步：编译

```powershell
cd templates
.\build.ps1
```

build.ps1 自动：
- 检查环境（xelatex/字体/cls 文件）
- 设置 TEXINPUTS
- 对所有 .tex 执行 xelatex ×3
- 输出 PDF 到同目录

### 方式C：手写 .tex

直接在 `templates/paper/`、`templates/report/` 或 `templates/math-notes/` 中创建 .tex 文件，然后编译。

---

## 模板速查

### 数理笔记骨架（harryopo-mathnotes）

```latex
\documentclass{harryopo-mathnotes}

\renewcommand{\mathtitle}{高等数学笔记}
\renewcommand{\mathauthor}{张三}
\date{2026年6月21日}

\begin{document}

\newgeometry{top=3cm,bottom=2.5cm,left=4cm,right=4cm}
\maketitle
\thispagestyle{empty}
\cleardoublepage

\setcounter{tocdepth}{2}
\tableofcontents
\cleardoublepage

\strictpagecheck
\setcounter{page}{1}
\restoregeometry
\onehalfspacing

\section{函数与极限}          % → "一、函数与极限"
\subsection{函数的概念}        % → "1.1 函数的概念"
正文…… $y = f(x)$ ……

\begin{table}[htbp]
\centering
\begin{tabularx}{\textwidth}{>{\hsize=0.7\hsize\linewidth=\hsize\raggedright\arraybackslash}X>{\hsize=1.3\hsize\linewidth=\hsize\raggedright\arraybackslash}X}
\toprule
\textbf{列A} & \textbf{列B} \\
\midrule
数据1 & 数据2 \\
\bottomrule
\end{tabularx}
\caption{表格标题（自动在下方）}
\end{table}

\end{document}
```

**math-notes 关键命令：**

| 命令 | 说明 |
|------|------|
| `\mathtitle` / `\mathauthor` | 封面标题/作者（需 `\renewcommand` 设置） |
| `\mathaffiliation` / `\mathinfo` | 封面单位/附加信息 |
| `\fzkt` / `\fzht` / `\fzfs` / `\fzdbs` / `\fzxbs` | 楷体/黑体/仿宋/大标宋/小标宋 |
| `\TitleFont` | 标题专用字体 |

**编注：** math-notes 是独立体系（不加载 `harryopo-base.sty`），因为 mdframed 边框体系与 tcolorbox 冲突，字体配置也不兼容。

### 论文骨架（单栏）

```latex
\documentclass{harryopo-paper}
\title{论文标题}
\author{作者姓名}
\date{2026年6月22日}
\abstractcontent{摘要内容}
\keywordscontent{关键词1；关键词2}
\begin{document}
\maketitlewithabstract
\section{引言}   正文……
\section{方法}   正文……
\end{document}
```

### 论文骨架（双栏）

```latex
\documentclass[twocolumn]{harryopo-paper}
% ... 其他同上，figure*/table* 可跨栏
\maketitlewithabstract  % 标题+摘要自动跨栏排版
```

### 报告骨架

```latex
\documentclass{harryopo-report}
\title{报告标题}
\author{作者}
\date{2026年6月22日}
\begin{document}
\maketitle                 % 封面
\begin{abstract}摘要\end{abstract}
\tableofcontents
\chapter{第一章}  \section{第一节}
\end{document}
```

### 主题选项

```latex
\documentclass{harryopo-paper}                  % 蓝色（默认）
\documentclass[dark]{harryopo-paper}            % 深紫
\documentclass[twocolumn]{harryopo-paper}       % 蓝色双栏
\documentclass[nomath]{harryopo-paper}          % 无数学（读书笔记）
\documentclass[twocolumn,dark,nomath]{harryopo-paper}  % 组合
```

---

## MD → LaTeX 映射

### Pandoc 引擎（math-notes）

Pandoc 原生支持几乎所有 Markdown 扩展语法，无需手动映射：

| Markdown | LaTeX | 说明 |
|----------|-------|------|
| `# Title` | `\section{Title}` | 一级标题 → "一、Title" |
| `## Title` | `\subsection{Title}` | 二级标题 → "1.1 Title" |
| `### Title` | `\subsubsection{Title}` | 三级标题 |
| `**bold**` | `\textbf{bold}` | AST 级解析 |
| `*italic*` | `\textit{italic}` | AST 级解析 |
| `` `code` `` | `\texttt{code}` | 行内代码 |
| ` ```py ... ``` ` | `\begin{lstlisting}` | 代码块（需手动属性配置） |
| `- item` / `1. item` | `\begin{itemize/enumerate}` | 列表 |
| `\| a \| b \|` | `\begin{table}...tabularx` | Lua Filter 智能表格 |
| `$$ E=mc^2 $$` | 保留为 `\[ E=mc^2 \]` | 块级公式 |
| `$x^2$` | 保留为 `\(x^2\)` | 行内公式 |
| `> quote` | `\begin{quote}` | 引用 |

### Python 引擎（paper/report — convert.py）

| Markdown | LaTeX | 说明 |
|----------|-------|------|
| `# title` | `\section*{title}` (paper) / `\chapter*{title}` (report) | 一级标题（无编号，自动进目录） |
| `## title` | `\subsection*{title}` (paper) / `\section*{title}` (report) | 二级标题（无编号，自动进目录） |
| `### title` | `\subsubsection*{title}` | 三级标题（无编号，自动进目录） |
| `#### title` | `\subhead{title}` | 括号细目 |
| `**bold**` | `{\fzht bold}` | 粗体→黑体（分组调用，精确行内） |
| `*italic*` | `\textit{italic}` | 斜体 |
| `` `code` `` | `\inlinecode{code}` | 行内代码 |
| `- item` | `\begin{itemize}\item` | 无序列表 |
| `1. item` | `\begin{enumerate}\item` | 有序列表 |
| `\| a \| b \|` | `\begin{table}...booktabs...` | 三线表 |
| `![](path)` | `\begin{figure}\includegraphics` | 图片 |
| `> quote` | `\begin{quote}` | 引用 |
| `$$ E=mc^2 $$` | `\begin{equation}` | 块级公式 |

---

## Pandoc Lua Filter 详解

### mathnotes-table.lua 功能

1. **比例 X 列**：基于内容宽度智能分配列宽（`\hsize=X\hsize`），自动换行不溢出
2. **数字列检测**：60% 以上为数字时自动居中
3. **数学保护**：Pandoc AST 级处理，`\|` 在数学公式中不会误拆列
4. **caption 下置**：`\caption{}` 在 `\end{tabularx}` 之后
5. **booktabs 三线表**：`\toprule` / `\midrule` / `\bottomrule`

### 表格注意事项

- 用 `lorem` 长文本测试是否溢出逻辑：`\hsize` 权重用 `md2latex.py` 或 Lua filter 处理
- float 表用 `[htbp]`，跨栏用 `table*`
- 数学公式直接写 `$...$` 或 `$$...$$`，Pandoc 会正确处理

---

## 命令速查

### 字体命令（全部模板通用）

| 命令 | 字体 | 文件 | 用途 |
|------|------|------|------|
| `\setCJKmainfont` | 方正书宋 | FZSSJW.TTF | 正文默认 |
| `\setCJKsansfont` | 方正黑体 | FZHTJW.TTF | 无衬线默认 |
| `\fzxb` | 方正小标宋 | FZXBSJW.TTF | 文档/章标题 |
| `\fzdbs` | 方正大标宋 | FZDBSJW.TTF | 节标题 |
| `\fzht` | 方正黑体 | FZHTJW.TTF | subsection/关键词标签 |
| `\fzkt` | 方正楷体 | FZKTJW.TTF | 作者/页眉/摘要正文 |
| `\fzfs` | 方正仿宋 | FZFSJW.TTF | 机构/日期 |

**⚠️ 声明式用法**：`\fzht`/`\fzkt`/`\fzfs`/`\fzdbs`/`\fzxb` 均为声明式命令（类似 `\bfseries`）。手写时用 `{\fzht 文字}` 分组调用；自动生成（convert.py 等）也统一输出 `{\fzht 文字}` 格式。**不要用 `\fzht{文字}` 参数式写法**——花括号不会限制字体切换范围。

### 环境（paper/report）

| 环境 | 说明 |
|------|------|
| `{theorem}` `{definition}` `{lemma}` | 定理类 |
| `{table}[htbp]` | 三线表 |
| `{figure}[htbp]` | 插图 |
| `{figure*}[tbp]` | 跨栏插图（双栏） |
| `{lstlisting}[style=pystyle]` | Python 代码 |
| `{algorithm}[htbp]` | 算法伪代码（仅 paper） |

### 环境（math-notes）

| 环境 | 说明 |
|------|------|
| `{table}[htbp]` | float 三线表（caption 自动下方） |
| `{tabularx}{\textwidth}{X...X}` | 自动换行表格（推荐用 Lua filter 生成） |
| `{mdframed}` | 定理/定义框架框 |

### 特殊功能

| 命令 | 适用模板 | 说明 |
|------|----------|------|
| `\upcite{ref}` | paper/report | 上标引用 |
| `\inlinecode{foo()}` | paper/report | 行内代码 |
| `\maketitlewithabstract` | paper | 标题+摘要（双栏自动跨栏） |
| `\renewcommand{\mathtitle}{...}` | math-notes | 设置封面标题 |

---

## 注意事项

### paper/report
1. **作者分隔**：多作者用逗号/分号分隔，convert.py 自动转顿号（避免 `\and` 在双栏中冲突）
2. **读书笔记**：使用 `--no-math` 禁用 unicode-math
3. **环境检查**：build.ps1 编译前自动检查 xelatex/字体/cls
4. **代码块转义**：LaTeX 特殊字符在代码块中自动转义
5. **DOCX 支持**：office.py 一键转换首选 `anydoc`（`pip install firecrawl-anydoc`，毫秒级 GFM 表格原生；含图文档自动回退 pandoc 保图片），需 `pip install python-docx`（pandoc 降级 + 表格回填）或 `winget install pandoc`
6. **标题无编号**：convert.py 已改为 `\section*`/`\subsection*` 系列，目录通过 `\addcontentsline` 保留；`.cls` 中重定义 `\thesection` 等为空，手写 .tex 也生效
7. **表格自适应**：convert.py 生成的表格使用 `tabularx{\textwidth}{>{\raggedright\arraybackslash}X...}`，caption 在下方；手写时同理，避免固定列宽导致越界
8. **图片 caption**：独立行图片 `![](alt|path)` 自动识别为 `\begin{figure}...\caption{alt}...\end{figure}`，caption 在图下方
9. **字体加载关键**：`harryopo-base.sty` 中 fontspec 语法必须是 `\setCJKmainfont{FZSSJW}[options]`（name 在前），否则方正字体加载失败并回退到 ctex 默认；所有 `\newfontfamily`/`\newCJKfontfamily` 需指定 `BoldFont=...` 自指，避免 "Font shape undefined" 警告
10. **`\fzht` 是声明式命令**：`\newcommand{\fzht}{\hrypht}` 定义的是字体切换声明（类似 `\bfseries`），不是带参数命令。**必须用 `{\fzht 文字}` 分组调用**来限定字体范围；`\fzht{文字}` 会导致花括号结束后字体切换仍然有效，后续文字也被强制黑体。所有 5 个字体快捷命令（`\fzkt`/`\fzfs`/`\fzdbs`/`\fzxb`/`\fzht`）均需此模式
11. **DOCX 两阶段流程**：mineru_cli.py 拆为 `--stage review`（生成审查MD）和 `--stage convert`（转LaTeX MD）两个阶段。**必须先执行 review 阶段展示给用户确认**，用户确认后再执行 convert 阶段。不要用 `--stage auto` 跳过审查
12. **加粗不做自动推断**：html_table_to_latex.py 不再自动给表头加黑体，加粗完全依赖原文 `**` 标记

### math-notes
6. **独立体系**：math-notes 不加载 `harryopo-base.sty`，不要引入 base.sty（mdframed 与 tcolorbox 冲突）
7. **Pandoc 优先**：md2latex.py 默认使用 Pandoc 引擎；无 Pandoc 时自动回退到纯 Python
8. **三遍编译**：必须 xelatex×3 确保 TOC 和交叉引用稳定
9. **比例 X 列**：表格用 `>{\hsize=N\hsize\linewidth=\hsize}X`，多列 `\hsize` 之和 = 列数
10. **数学保护**：Pandoc 引擎原生 AST 级保护表格中的 `|` 不会被误解析
11. **字体体系**：独立使用 XITS + TeX Gyre Heros，不加载 harryopo-base.sty 的方正字体配置

---

## 依赖

### Word (.docx) 流程
- **必需**：Python 3.7+、`python-docx`（`pip install python-docx`）
- **数学公式**：`lxml`（构建 OMML）
- **TOC 自动更新**：`pywin32`（`pip install pywin32`，Windows + 已装 Word；无 COM 时自动跳过并提示手动"更新域"）
- **中文字体**：方正方案需系统已装方正 GBK 字体；开源方案用 Windows 自带宋体/黑体/楷体/仿宋

### LaTeX 流程
- **必需**：Python 3.7+、xelatex (TeX Live 2024+)、fontspec v2.9+
- **推荐**：Pandoc 3.10+（MD→LaTeX 最优引擎，已安装于 `%LOCALAPPDATA%\Pandoc\`）
- **DOCX 转换**：office.py 首选 `anydoc`（`pip install firecrawl-anydoc`，无图文档毫秒级转换，GFM 表格原生），MinerU 3.0+（`pip install -U "mineru[all]"`）+ python-docx
- **字体**：已内嵌于 `templates/fonts/`，无需单独安装
- **关键**：fontspec v2.9+ 语法要求 `\setCJKmainfont{FONTNAME}[options]`（name 在前），反之为 `[options]{name}` 会导致方正字体加载失败并回退到 ctex 默认字体
