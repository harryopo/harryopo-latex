---
name: "harryopo-office"
description: "harryopo 办公文档超级 skill：Word / LaTeX 全格式。Word：Markdown 中间态 → 公文/学术 .docx（方正/开源字体一键切换，原生自动目录、OMML 数学公式、表格/图片/注释/参考文献规范排版）。LaTeX：论文/报告/笔记 PDF，支持从 Markdown/Word 自动转换，或手写 .tex。单双栏、蓝/黑主题、方正字体、XITS 数学、三线表。内置图表融合：diagram-design 编辑级图表（39 类型：架构/流程/时序/泳道/ER/桑基等）+ Mermaid 流程图自动渲染插入双链路。中文排版护栏：标点全角化 + 空格清理（text_norm.py，双引擎入口自动清洗）。触发词：写word、生成word、word文档、docx、公文模板、学术论文word、word转换、latex、论文、报告、PDF、tex、md转latex、word转latex、docx转pdf、markdown转tex、文档转换、架构图、流程图、时序图、框架图、画个图、配图、diagram-design。"
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
│   ├── office.py                        # ★ 统一主入口（render / diagram / template 三子命令）
│   ├── convert.py                        # MD/DOCX → paper/report .tex（纯 Python）
│   ├── tex2md.py                         # .tex → MD 中间态（反向链路：LaTeX→Word/PDF）
│   ├── diagram_render.py                 # 图表统一渲染器（mermaid 流程图，被 office.py 调用）
│   ├── diagram_design_render.py          # diagram-design HTML → PNG（--svg 仅截 SVG / --check 自检）
│   ├── text_norm.py                      # 中文标点全角化 + 空格清理（护栏层，md_to_word/convert 共用）
│   ├── md2latex.py                       # math-notes MD → .tex（纯 Python 版；Pandoc 优先版在 templates/math-notes/md2latex.py）
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
│       │   ├── template_registry.py      #     模板注册表（入库/发现/schema，manifest 白名单校验）
│       │   ├── seed_builtins.py          #     内置模板幂等初始化
│       │   └── examples/
│       │       ├── make_example_template.py  # 生成示例模板（占位符/循环表格/图片）
│       │       ├── template.docx / schema.json / data.json / output.docx
│       ├── configs/
│       │   ├── fangzheng.json            #   方正字体方案（本地，GBK）
│       │   └── opensource.json           #   开源字体方案（Windows 系统字体）
│       └── examples/
│           └── example.md                #   完整示例（标题/摘要/表格/公式/图片/注释/参考文献）
└── skills/
    ├── diagram-design/                   # 编辑级图表 skill（39 类型 × 3 变体）【内嵌】
    │   ├── SKILL.md                      #   设计规范（4px网格/6连接器规则/焦点色/密度预算）
    │   ├── assets/                       #   模板 + 117+ 成品示例 HTML
    │   ├── references/                   #   53 个类型/规范参考文档
    │   └── scripts/                      #   self_check.py / mermaid_extract.py / drawio_extract.py
