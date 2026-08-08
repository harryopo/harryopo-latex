# harryopo LaTeX 通用模板调研报告

## 一、参考模板概览

| 模板 | 基础类 | 核心特色 | 适用场景 |
|------|--------|----------|----------|
| 双栏.tex | ctexart | `cuted` 跨栏摘要、`\upcite` 上标引用 | 学术短论文 |
| 中文book (kaobook) | kaobookCJKsc (KOMA-Script) | 宽边注、多布局切换、索引/术语表 | 学术专著、教材 |
| 橙色书籍 (textbook) | book | 6 种主题色、丰富教学盒、侧标导航、封面封底 | 教材、教学用书 |

---

## 二、各模板优势分析

### 2.1 双栏.tex — 学术短论文模板

**核心优势：**
- **简洁规范**：直接基于 `ctexart`，无额外复杂依赖
- **跨栏排版**：使用 `cuted` 包的 `strip` 环境实现摘要跨双栏
- **上标引用**：`\upcite` 命令实现上标角注引用
- **中文排版规范**：`\CTEXsetup` 统一设置标题格式

**可借鉴的设计：**
```latex
% 跨栏摘要
\begin{strip}
    \noindent \textbf{摘要} \quad 内容...
\end{strip}

% 上标引用
\newcommand{\upcite}[1]{\textsuperscript{\textsuperscript{\cite{#1}}}}
```

**不足：**
- 功能单一，无目录美化
- 无页眉页脚定制
- 封面页缺失

---

### 2.2 中文book (kaobook) — 学术专著模板

**核心优势：**
- **三种页面布局**：`margin`（宽边注）、`wide`（宽正文）、`fullwidth`（全宽）
- **专业边注系统**：`\marginnote`、`\sidenote`，自动编号
- **丰富的结构**：前言、目录、术语表、索引、参考文献
- **KOMA-Script 底层**：提供精细的排版控制
- **章节样式可切换**：`plain`、`kao`、`\chapterimage` 带图标题

**可借鉴的设计：**
```latex
% 三种布局切换
\pagelayout{margin}   % 宽边注
\pagelayout{wide}     % 宽正文
\pagelayout{fullwidth}% 全宽

% 边注
\marginnote{这是边注内容}

% 章节图片标题
\setchapterimage[8cm]{image.jpg}
\chapter{标题}
```

**不足：**
- 依赖 KOMA-Script，与标准 LaTeX 类不兼容
- 配置复杂，学习曲线陡峭
- 编译依赖链长

---

### 2.3 橙色书籍 (textbook) — 教学教材模板

**核心优势：**
- **6 种主题色**：BLUE、GREEN、RED、PURPLE、GRAY、FANCY
- **丰富的教学盒**：20+ 种盒子环境
  - 定义类：`Definition`、`Theorem`、`Lemma`、`Axiom`、`Proposition`、`Corollary`
  - 教学类：`Point`（要点）、`Case`（案例）、`Example`+`Answer`
  - 互动类：`Practice`（练习）、`Exercise`（习题）、`Thinking`（思考）
  - 拓展类：`Expansion`（拓展）、`History`（史话）、`STS`（科技社会）
  - 代码类：`PythonBox`
  - 专题类：`SpecialTopic`、`Test`（测试卷）
- **侧标导航**：页面右侧的彩色条形章节标记，随页面滚动
- **封面封底**：TikZ 绘制的专业封面（琴键装饰、渐变色块）
- **智能选择题**：`\xx{A}{B}{C}{D}` 自动根据选项长度排版为 1/2/4 列
- **双栏分屏**：`Paracol` 环境支持左文右图/代码
- **边注图片**：`\marginpic`、`\margintab`

**可借鉴的设计：**
```latex
% 主题切换
\documentclass[color=ORANGE]{textbook}

% 丰富的盒子
\begin{Definition}[定义名称]
    内容...
\end{Definition}

\begin{Theorem}[定理名称]
    内容...
\end{Theorem}

% 智能选择题
\xx{选项A}{选项B}{选项C}{选项D}

% 双栏分屏
\begin{Paracol}
    左栏文字...
    \switchcolumn
    右栏图片...
\end{Paracol}
```

