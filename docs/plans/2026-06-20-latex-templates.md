# LaTeX 通用模板体系实施计划

> **For agentic workers:** 按 task 顺序实施，每个 task 对应一个文件的创建。使用 checkbox (`- [ ]`) 跟踪进度。

**Goal:** 创建一套美观、层级清晰、结构完整的 4 场景 LaTeX 通用模板体系（报告/论文/书籍/笔记），兼容 XeLaTeX + 中文。

**Architecture:** 一层共享基础包 `harryopo-base.sty` + 四层场景文档类 `.cls`，共享字体/颜色/代码高亮/数学配置，每层按需扩展。

**Tech Stack:** XeLaTeX, expl3, tcolorbox, listings, ctex/xeCJK, 方正字体 + Source Code Pro

**输出目录:** `d:\ai\latex\templates\`

---

## 架构设计

```
templates/
├── harryopo-base.sty               # [共享层] 字体 + 颜色 + 代码高亮 + 数学 + 超链接
├── harryopo-report.cls              # [报告] ctexart, 11pt, standard layout, cover page
├── harryopo-paper.cls               # [论文] ctexart, 11pt, twocolumn option, abstract
├── harryopo-book.cls                # [书籍] ctexbook, 11pt, chapters, teaching boxes
├── harryopo-notes.cls               # [笔记] extarticle, 9pt, wide right margin, 6-color margin notes
├── build.ps1                     # [编译] 三遍 xelatex + 清理临时文件
└── examples/
    ├── example-report.tex        # 报告示例：含封面、摘要、正文、参考文献
    ├── example-paper.tex         # 论文示例（单栏）
    ├── example-paper-twocolumn.tex  # 论文示例（双栏）
    ├── example-book.tex          # 书籍示例：含 frontmatter/mainmatter/backmatter
    └── example-notes.tex         # 笔记示例：含代码块、旁注、分屏对照