├── templates/                            # 完整 LaTeX 模板包（自包含）
│   ├── build.ps1                         # 编译脚本（环境检查 + TEXINPUTS + xelatex×3）
│   ├── cls/                              # 文档类/样式
    │   ├── harryopo-base.sty             #   共享基础包 v4.2
    │   ├── harryopo-paper.cls            #   论文文档类（单/双栏 + nomath）v4.0
    │   ├── harryopo-report.cls           #   报告文档类（封面 + 目录）v4.0
    │   └── flushend.sty                  #   双栏末页栏平衡（TinyTeX 缺包时的项目自包含副本）
    ├── fonts/                            # 内嵌字体（18个文件，无需系统安装）
    ├── previews/                         # 示例文档 + 预览方案（5 个最新示例 md）
    │   ├── README.md                     #   示例清单 + office.py 生成命令 + 元信息约定
    │   ├── harryopo-preview.css          #   MD 预览样式（模拟蓝主题）
    │   ├── paper-single-column.md        #   论文单栏示例
    │   ├── paper-twocolumn.md            #   论文双栏示例
    │   ├── paper-showcase.md             #   论文全特性示例（算法/公式/多表/引用）
    │   ├── report.md                     #   报告示例（章节式 + 自动目录）
    │   └── report-showcase.md            #   报告全特性示例（mermaid/RAG 多Agent）
    ├── paper/                            # 论文编译目录（运行时生成 e2e 产物）
    │   └── figures/                      #   占位图（office.py 自动生成真实图）
    ├── report/                           # 报告编译目录（运行时生成 e2e 产物）
    └── math-notes/                       # 数理笔记目录（独立体系）
        ├── harryopo-mathnotes.cls        #   笔记文档类（独立，不加载base.sty）
        ├── md2latex.py                   #   MD→LaTeX 统一脚本（Pandoc 引擎 + Python 回退）
        ├── md2latex.ps1                  #   PowerShell 便捷编译入口
        ├── example-note.md               #   示例 Markdown（高等数学笔记）
        ├── README.md                     #   使用说明
        ├── build.ps1                     #   编译脚本
        ├── fonts/                        #   专用字体（XITS + TeX Gyre Heros）
        ├── figures/                      #   占位图
        └── pandoc/                       #   Pandoc 集成
            ├── mathnotes-template.latex  #     自定义 LaTeX 模板
            └── mathnotes-table.lua       #     智能表格 Lua Filter
```

---

## 工作流程

### 文档生成主流程（推荐路径 · 内容 → 预览 → 图表建议 → 插入 → Word/LaTeX）

**用户写文档 / 文章 / 报告时直接调用本 skill，走以下推荐路径：**

```
用户需求（写文档 / 文章 / 报告）
  │
  ▼ ① 元信息提问（MD 生成前 · 必须）
AI 先提问文档元信息（AskUserQuestion 一次问清，用户可跳过不填）：
  - 文档类型：论文 / 报告 / 笔记
  - 作者：姓名（可含职位/学院/学号注释，如 "张三 计算机学院 2025000101"）
  - 学校 / 单位
  - 日期（今天 / 自定义）
  - 副标题（可选）、栏数（论文：单栏/双栏）、主题（蓝/深紫/黑白灰）
  用户确认后进入 ②
  │
  ▼ ② 内容生成
AI 产出结构化 Markdown 中间态（用户可直接编辑），元信息按约定写入
  （`> 副标题：` / `> 作者：` / `> 单位：` / `> 日期：` blockquote 形式）
  │
  ▼ ③ 内容预览
呈现 MD 给用户确认内容是否有误（可编辑修改）
  │
  ▼ ④ 图表智能分析（贯穿内容生成过程）
AI 阅读内容 → 判断是否适合配图（diagram-design 30+ 类型）
  ├─ 适合 → 提问用户："检测到 XX 内容，建议生成【架构图 / 流程图 / 时序图 / …】，
  │          要生成哪个？"（内容适配多类型时给用户选择）→ 用户确认后进入 ⑤
  └─ 不适合 / 用户拒绝 → 跳过（禁止擅自生成）
  │
  ▼ ⑤ 图描述确认（画图前必须）
用户选定图类型后，AI 先产出**图描述 MD**（图的大致设计，文字形式给用户确认）：
  - 图类型与主题（如：三层架构图 / 数据流图）
  - 节点清单（名称 + 角色，≤9 个，超则拆图）
  - 连线关系（from → to + 标签）
  - 布局意图（分层/方向/焦点色）
用户确认/修改描述 → 进入 ⑥；拓扑理解有偏差先改描述
（描述确认成本低，HTML 画完再返工成本高）
  │
  ▼ ⑥ 图表生成与审核
diagram-design 生成 HTML → PNG → self_check 自检 → 展示图片地址给用户审核（满意再继续）
  │
  ▼ ⑦ 智能插入（写好注释）
