---
name: "harryopo-latex"
description: "harryopo LaTeX 中文模板：生成论文/报告/笔记 PDF。支持从 Markdown/Word 自动转换，或手写 .tex。单双栏、蓝/黑主题、方正字体、XITS 数学、代码高亮、算法伪代码、三线表。Pandoc + Lua 智能表格（比例X列+自动换行）。混合编号（一、1.1）+ 智能页眉。触发词：latex、论文、报告、模板、PDF、tex、md转latex、word转latex、docx转pdf、markdown转tex、文档转换、读书笔记、数学笔记、数理笔记。"
---
# harryopo-latex

harryopo LaTeX 中文模板体系 —— 支持手写 .tex 和 MD/DOCX 自动转换（Pandoc + Lua Filter 或纯 Python），编译生成专业 PDF。

## 项目架构

```text
harryopo-latex/
├── SKILL.md                              # 本文件
├── scripts/
│   ├── convert.py                        # MD/DOCX → paper/report .tex（纯 Python）
│   ├── md2latex.py                       # MD → math-notes .tex（Pandoc 优先 + Python 回退）
│   ├── mineru_cli.py                     # DOCX/PDF → MD（MinerU 解析 + 清洗 + HTML表格转LaTeX）
│   ├── html_table_to_latex.py            # HTML 表格 → LaTeX（colspan/rowspan → multicolumn/multirow）
│   └── test-sample.md                    # 测试用 Markdown
└── templates/                            # 完整模板包（自包含）
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
| 总结报告/总结文档 | "总结报告"、"总结文档"、"写总结"、"生成总结" | **先总结后转换** |
| 输出 PDF | "输出 PDF"、"生成 PDF"、"转 PDF" | 确认源材料后转换编译 |
| 输出 LaTeX | "输出 LaTeX"、"生成 LaTeX"、"转 latex"、"写 tex" | 确认源材料后转换 |
| MD/DOCX 转 LaTeX | "md转latex"、"docx转pdf"、"markdown转tex" | 直接转换 |
| 手写 LaTeX | "写论文"、"写报告"、"写笔记" | 提供骨架模板 |

### 先总结后转换流程（关键）

**核心原则：内容确认优先于格式转换。**

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

### 方式A：MinerU DOCX → MD → LaTeX（DOCX 首选）

适用场景：用户上传 Word 文档（.docx），需要保留表格结构（含合并单元格）。

**MinerU 优势**：0.2 秒/页极速解析，原生 DOCX 支持，表格合并单元格（colspan/rowspan）精确保留为 HTML，公式识别业界 SOTA。

#### 前提

```powershell
# 安装 MinerU（首次）
pip install -U "mineru[all]"
# 下载模型（首次，选 modelscope + pipeline，约 2-3GB）
@("modelscope","pipeline") | mineru-models-download
```

#### 一键转换

```powershell
# DOCX → 清洗后 MD（含 HTML 表格转 LaTeX）
python scripts/mineru_cli.py input.docx -o output_dir/

# 然后用 convert.py 转 LaTeX
python scripts/convert.py output_dir/result.md --type paper --no-math
```

#### 处理流程

```
DOCX → [MinerU office 解析] → Markdown + HTML 表格
         → [mineru_cli.py 清洗] → 去标题加粗 + HTML 表格转 LaTeX
         → [convert.py] → paper/report .tex
         → [xelatex ×3] → PDF
```

#### 表格处理（核心能力）

| 表格类型 | MinerU 输出 | LaTeX 生成 |
|----------|------------|-----------|
| 简单表 | HTML `<table>` | tabularx + booktabs 三线表 |
| 水平合并 | `colspan="N"` | `\multicolumn{N}{c}{...}` |
| 垂直合并 | `rowspan="N"` | `\multirow{N}{*}{...}` |
| 跨页长表（>20行） | HTML `<table>` | longtable + \endhead/\endfoot |

**注意**：multirow 与 tabularx 冲突，含合并单元格的表自动切换为固定列宽 tabular。

#### 加粗→黑体规则

中文排版规范：MD 的 `**加粗**` 统一转为 `\fzht{}`（方正黑体），而非 `\textbf{}`（中文字体加粗后笔画糊）。此规则在 convert.py 和 html_table_to_latex.py 中均已实现。

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
| `**bold**` | `\textbf{bold}` | 粗体 |
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
5. **DOCX 支持**：需 `pip install python-docx` 或 `winget install pandoc`
6. **标题无编号**：convert.py 已改为 `\section*`/`\subsection*` 系列，目录通过 `\addcontentsline` 保留；`.cls` 中重定义 `\thesection` 等为空，手写 .tex 也生效
7. **表格自适应**：convert.py 生成的表格使用 `tabularx{\textwidth}{>{\raggedright\arraybackslash}X...}`，caption 在下方；手写时同理，避免固定列宽导致越界
8. **图片 caption**：独立行图片 `![](alt|path)` 自动识别为 `\begin{figure}...\caption{alt}...\end{figure}`，caption 在图下方
9. **字体加载关键**：`harryopo-base.sty` 中 fontspec 语法必须是 `\setCJKmainfont{FZSSJW}[options]`（name 在前），否则方正字体加载失败并回退到 ctex 默认；所有 `\newfontfamily`/`\newCJKfontfamily` 需指定 `BoldFont=...` 自指，避免 "Font shape undefined" 警告

### math-notes
6. **独立体系**：math-notes 不加载 `harryopo-base.sty`，不要引入 base.sty（mdframed 与 tcolorbox 冲突）
7. **Pandoc 优先**：md2latex.py 默认使用 Pandoc 引擎；无 Pandoc 时自动回退到纯 Python
8. **三遍编译**：必须 xelatex×3 确保 TOC 和交叉引用稳定
9. **比例 X 列**：表格用 `>{\hsize=N\hsize\linewidth=\hsize}X`，多列 `\hsize` 之和 = 列数
10. **数学保护**：Pandoc 引擎原生 AST 级保护表格中的 `|` 不会被误解析
11. **字体体系**：独立使用 XITS + TeX Gyre Heros，不加载 harryopo-base.sty 的方正字体配置

---

## 依赖

- **必需**：Python 3.7+、xelatex (TeX Live 2024+)、fontspec v2.9+
- **推荐**：Pandoc 3.10+（MD→LaTeX 最优引擎，已安装于 `%LOCALAPPDATA%\Pandoc\`）
- **可选**：python-docx（DOCX 支持）
- **字体**：已内嵌于 `templates/fonts/`，无需单独安装
- **关键**：fontspec v2.9+ 语法要求 `\setCJKmainfont{FONTNAME}[options]`（name 在前），反之为 `[options]{name}` 会导致方正字体加载失败并回退到 ctex 默认字体