**不足：**
- 依赖过多（minted、fontawesome5、pgfplots 等）
- 编译需要 `-shell-escape` 参数
- 面向教材场景，通用性受限

---

## 三、通用模板设计方案

### 3.1 设计原则

1. **学术优先**：参考双栏.tex 的简洁规范，避免过度花哨
2. **模块化**：共享基础包 + 独立文档类，按需加载
3. **标准兼容**：基于 ctexart/ctexbook，不依赖 KOMA-Script
4. **主题切换**：借鉴 textbook 的多色方案，但更克制
5. **编译简单**：XeLaTeX 单次编译即可，无需特殊参数

### 3.2 模板架构

```
templates/
├── harryopo-base.sty          # 共享基础包（字体/颜色/数学/超链接）
├── harryopo-report.cls        # 实验报告/课程报告
├── harryopo-paper.cls         # 学术论文（单栏/双栏）
├── harryopo-book.cls          # 书籍/教材
├── harryopo-notes.cls         # 学习笔记
├── build.ps1               # 编译脚本
└── examples/
    ├── example-report.tex
    ├── example-paper.tex
    ├── example-paper-twocolumn.tex
    ├── example-book.tex
    └── example-notes.tex
```

### 3.3 各模板功能矩阵

| 功能 | report | paper | book | notes |
|------|--------|-------|------|-------|
| 封面页 | 信息表式 | 标题式 | 独立封面 | 标题式 |
| 摘要 | tcolorbox | 内联 | 前言 | - |
| 目录 | 自动 | 自动 | 自动 | 自动 |
| 页眉页脚 | 节标题+页码 | 节标题+页码 | 章标题+页码 | 节标题+页码 |
| 主题色 | 3 色可选 | 3 色可选 | 3 色可选 | 3 色可选 |
| 章节美化 | 基础 | 基础 | 色块章标 | 基础 |
| 双栏模式 | - | ✓ | - | - |
| 教学盒 | - | - | 6 种 | 4 种 |
| 旁注 | - | - | ✓ | 6 色旁注 |
| 参考文献 | thebibliography | thebibliography | - | - |

### 3.4 主题色方案

| 主题 | MainColor | 风格描述 |
|------|-----------|----------|
| blue (默认) | #1A365D 深蓝 | 权威、稳重、学术 |
| green | #1D4044 墨绿 | 清新、自然、沉稳 |
| dark | #322659 深紫 | 深邃、典雅、庄重 |

### 3.5 字体方案

| 用途 | 英文 | 中文 |
|------|------|------|
| 正文 | Times New Roman | 书宋（方正） |
| 标题 | Arial / Helvetica | 黑体（方正） |
| 强调 | - | 楷体（方正） |
| 引用 | - | 仿宋（方正） |

### 3.6 教学盒设计（book/notes）

| 盒子 | 颜色 | 用途 |
|------|------|------|
| 核心概念 | 蓝色 | 定义、定理 |
| 示例讲解 | 绿色 | 例题、案例 |
| 提示技巧 | 青色 | 注意事项 |
| 注意警告 | 橙色 | 易错点 |
| 同步练习 | 紫色 | 习题 |
| 底层逻辑 | 深青 | 原理分析 |

---

## 四、与参考模板的对比

| 维度 | 双栏.tex | kaobook | textbook | **harryopo 通用模板** |
|------|----------|---------|----------|-------------------|
| 学习成本 | 低 | 高 | 中 | **低** |
| 编译复杂度 | 简单 | 复杂 | 复杂 | **简单** |
| 视观效果 | 朴素 | 专业 | 华丽 | **学术大气** |
| 功能丰富度 | 低 | 高 | 高 | **中** |
| 通用性 | 低 | 中 | 低 | **高** |
| 中文支持 | ctex | 自定义 | ctex | **ctex** |
| 依赖数量 | 少 | 多 | 极多 | **少** |

---

## 五、结论

harryopo 通用模板定位为 **"学术优先、简洁规范、易于使用"** 的中文学术模板系统，适合：
- 高校实验报告、课程论文
- 学术会议论文（双栏）
- 教材编写
- 学习笔记整理

核心设计理念：**用最少的依赖，实现最专业的排版效果。**