审核通过 → 图片引用插入文档对应位置（图注：`![图N：xxx](figures/xx.png)`）
        → 需要补充说明时加 `> 注：xxx` 注释
  │
  ▼ ⑧ 最终输出
office.py render → Word / LaTeX（可选 --pdf / --template 按模板出）
        → 产物统一归到 output/<项目名>/（md + docx + tex + pdf + figures/）
        → 提示用户：LaTeX 源码可直接在 IDE（VS Code + LaTeX Workshop）打开编辑实时预览
```

**各环节硬约束**：
- **元信息提问优先于内容生成**：① 未完成（用户未回答/跳过）不得进入 ②；作者/学校/日期是论文必备元信息
- **内容确认优先于格式转换**：② 内容预览、⑤ 图描述、⑥ 图审核三步必须用户确认后才继续
- **图表属于视觉产物**：不确认不进文档（禁止未确认直接插入）；**图描述未确认不得写 HTML**
- **中文标点与空格（输出硬约束）**：AI 产 MD 必须用中文标点（“”‘’，。：；？！（）、《》），中英文/数字之间不留半角空格；引擎入口 text_norm.py 会自动清洗兑底（护栏层），但源头规范可避免歧义
- **禁止 ASCII 字符画**：任何图都必须经双引擎之一渲染为 PNG（diagram-design / mermaid）；**字符画、文本框线图、"示意图"占位一律不得进入文档**——画不了就走图描述环节与用户沟通，不许降级
- **插入的图片必须带图注**；补充说明用 `> 注：` 注释块
- **用户未要求图时**：AI 主动分析（见下方智能分析映射表），适合就提问，不适合不说
- **产物目录统一**：最终交付集中到 `output/<项目名>/`（Markdown 源 / Word docx / LaTeX tex / PDF / figures 图片），便于查看编辑

### 触发词识别

当用户输入包含以下关键词时，进入对应流程：

| 用户意图 | 关键词示例 | 处理流程 |
|----------|-----------|----------|
| 写文档/文章/报告 | "写文档"、"写文章"、"写报告"、"写方案"、"帮我写"、"生成文章" | **走文档生成主流程：内容 → 预览 → 图表建议 → 插入 → Word/LaTeX** |
| 生成 Word 文档 | "写word"、"生成word"、"word文档"、"docx"、"公文"、"学术论文word" | **先出 MD 中间态 → md_to_word.py 渲染** |
| 按用户模板填充 | "按模板"、"模板填充"、"套用模板"、"docxtpl"、"填写模板"、"根据模板生成" | **extract schema → AI 产 data.json → render（docxtpl 保真）** |
| 总结报告/总结文档 | "总结报告"、"总结文档"、"写总结"、"生成总结" | **先总结后转换** |
| 输出 PDF | "输出 PDF"、"生成 PDF"、"转 PDF" | 确认源材料后转换编译 |
| 输出 LaTeX | "输出 LaTeX"、"生成 LaTeX"、"转 latex"、"写 tex" | 确认源材料后转换 |
| MD/DOCX 转 LaTeX | "md转latex"、"docx转pdf"、"markdown转tex" | 直接转换 |
| 手写 LaTeX | "写论文"、"写报告"、"写笔记" | 提供骨架模板 |
| 生成框架图 | "框架图"、"架构图"、"流程图"、"时序图"、"画个图"、"配图" | **先提问是否生成 → diagram-design 生成（可多类型选择）→ 渲染插入三条链路** |

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
| `> 副标题：xxx` | 副标题（紧随主标题下方，居中楷体） |
| `> 作者：xxx`（如 `张三 计算机学院 2025000101`） | 作者（居中楷体四号 14pt） |
| `> 单位：xxx` / `> 学校：xxx` | 学校/单位（居中楷体小字；LaTeX 并入作者行下方仿宋） |
| `> 日期：xxx` | 日期（居中仿宋；LaTeX 渲染为 `\date{}`） |
| 主标题后第一段裸文本（无 `> 前缀`，长度<60） | 作者（兼容旧写法，居中楷体） |
| `**摘要：** 内容` | 摘要（"摘要："黑体 + 内容楷体） |
| `**关键词：** 词1；词2` | 关键词（"关键词："黑体 + 内容楷体） |
| `# 一、引言`（后续 `# `） | 一级标题 Heading 1（进目录） |
| `## 2.1 小节` | 二级标题 Heading 2 |
| `### 3.1.1 小节` | 三级标题 Heading 3 |
| `#### 3.1.1.1 小节` | 四级标题 Heading 4 |
| 普通段落 | 正文（方正书宋，首行缩进，1倍行距） |
| 段落内 `**加粗**` | 黑体片段（中文字体加粗用黑体而非加粗样式） |
| `> 注：xxx` | 注释段落（仿宋，五号，灰色） |
| `> **表1：xxx**`（MD 中写在表格上方） | 表格标题（楷体居中，渲染时显示在**表格下方**） |
| `\| a \| b \|` 表格 | 表格（表头黑体居中，内容居中） |
| `> 注：xxx`（表格下方） | 表格注释 |
| `- 项目` / `1. 项目`（缩进 2 空格嵌套） | 列表（无序 •/◦、有序保留编号，按层级缩进） |
| `![图1：xxx](path.png)` | 图片（图注下方；文件缺失自动占位） |
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

