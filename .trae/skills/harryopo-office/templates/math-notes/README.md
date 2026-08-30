# harryopo-mathnotes

> 数理笔记 LaTeX 模板 —— 色块 + 侧边竖线 · 宽边注 · 方正字体 · XITS 数学 · Pandoc MD→LaTeX

适用于高等数学、数学分析、线性代数等数理类学习笔记的排版。基于 `extarticle`（9pt）构建，支持 `twoside` 奇偶页对称边距。支持 **Markdown 一键转 PDF**（Pandoc + Lua Filter）。

---

## 快速开始

### 方式A：Markdown → PDF（推荐）

```powershell
# 一键转换 + 编译（Pandoc 引擎，默认）
python md2latex.py example-note.md --engine pandoc --clean

# 或：纯 Python 引擎（无需 Pandoc）
python md2latex.py example-note.md --engine python --clean

# 仅生成 .tex，不编译
python md2latex.py example-note.md --tex-only
```

### 方式B：手写 .tex

```bash
xelatex main.tex    # 第 1 遍
xelatex main.tex    # 第 2 遍（生成目录 + 交叉引用）
xelatex main.tex    # 第 3 遍（稳定交叉引用）
```

或使用编译脚本：

```powershell
.\build.ps1          # 自动编译 3 遍
.\build.ps1 -Clean   # 清理临时文件
```

---

## Markdown → LaTeX 映射（Pandoc 引擎）

| Markdown | LaTeX | 说明 |
|----------|-------|------|
| `# Title` | `\section{Title}` | 一级标题 → "一、Title" |
| `## Title` | `\subsection{Title}` | 二级标题 → "1.1 Title" |
| `### Title` | `\subsubsection{Title}` | 三级标题 |
| `**bold**` | `\textbf{bold}` | AST 级解析 |
| `*italic*` | `\textit{italic}` | AST 级解析 |
| `` `code` `` | `\texttt{code}` | 行内代码 |
| `- item` / `1. item` | `\begin{itemize/enumerate}` | 嵌套列表 |
| `\| a \| b \|` | `\begin{table}...tabularx` | Lua 智能表格 |
| `$x^2$` | `\(x^2\)` | 行内公式 |
| `$$ E=mc^2 $$` | `\[ E=mc^2 \]` | 块级公式 |
| `> quote` | `\begin{quote}` | 引用 |

---

## 环境依赖

### TeX 发行版

- **TeX Live 2024+** 或 **MiKTeX**（需含 `xelatex`）

### 推荐工具

