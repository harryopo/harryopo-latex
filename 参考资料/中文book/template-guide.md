# 中文 KaoBook 模板使用指南

> 基于 [kaobook](https://github.com/fmarotta/kaobook) (v0.9.8) + [kaobookCJKsc](https://github.com/xuehao/kaobookCJKsc) 改造的中文书籍模板，专为 Windows + XeLaTeX 优化。

---

## 一、目录结构

```
中文book/
├── main.tex                    # 主文档入口
├── main.bib                    # 参考文献数据库
├── template-guide.md           # 本使用指南
├── styles/                     # 样式/类文件
│   ├── kaobookCJKsc.cls        #   文档类（基于 scrbook）
│   ├── kaoCJKsc.sty            #   核心样式包（页面布局、章节、TOC等）
│   ├── kaoWinCJKsc.sty         #   字体配置 + 定理环境 ★核心修改★
│   ├── kaobiblioCJKsc.sty      #   参考文献样式（GB/T 7714-2015）
│   ├── kaotheoremsCJKsc.sty    #   定理环境
│   ├── kaorefsCJKsc.sty        #   交叉引用
│   ├── kaohandtCJKsc.cls       #   （保留，未使用）
│   ├── packageconfig.tex       #   导言区配置
│   └── config.tex              #   文档内配置（中文名称、引用格式）
├── chapters/                   # 各章节 .tex 文件
│   ├── qianyan.tex             #   前言
│   ├── zhuyaoneirong.tex       #   主要特性
│   ├── xuanxiang.tex           #   选项设置
│   ├── wenbenbiaozhu.tex       #   文本标注
│   ├── tuxiangyubiaoge.tex     #   图像与表格
│   ├── yinyong.tex             #   引用
│   ├── paiban.tex              #   排版
│   ├── shuxue.tex              #   数学
│   ├── fulu.tex                #   附录（字体测试）
│   ├── zimubiao.tex            #   字母表（需 glossaries，默认禁用）
│   └── yizhexu.tex             #   译者序（默认禁用）
└── images/                     # 图片资源
```

---

## 二、字体规范

| 用途 | 字体 | 命令 | 文件名 |
|------|------|------|--------|
| 最大标题 | 方正小标宋 | `\fzxiaobiaosong` | `FZXBSJW.ttf` |
| 次级标题 | 方正黑体 | `\fzhei` / `\yh` | `FZHei-B01.ttf` |
| 正文 | 方正书宋 | `\fzsong` (默认) | `方正书宋_GBK.ttf` |
| 其他板块 | 方正楷体 | `\fzkai` | `方正楷体_GBK.ttf` |
| 侧边注释 | 方正仿宋简体 | `\fzfs` | `方正仿宋_GBK.ttf` |
| 代码/公式 | Cascadia Code / Consolas / Courier New | 自动选择 | — |

**装饰字体**（非核心功能）：

| 字体 | 命令 | 文件名 |
|------|------|--------|
| 方正隶书 | `\fzli` | `FZLSJW.ttf` |
| 方正舒体 | `\fzshti` | `FZSTJW.ttf` |
| 方正姚体 | `\fzyao` | `FZYTJW.ttf` |

**系统备用字体**：宋体 (`\song`)、黑体 (`\hei`)、楷体 (`\kai`)、仿宋 (`\fs`)、等线 (`\dx`)、新宋体 (`\xs`)

---

## 三、快速开始

### 1. 环境要求

- **编译器**：XeLaTeX（必须！不支持 pdfLaTeX/LuaLaTeX）
- **发行版**：TeX Live 2025 或更新
- **操作系统**：Windows 10/11（字体路径硬编码为 `C:/Windows/Fonts/`）
- **必需字体**：
  - 方正书宋_GBK.ttf
  - FZHei-B01.ttf（方正黑体）
  - 方正楷体_GBK.ttf
  - 方正仿宋_GBK.ttf（方正仿宋简体）
  - FZXBSJW.ttf（方正小标宋）

### 2. 编译

```powershell
# 清理旧文件
Remove-Item main.aux, main.toc, main.out, main.pdf -ErrorAction SilentlyContinue

# 首次/修改交叉引用后（运行3遍）
xelatex -synctex=1 main.tex
xelatex -synctex=1 main.tex
xelatex -synctex=1 main.tex

# 如需处理参考文献
biber main
xelatex -synctex=1 main.tex
```

### 3. 新建自己的文档

1. 复制 `main.tex` 为你的文件名
2. 修改标题、作者、日期等元信息
3. 替换 `chapters/` 中的内容
4. 替换 `images/` 中的图片
5. 编译

---

## 四、关键配置说明

### 文档类选项 (`main.tex`)

```latex
\documentclass[
    a4paper,           % 纸张大小
    fontsize=10pt,      % 字号（10pt/11pt/12pt）
    twoside=false,      % 单面/双面排版
    open=any,           % 新章节起始页
    chapterentrydots=true,
    numbers=noenddot,
]{styles/kaobookCJKsc}
```

### 标题页字体 (`main.tex` 第136行)

```latex
{\color{titlecolorcoverpage}\Huge\fzxiaobiaosong \textbf{\@title} \par}
```

- 主标题用 `\fzxiaobiaosong`（方正小标宋）
- 副标题用 `\yh`（方正黑体）
- 作者/日期用 `\yh`（方正黑体）

### 目录字体 (`styles/kaoCJKsc.sty`)

目录中 part 标题使用 `\yh\large`，章节标题使用 `\yh`（方正黑体）。

### 边注字体 (`styles/kaoWinCJKsc.sty` 第95行)

```latex
\renewcommand*{\marginfont}{\fzfs\footnotesize\justifying\frenchspacing}
```

边注统一使用 `\fzfs`（方正仿宋）。

### 标题字体 (`styles/kaobookCJKsc.cls`)

KOMA-Script 标题字体：
- `\addtokomafont{part}` → `\yh`
- `\addtokomafont{chapter}` → `\yh`
- `\addtokomafont{section}` → `\yh`
- `\addtokomafont{subsection}` → `\yh`

---

## 五、常用功能

### 章节标题样式

```latex
\setchapterstyle{plain}   % 默认样式
\setchapterstyle{kao}     % 边注样式（主体部分推荐）
\setchapterstyle{lines}   % 线条样式
\setchapterstyle{bar}     % 灰色条样式

% 带背景图的章节
\setchapterimage[8cm]{path/to/image.jpg}
```

### 页面布局

```latex
\pagelayout{margin}    % 宽边注布局（默认，适合正文）
\pagelayout{wide}      % 无边注宽布局（适合前言/附录）
\pagelayout{fullwidth} % 完全无边距
```

### 边注与脚注

```latex
\sidenote{边注内容}
\marginnote{边注内容}
\footnote{脚注内容}
```

### 宽段落

```latex
\begin{widepar}
  横跨正文+边注区域的宽段落
\end{widepar}
```

### 定理环境（需 `[testMathBox]` 选项）

当前 `packageconfig.tex` 中已启用 `\usepackage[testMathBox]{styles/kaoWinCJKsc}`，提供：
- `Definition` / `Theorem` / `Lemma` / `Corollary`
- `Proposition` / `Proof` / `Example` / `Solution`
- 彩色盒子：`theo`、`lem`、`prf`、`soln`

### 分页引用

```latex
\refpage{label}   % 输出"第 X 页"
\refch{label}     % 输出"第 X 章"
\refsec{label}    % 输出"第 X 节"
```

---

## 六、添加字体

如需添加新的方正字体，编辑 `styles/kaoWinCJKsc.sty`：

```latex
% 定义新字体族
\setCJKfamilyfont{fzxxx}[Path=\fontpath, Extension=.ttf]{FZXXXJW}
\newcommand{\fzxxx}{\CJKfamily{fzxxx}}
```

在 `C:\Windows\Fonts` 中确认字体文件名后再添加。

---

## 七、常见问题

### 1. 编译报错 "The font XXX cannot be found"

说明系统中缺少对应的方正字体文件。检查 `C:\Windows\Fonts\` 中是否存在该 `.ttf` 文件，如不存在需安装。

### 2. "Font shape TU/XXX/m/sl undefined"

中文斜体/粗体变体不存在时 LaTeX 会自动替换，属正常警告，不影响输出。

### 3. 参考文献不显示

先运行 `biber main`，再运行 `xelatex`。

### 4. 交叉引用显示为 "??"

需要再运行一次 XeLaTeX 以稳定交叉引用。

### 5. 更换为非 Windows 系统

需修改 `kaoWinCJKsc.sty` 中的 `\fontpath`（第24行），改用系统字体名称（不带 Path）。

---

## 八、版本历史

- **2026-06-21**：迁移至方正家族字体体系，清理冗余字体命令，修复 fulu.tex 字体测试页
- 原始 fork：[kaobookCJKsc](https://github.com/xuehao/kaobookCJKsc)
- 原始模板：[kaobook](https://github.com/fmarotta/kaobook) v0.9.8