# 指定输出路径 / 不自动更新目录 / 同会话导出 PDF
python md_to_word.py input.md -o output.docx
python md_to_word.py input.md --no-toc
python md_to_word.py input.md --pdf
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

### 场景D：模板注册表（模板库管理 → 按模板出文档）

**核心：注册表是模板的"中央元数据单点"。模板入库 → 自动提取 schema → AI 按 schema 受约束产出 → 引擎渲染保真。LLM 不直接动模板文件（对齐 arXiv 双轨框架）。**

目录：`templates/registry/`（manifest.json 索引 + word/latex/markdown 模板库 + schemas/ + previews/）。内置模板：harryopo-paper / harryopo-report / harryopo-notes（LaTeX）+ docxtpl-example（Word）。

```powershell
cd .trae/skills/harryopo-office/scripts/word/template

# 模板入库（docx 自动提取 schema；可指定分类/名称/id/标签）
python template_registry.py add 公文模板.docx -c 用户自定义 -n 公文模板 --tags 公文 红头

# 发现与查询
python template_registry.py list                      # 全部
python template_registry.py list -f docx             # 按格式
python template_registry.py search 报告              # 名称/id/标签模糊
python template_registry.py describe harryopo-report # 详情 + schema 摘要

# schema（AI structured output 依据）
python template_registry.py schema harryopo-report -o schema.json

# 移除（内置模板需 --force）
python template_registry.py remove user-xxx --force -d   # -d 同时删文件

# office.py 统一入口（template 子命令透传注册表 CLI）
python office.py template list
python office.py render input.md --template harryopo-report   # 按模板路由渲染链路
```

**AI 按模板出文档工作流**：
```
1. template list / search → 找到模板 id
2. template describe <id> → 了解模板字段与引擎
3. docx 模板：schema <id> → 按 schema 向用户确认字段 → 产出 data.json → docx_template.py render
4. latex 模板：AI 产 MD 内容 → office.py render input.md --template <id>（自动路由 paper/notes 链路）
```

**manifest 严格校验**：未知字段拒绝加载（对齐 M365 Copilot），内置模板受删除保护。

### 图表生成与插入流程（diagram-design 编辑级图表 · 39 类型）

**核心闭环**：AI 智能分析 → 用户确认 → diagram-design 生成（39 类型编辑级图表）→ 渲染 PNG → 用户审核 → 插入 Word / LaTeX。用户未要求图时，AI 主动分析内容是否适合配图并给出建议。

#### 第1步：智能分析 & 触发（关键）

**触发条件**：

- **用户明确要求图**（"画个图"/"配图"/"架构图"/"流程图"/"时序图"等）→ 直接进入第2步
- **用户未要求** → AI 阅读文档内容后**主动判断是否适合配图**：