- **Pandoc 3.10+**（MD→LaTeX 最优引擎，已安装于 `%LOCALAPPDATA%\Pandoc\`）
- **Python 3.7+**（纯 Python 引擎备选，零依赖）

### 必需宏包

所有宏包均可在 CTAN 获取，由模板自动加载：

| 宏包 | 用途 |
|------|------|
| `fontspec`, `xeCJK`, `ctex` | 字体与中文支持 |
| `unicode-math` | XITS Math 数学字体 |
| `amsmath`, `amsthm` | 数学排版与定理 |
| `geometry` | 页面布局 |
| `mdframed`, `framed` | 色块框架 |
| `marginnote`, `marginfix` | 边注 + 防重叠 |
| `caption`, `subcaption` | 浮动体标题 |
| `titlesec` | 节标题格式 |
| `fancyhdr` | 页眉页脚（智能：奇数页=子节，偶数页=节） |
| `tabularx`, `booktabs` | 表格自动换行 + 三线表 |
| `xcolor[svgnames,table]` | 颜色 + 隔行着色表格 |
| `hyperref` | 超链接交叉引用 |
| `setspace` | 行距控制 |
| `graphicx`, `adjustbox` | 图片排版 |
| `changepage` | 页面调整 |

### 字体配置

#### 西文字体（已内嵌）

模板自带 XITS 和 TeX Gyre Heros 字体，存放在 `fonts/` 目录中，**开箱即用无需安装**。

| 字体 | 用途 | 许可证 |
|------|------|--------|
| XITS（Regular/Bold/Italic） | 正文 | SIL OFL |
| XITS Math | 数学公式 | SIL OFL |
| TeX Gyre Heros | 无衬线标题 | SIL OFL |

若 `fonts/` 目录被删除，模板会自动回退到系统字体（Times New Roman / Arial / TeX Gyre Termes Math）。

#### 中文字体（方正系列，推荐安装）

模板优先使用方正系列字体以获得最佳排版效果。若系统中无方正字体，会自动回退到系统自带中文字体（宋体/黑体/楷体/仿宋）。

---

## 文件结构

```
math-notes/
├── harryopo-mathnotes.cls   # 文档类（核心）
├── md2latex.py              # MD→LaTeX 转换脚本（Pandoc + Python 双引擎）
├── example-note.md          # MD 示例（高等数学笔记）
├── main.tex                 # 手写示例文档
├── main.pdf                 # 编译输出（15 页）
├── build.ps1                # 编译脚本
├── README.md                # 本文件
├── pandoc/                  # Pandoc 集成
│   ├── mathnotes-template.latex  # 自定义 LaTeX 模板
│   └── mathnotes-table.lua       # 智能表格 Lua Filter
├── fonts/                   # 西文字体（XITS / TeX Gyre Heros）
├── image/                   # 图片目录（自定义）
├── images/                  # 备选图片目录
├── figures/                 # 备选图片目录
└── fig/                     # 备选图片目录
```

---

## 文档类选项

```latex
\documentclass{harryopo-mathnotes}
```

无额外选项。页面为 A4 + 9pt + twoside，左侧 2.3cm 正文、右侧 6cm 边注栏。

---

## 封面设置

在导言区重新定义以下命令：

```latex
\renewcommand{\mathtitle}{数理笔记模板}          % 标题
\renewcommand{\mathauthor}{张三}               % 作者
\renewcommand{\mathaffiliation}{harryopo · 数学教研室}  % 单位
\renewcommand{\mathinfo}{%                        % 附加信息（可选）
  {\Large\fzfs 学科: 高等数学}
  \vspace{0.6cm}
  {\Large\fzfs 日期: \today}
}
```

封面为右对齐布局：标题 → 天蓝分隔线 → 作者 → 附加信息 → 单位 → 版权。

---

## 命令与环境参考

### 字体快捷命令

| 命令 | 字体 |
|------|------|
| `\fzdbs` | 方正大标宋 |
| `\fzht` | 方正黑体 |
| `\fzkt` | 方正楷体 |
| `\fzfs` | 方正仿宋 |
| `\fzxbs` | 方正小标宋 |

### 节标题

```latex
\section{函数与极限}           % → "一、函数与极限"（中文编号 + 顿号）
\subsection{函数的概念}         % → "1.1 函数的概念"（阿拉伯数字）
\subsubsection{函数的表示法}    % → "1.1.1 函数的表示法"（阿拉伯数字）
```

| 层级 | 编号格式 | 字体/颜色 |
|------|----------|-----------|
| `\section` | 一、二、三... | 大标宋 + DeepSkyBlue |
| `\subsection` | 1.1, 1.2... | 小标宋 + DeepSkyBlue |
| `\subsubsection` | 1.1.1, 1.1.2... | 黑体 + DeepSkyBlue |

### 页眉页脚（智能切换）

模板自动设置奇数页/偶数页不同页眉：
- **奇数页**右侧：当前 `\subsection` 标题
- **偶数页**左侧：当前 `\section` 标题
- 页脚居中：页码

无横线分隔（`\headrulewidth=0pt`）。

### 定义块（formal 包裹）

```latex
\begin{formal}
\begin{definition}[函数极限]
  设函数 $f(x)$ 在点 $x_0$ 的某个去心邻域内有定义...
\end{definition}
\end{formal}
```

`formal` 环境提供灰色竖线 + 浅灰背景。其内可使用：

| 环境 | 输出 | 编号方式 |
|------|------|----------|
| `definition` | 定义 | 共享计数器 |
| `theorem` | 定理 | 共享计数器 |
| `lemma` | 性质 | 共享计数器 |
| `corollary` | 推论 | 共享计数器 |
| `example` | 例 | 独立计数器 |

### 例题与解答

```latex
\begin{example}\label{ex:sinxx}
  求极限 $\lim_{x\to 0}\frac{\sin x}{x}$
\end{example}
\begin{answer}
  \textbf{答：} 由重要极限公式...
\end{answer}
```

`answer` 环境为淡蓝背景框，适合展示解答过程。

### 注解标注

```latex
\begin{attention}
  极限存在的充要条件是左右极限存在且相等。
\end{attention}

\begin{tips}
  求解 0/0 型极限时，优先考虑因式分解...
\end{tips}

\begin{warns}
  使用洛必达法则前，必须验证不定型条件。
\end{warns}
```

三种标注均为左侧竖线 + 淡蓝背景，颜色由深到浅区分层次：

| 环境 | 竖线颜色 | 用途 |
|------|----------|------|
| `attention` | 深天蓝 RGB(0,130,215) | 重要提醒 |
| `tips` | 中天蓝 RGB(60,165,230) | 方法技巧 |
| `warns` | 浅天蓝 RGB(135,200,240) | 常见错误 |

### 侧边注解

```latex
% 纯文字边注
\bianzhu[边注标题]{边注正文内容...}

% 无标题边注
\bianzhu{只有正文内容...}

% 带图片的边注
\bianzhutu[图片标题]{example-image-a}{图片说明文字...}
```

边注使用 `marginpar` + `marginfix`，自动防纵向重叠、奇偶页位置自动切换。

### 习题

```latex
\begin{exercise}[题目描述]
  求函数的导数：$f(x) = x \cdot e^x \cdot \sin x$