```

### 各模板对比

| 特性 | report | paper | book | notes |
|------|--------|-------|------|-------|
| **基类** | ctexart | ctexart | ctexbook | extarticle |
| **字号** | 11pt | 11pt | 11pt | 9pt |
| **页面** | A4 标准 | A4 紧凑/双栏 | A5/A4 | A4 左右不对称 |
| **旁注** | ❌ | ❌ | 右侧 margin | 右侧 6.5cm 大边距 |
| **代码** | 基础 | 基础 | ✅ listings | ✅ listings+tcolorbox |
| **教学盒子** | ❌ | ❌ | 6种 | 5种+6色旁注 |
| **封面** | ✅ titlepage | ✅ maketitle | ❌ | ✅ titlepage |
| **目录** | ✅ | ❌ | ✅ | ✅ |
| **参考文献** | ✅ | ✅ bibtex | ✅ biblatex | ❌ |
| **分屏对照** | ❌ | ❌ | ❌ | ✅ |

### 颜色主题（统一于 base.sty）

4 级颜色层次（借鉴橙色书籍）：
- **主题色 MainColor**：章节标题、链接、盒子边框
- **辅助色 SubColor**：次要标题、盒子标题栏
- **点缀色 SmallColor**：着重号、小标记
- **极淡色 TinyColor**：盒子背景

内置 3 套主题：
- `blue`（默认，学术蓝 #4A90D9）
- `green`（清新绿 #059669）
- `dark`（深色紫 #6F42C1）

### 共享基础包 harryopo-base.sty 模块

1. **依赖包加载**（去重、按序）
2. **颜色定义**（GitHub 代码色 + 3 套主题色 + 语义色）
3. **字体配置**（Source Code Pro + 方正书宋/黑体/楷体/仿宋/大标宋）
4. **代码高亮**（listings pystyle，GitHub 风格）
5. **数学环境**（amsmath + amssymb + amsthm）
6. **tcolorbox 基础**（breakable,skins,most）
7. **超链接**（hyperref，黑色链接）
8. **图表支持**（graphicx, booktabs, caption）
9. **代码行内**（\inlinecode 命令）

---

## 任务分解

### Task 1: 创建 harryopo-base.sty 共享基础包

**Files:**
- Create: `d:\ai\latex\templates\harryopo-base.sty`

**内容概要:**
- kvoptions 接收 theme=blue|green|dark 参数
- 9 大模块（如上）
- 最终约 200 行

### Task 2: 创建 harryopo-report.cls 实验报告模板

**Files:**
- Create: `d:\ai\latex\templates\harryopo-report.cls`

**内容概要:**
- 基于 ctexart, 11pt, a4paper
- 加载 harryopo-base.sty
- 自定义 \maketitle（含课程名/学号/姓名/日期）
- abstract 环境
- 标题格式：section 蓝色主题色，subsection 次色
- 参考文献：thebibliography 环境
- geometry: left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm

### Task 3: 创建 harryopo-paper.cls 学术论文模板

**Files:**
- Create: `d:\ai\latex\templates\harryopo-paper.cls`

**内容概要:**
- 基于 ctexart, 11pt, a4paper
- 加载 harryopo-base.sty
- twocolumn 选项（一键切换双栏）
- 自定义 \maketitle（标题/作者/摘要/关键词）
- 紧凑布局：left=2cm, right=2cm, top=2cm, bottom=2cm
- \abstract, \keywords 命令
- 双栏时 \twocolumn[\maketitle] 标题跨栏
- 参考文献：bibtex 兼容

### Task 4: 创建 harryopo-book.cls 书籍/教材模板

**Files:**
- Create: `d:\ai\latex\templates\harryopo-book.cls`

**内容概要:**
- 基于 ctexbook, 11pt, a5paper (or a4paper)
- 加载 harryopo-base.sty
- frontmatter/mainmatter/backmatter 支持
- 6 种教学盒子：keyconcept, examplebox, tipbox, warningbox, practicebox, answerbox
- 章节标题美化（带色块）
- 右侧 margin 旁注（marginparwidth=4cm）
- 页眉页脚：左页章名、右页节名
- 目录美化

### Task 5: 创建 harryopo-notes.cls 学习笔记模板

**Files:**
- Create: `d:\ai\latex\templates\harryopo-notes.cls`

**内容概要:**
- 基于 extarticle, 9pt, a4paper, twoside
- 加载 harryopo-base.sty
- 不对称号布局：left=2.3cm, right=6.5cm
- marginparwidth=5cm, marginparsep=0.6cm
- 6 种颜色编码旁注（从 python-study 迁移）：
  - \tipnote, \codenote, \keynote, \warnnote, \tricknote, \margintip
- 代码环境：pythoncode (tcblisting)
- 教学环境：pyexample, pyanswer, pypractice, formal, codeoutput
- 分屏对照：\codesplit, \codelinecompare, \codecompare
- 定理环境：definition, lemma

### Task 6: 创建示例文件 + build.ps1

**Files:**
- Create: `d:\ai\latex\templates\examples\example-report.tex`
- Create: `d:\ai\latex\templates\examples\example-paper.tex`
- Create: `d:\ai\latex\templates\examples\example-paper-twocolumn.tex`
- Create: `d:\ai\latex\templates\examples\example-book.tex`
- Create: `d:\ai\latex\templates\examples\example-notes.tex`
- Create: `d:\ai\latex\templates\build.ps1`

### Task 7: 编译验证

对每个示例文件运行 `build.ps1` 或 `xelatex`，确认 PDF 正常生成，无严重警告。

---

## Self-Review Checklist

### 1. Spec Coverage
- [x] 报告模板（report）→ Task 2
- [x] 论文模板（paper）→ Task 3
- [x] 论文双栏模式 → Task 3（twocolumn 选项）
- [x] 书籍模板（book）→ Task 4
- [x] 笔记模板（notes）→ Task 5
- [x] 美观、层级清晰、结构完整 → 统一样式规范
- [x] 通用模板 → 共享 base.sty
- [x] 编译脚本 → Task 6 build.ps1
- [x] 示例文件 → Task 6 examples/
- [x] 编译验证 → Task 7

### 2. Placeholder Scan
- 所有任务都有具体文件路径
- 所有命令都有实际内容
- 无 TBD/TODO

### 3. Type Consistency
- 所有 .cls 通过 kvoptions 接收相同 theme 参数
- 所有 .cls 加载同一个 harryopo-base.sty
- 颜色命名与 base.sty 定义一致
- 命令命名风格统一（snake_case 用于 LaTeX 命令）

---

**Plan complete. 开始执行所有任务。**