| 文档内容 | 建议？ | 建议图表（diagram-design 类型） |
|----------|--------|-------------------------------|
| 系统架构、模块划分、技术栈层次 | ✅ 建议 | Architecture（架构图） |
| 业务流程、编排流水线、决策逻辑 | ✅ 建议 | Flowchart / Process / Data flow |
| 调用链、消息交互、多角色时序 | ✅ 建议 | Sequence（时序图） |
| 跨部门/多角色协作流程 | ✅ 建议 | Swimlane（泳道图） |
| 实体关系、数据模型、数据库表 | ✅ 建议 | ER / Database schema |
| 优先级/两维对比 | ✅ 建议 | Quadrant（象限图） |
| 数据分布、趋势、占比 | ✅ 建议 | Bar / Line / Treemap |
| 简单列表、纯文字说明 | ❌ 不建议 | （用表格/正文即可） |

给用户一句具体建议（例如："文档涉及系统架构，建议配一张架构图，是否生成？"）→ 用户确认 → 第2步；用户拒绝 → 跳过（**禁止擅自生成**）。**内容适配多类型时给出选择**（例如："这段内容可配【架构图 / 时序图】，要生成哪个？"）。

#### 第2步：引擎选型

| 场景 | 引擎 | 说明 |
|------|------|------|
| **编辑级图表（首选）** | **diagram-design** | 39 类型 × 3 变体（极简亮/暗/全编辑），白纸黑字编辑风，可配品牌色；`skills/diagram-design/` |
| 快速简单流程图 | mermaid | `` `mermaid` `` 代码块，渲染器自动转 PNG |

> 图表引擎只有以上两个（super-diagram 已于 2026-09-02 移除，收敛决策）：架构/时序等复杂图一律走 diagram-design。

#### 第3步：图描述 MD（画图前必须 · 用户确认）

写 HTML 之前，先产出一份**图描述 MD** 给用户确认（文字成本远低于 HTML 返工）：

```markdown
## 图1 描述：多智能体编排平台架构

- 图类型：架构图（Architecture，diagram-design）
- 画布：960×560，light 主题，焦点色 #0c8599
- 节点（6）：
  | 节点 | 角色 | 层 |
  |------|------|-----|
  | 用户 | 入口 | 接入层 |
  | API 网关 | 路由/鉴权 | 接入层 |
  | 编排引擎 | 核心调度 | 编排层 |
  | 智能体池 | 执行单元 | 执行层 |
  | 向量库 | 记忆/检索 | 基础设施 |
  | 关系数据库 | 持久化 | 基础设施 |
- 连线：用户→网关(对话)、网关→编排(请求)、编排→智能体池(调度)、
  智能体池→向量库(检索)、编排→关系库(落盘)
- 布局：四层自上而下，同层水平排布，边标签在线段中点
```

用户确认描述（或提出修改）→ 进入第4步；**描述未确认禁止写 HTML**。

#### 第4步：生成（diagram-design 流程）

1. **读规范**：加载 `skills/diagram-design/SKILL.md` + 对应 `references/type-*.md`（按图类型选），先确认 type/size/复杂预算
2. **写 HTML**：复制 `skills/diagram-design/assets/template.html`（或 `-dark`/`-full`）为底，按规范手写 SVG：
   - **语义 token**：`paper` 底 / `ink` 文字 / `muted` 次级 / `accent` 焦点色（≤2 个元素）；**中文环境字体栈必须补 `'Microsoft YaHei'`** fallback（模板原字体 Geist/Instrument Serif 无中文）
   - **4px 网格**：所有 x/y/字号/间距必须被 4 整除
   - **6 条连接器规则**：正交圆角 r=8、箭头标签距线 6-10px、连接器不重叠、同边 fan-out ≥12px、不穿非端点盒子、标签遮罩不压节点
   - **密度 4/10**：≤9 节点、≤12 箭头；超过则拆图（overview + detail）
   - **无障碍**：`<svg role="img" aria-labelledby>`，`<title>` 第一个子元素，slug 前缀 ID