\end{exercise}
```

习题按节自动编号（如"习题 1.1"），支持 `\label` / `\ref` 交叉引用。

### 表格（tabularx + booktabs）

推荐使用 `tabularx` 配合比例 X 列和 `booktabs` 三线表。表格 caption 自动放在下方。

```latex
\begin{table}[htbp]
  \centering
  \begin{tabularx}{\textwidth}{>{\hsize=0.7\hsize\linewidth=\hsize\raggedright\arraybackslash}X>{\hsize=1.3\hsize\linewidth=\hsize\raggedright\arraybackslash}X}
    \toprule
    \textbf{函数} & \textbf{导数} \\
    \midrule
    $x^n$ & $nx^{n-1}$ \\
    $\sin x$ & $\cos x$ \\
    \bottomrule
  \end{tabularx}
  \caption{基本求导公式}
\end{table}
```

**关键要点：**
- 多列 `\hsize` 之和必须等于列数（如2列：0.7+1.3=2.0）
- X 列内容过长时自动换行，不会溢出页边距
- 数字列可用 `\centering\arraybackslash` 替代 `\raggedright`
- Pandoc + Lua Filter 自动生成比例 X 列（无需手写）

### 浮动体（图片）

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.55\textwidth]{example-image-b}
  \caption{图片说明}\label{fig:example}
\end{figure}
```

Caption 自动输出中文"图 1""表 1"，字体为方正仿宋 footnotesize。

### 交叉引用

```latex
\label{def:limit}           % 设置标签
\ref{def:limit}             % 引用编号
\eqref{eq:divergence}       % 引用公式（带括号）
图~\ref{fig:example}        % 图表引用
```

`hyperref` 已启用 `colorlinks, linkcolor=black`，引用文字为黑色可点击链接。

### 附录

```latex
\cleardoublepage
\appendix
\section{常用公式表}
...
```

附录自动切换为中文编号（"附录一""附录二"...），习题编号同步更新。

### 参考文献

```latex
\begin{thebibliography}{99}
  \bibitem{tao} Terence Tao, \textit{Analysis I}, 2006.
\end{thebibliography}
```

---

## 页面参数

| 参数 | 值 |
|------|-----|
| 纸张 | A4 (210mm × 297mm) |
| 基础字号 | 9pt |
| 左页边距 | 2.3cm |
| 右页边距 | 6cm |
| 上边距 | 3cm |
| 下边距 | 2.5cm |
| 边注宽度 | 5.3cm |
| 边注与正文间距 | 12pt |
| 模式 | twoside（奇偶页对称） |

---

## 颜色方案

| 颜色 | 定义 | 用途 |
|------|------|------|
| DeepSkyBlue | SVG 标准色 | 封面、节标题、边注标题、习题编号 |
| `attnline` | RGB(0,130,215) | 注意竖线 |
| `attnbg` | RGB(228,242,255) | 注意背景 |
| `tipsline` | RGB(60,165,230) | 提示竖线 |
| `tipsbg` | RGB(238,249,255) | 提示背景 |
| `warnsline` | RGB(135,200,240) | 警告竖线 |
| `warnsbg` | RGB(245,251,255) | 警告背景 |
| `formalshade` | gray 0.95 | 定义块背景 |
| `defbar` | gray 0.55 | 定义块竖线 |
| `answerbg` | RGB(230,245,255) | 解答背景 |

---

## 自定义指南

### 调整颜色

编辑 `harryopo-mathnotes.cls` 中 `% 颜色定义` 段落的 `\definecolor` 命令。

### 调整页边距

编辑 `harryopo-mathnotes.cls` 中 `\leftblank`, `\rightblank`, `\topblank`, `\bottomblank` 长度定义。

### 替换字体

替换 `.TTF` 文件后，修改 `harryopo-mathnotes.cls` 中 `% 中文字体` 段落的字体文件名。

### 添加新环境

参照 `attention` / `tips` / `warns` 模式，使用 `\newmdenv` 定义 `mdframed` 框架，再用 `\newenvironment` 包装。

---

## 常见问题

**Q: 编译报错 "Font ... not found"**

A: 确认方正字体 `.TTF` 文件已安装至系统字体目录，或将 `.TTF` 放入项目目录。

**Q: 边注重叠**

A: 本模板已引入 `marginfix` 自动检测和调整。若仍有极端情况下重叠，需在正文中分散边注位置。

**Q: 如何去掉页码/页眉**

A: 使用 `\thispagestyle{empty}`（单页）或在导言区 `\pagestyle{empty}`（全局）。

**Q: Pandoc 表格内容超出页边距**

A: Lua Filter 已自动处理，使用比例 X 列（`\hsize=N\hsize`）。若仍有问题，检查 `mathnotes-table.lua` 中的列宽计算逻辑。

**Q: 表格中数学公式的 `|` 被拆分成多列**

A: Pandoc 引擎 AST 级原生保护，不会有此问题。Python 引擎已通过占位符法修复。

---

## 许可证

MIT License

---

## 致谢

- 方正字库：提供优质中文字体
- XITS 字体：高质量数学排版字体
- Pandoc：通用文档转换器
- LaTeX 社区：无数宏包贡献者