3. **保存 HTML** → `figures/图N-描述.html`
4. **渲染 PNG + 自检**：
   ```powershell
   cd .trae/skills/harryopo-office/scripts
   python office.py diagram figures/图N-描述.html -o figures/图N-描述.png --svg --check
   ```
   （`--svg` 只截 SVG 区域不含标题；`--check` 先跑 self_check.py 验证）

#### 第5步：用户审核（关键闭环）

渲染出 PNG 后，**必须先把图展示给用户确认是否满意**：
- 满意 → 进入第6步
- 不满意 → 按用户反馈修改 HTML（拓扑/坐标/配色/图注）→ 重新渲染 → **直到用户满意再继续**（禁止未确认直接插入文档）
- 若偏差源于对内容的理解（而非画法）→ 回到第3步改图描述再重画

> 图表属于视觉产物，用户是否认可必须人工确认——内容确认优先于格式转换，图确认优先于文档生成。

#### 第6步：智能插入（写好注释）

审核通过后，在 MD 中间态对应位置写图片引用（**图注必须完整**：`图N：` 编号 + 说明文案，写在 `![]()` 的 alt 里）：

```markdown
![图3：多智能体编排平台架构](figures/图3-多智能体编排.png)

> 注：本图展示接入层、编排层、智能体执行层与基础设施的关系。
```

需要补充说明时，紧跟图片后加 `> 注：xxx` 注释块（渲染为仿宋灰色注释）。**插入位置与正文逻辑衔接**：图应紧跟首次引用它的段落之后。

---

**备选引擎流程（mermaid）**：AI 在 MD 中嵌入 mermaid 代码块，`office.py render` 自动识别并渲染：

- **mermaid**：````mermaid` 代码块（简单流程图；架构/时序等复杂图走 diagram-design）
- **渲染**：`office.py render` 自动识别代码块 → PNG → 图片引用 → 双链路（Word / LaTeX）

> ` ```super-diagram ` 代码块已不再支持（引擎已于 2026-09-02 移除）：渲染时会报错并提示改用 diagram-design。

**依赖**：diagram-design 渲染需 `playwright`（含 chromium，`office.py diagram` 委托 `diagram_design_render.py`）；mermaid 需 `mmdc`。

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

### 方式C：MD/DOCX → paper/report（convert.py）

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
| `- item` | `\begin{itemize}\item` | 无序列表（缩进 2 空格嵌套） |
| `1. item` | `\begin{enumerate}\item` | 有序列表（缩进 2 空格嵌套） |
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
- **模板填充**：`docxtpl`（`pip install docxtpl`，docxtpl 模板子 skill 用）
- **中文字体**：方正方案需系统已装方正 GBK 字体；开源方案用 Windows 自带宋体/黑体/楷体/仿宋

### LaTeX 流程
- **必需**：Python 3.7+、xelatex (TeX Live 2024+)、fontspec v2.9+
- **推荐**：Pandoc 3.10+（MD→LaTeX 最优引擎，已安装于 `%LOCALAPPDATA%\Pandoc\`）
- **DOCX 转换**：office.py 首选 `anydoc`（`pip install firecrawl-anydoc`，无图文档毫秒级转换，GFM 表格原生），MinerU 3.0+（`pip install -U "mineru[all]"`）+ python-docx
- **字体**：已内嵌于 `templates/fonts/`，无需单独安装
- **关键**：fontspec v2.9+ 语法要求 `\setCJKmainfont{FONTNAME}[options]`（name 在前），反之为 `[options]{name}` 会导致方正字体加载失败并回退到 ctex 默认字体

### 图表流程
- **diagram-design 渲染**：`playwright`（`pip install playwright` + `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/ python -m playwright install chromium`），`office.py diagram` 委托 `diagram_design_render.py`
- **mermaid**：`mmdc`（`npm install -g @mermaid-js/mermaid-cli`，含 puppeteer chromium）
