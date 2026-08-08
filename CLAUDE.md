# CLAUDE.md — d:\ai\latex 项目规则

> 本项目为harryopo LaTeX 通用模板体系。以下规则适用于所有在本项目中工作的 AI Agent。

---

## ⚠️ 当前状态 (2026-06-21)

**核心模板文件尚未创建！** templates/ 目录当前仅有：
- `examples/`（example-paper.tex/pdf, example-paper-twocolumn.tex/pdf）
- `math-notes/`（完整独立的数理笔记系统）

**缺失（需紧急创建）：**
- `templates/harryopo-base.sty` — 共享基础包
- `templates/harryopo-paper.cls` — 论文文档类（examples 依赖）
- `templates/harryopo-report.cls` — 报告文档类
- `templates/harryopo-book.cls` — 书籍文档类
- `templates/harryopo-notes.cls` — 笔记文档类
- `templates/build.ps1` — 编译脚本

**详细实施计划见** `docs/plans/2026-06-20-latex-templates.md`（Task 1-7）

---

## 硬规则

### 编译
- **必须使用 XeLaTeX**，不得使用 pdfLaTeX 或 LuaLaTeX
- 编译 3 遍以确保交叉引用和目录稳定
- build.ps1 使用 TEXINPUTS 环境变量让 xelatex 在 templates/ 目录搜索 .cls/.sty

### 模板架构
- **共享体系**（report/paper/book/notes）均加载 `harryopo-base.sty`，使用 `\ifdefined\harryopo@theme` 机制传递主题
- **math-notes 是独立体系**（`templates/math-notes/`），不加载 base.sty，不修改其架构
- 新增模板必须：基于 ctexart/ctexbook/extarticle，加载 harryopo-base.sty，遵守主题中继机制

### 命名
- 模板文件前缀 `harryopo-`
- 示例文件前缀 `example-`
- 文档类 `.cls`、样式包 `.sty`

---

## 踩坑警示

1. **不要在 math-notes 中引入 base.sty**——mdframed 边框体系与 tcolorbox 冲突，字体配置也不兼容
2. **不要用 multicol 做双栏**——ctexart 原生 twocolumn 选项配合 cuted+flushend 是最优解
3. **不要在 .sty 中用 kvoptions**——主题通过 `\def\harryopo@theme{}` 在加载 base.sty 前设定
4. **algorithm2e 需要 \newcounter{chapter}**——ctexart 无 chapter 计数器
5. **marginfix 必须加载在 geometry 之后**
6. **`\hfuzz` 对显式 `\hbox to` 命令无效**——仅对段落自动断行产生的溢出敏感，对 TeX 原语级别的 `\hbox to <dimen>` 溢出无能为力
7. **`silence` 包无法过滤 Tex 原语级别的 Overfull \hbox**——`silence` 仅处理 LaTeX 层次的警告，需用 `\rlap` 等调整内容宽度来消除
8. **超出 `\textwidth` 的图片/内容用 `\rlap{}` 包裹**——让内容向右延伸到页边距而不产生 overfull box（常见于 kaobook 的章节标题图片）
9. **不要在 base.sty 中重复加载 ctex**——cls 已通过 ctexart/ctexrep 加载，重复加载导致 `Missing \begin{document}` 致命错误
10. **CJK 字体族名不要与 ctex 默认集冲突**——`zhkai`/`zhfs`/`zhhei` 是 fandol 默认定义的，用 `\newCJKfontfamily` 创建独立族（如 `hrypkai`）
11. **`\and` 在 `\twocolumn[]` 中会触发 `\crcr` 错误**——`\and` 内部使用 `\\` 表格对齐，与 `\twocolumn[]` 的盒子处理冲突，改用中文顿号 `、` 分隔作者
12. **`strip` 环境 (cuted) 与 booktabs 冲突**——`\toprule`/`\midrule`/`\bottomrule` 在 `strip` 中产生 `\crcr` 错误，改用 `\twocolumn[]` 替代
13. **unicode-math 的 SizeFeatures 需要 XITSMath.otf（无 -Regular 后缀）**——必须从 XITSMath-Regular.otf 复制一份
14. **fontspec BoldFont/ItalicFont 不可用 `*` 通配符**——黑体/楷体是独立文件（FZHTJW/FZKTJW），非书宋后缀，必须显式指定
15. **longtable 的 \endfirsthead/\endhead 前面不能放 \multicolumn 内容行**——只能放 \hline，否则报错 `\ltcaption@ORI@LT@array was complete`（caption 包修补 longtable 后的兼容性问题）。表头内容应作为数据的第一行输出，而非放在 \endfirsthead 前面
16. **MinerU DOCX 表格输出是 HTML 格式**——保留 colspan/rowspan，可直接映射到 \multicolumn/\multirow；比 Markdown 表格强大得多
17. **MinerU 会给 Word 标题标记加粗**——标题样式含 bold 属性，输出为 `# **标题**`，清洗时需去掉 `**`
18. **`\fzht{文字}` 的花括号不会限制字体切换范围**——`\newcommand{\fzht}{\hrypht}` 定义的是声明式命令（类似 `\bfseries`），`\fzht{文字}` 等价于先全局切换字体再开分组，花括号结束后字体切换仍然有效。解决方案：用 `\@ifnextchar\bgroup` 实现双模式——`\fzht{文字}` 自动包裹分组，`{\fzht 文字}` 保持声明式行为。所有字体快捷命令（`\fzkt`/`\fzfs`/`\fzdbs`/`\fzxb`/`\fzht`）均需此模式

---
## 项目事实

- **位置**: `d:\ai\latex\`
- **子项目**: `参考资料/中文book/` — kaobook 中文书籍模板（方正字体、XITS 数学，独立体系，39页编译通过）
- **模板目录**: `d:\ai\latex\templates\`
- **记忆系统**: `d:\ai\latex\memory\MEMORY.md`
- **学习日志**: `d:\ai\latex\.learnings\`
- **论文示例参考**: `templates/examples/example-paper.tex`（当前无法重新编译，缺少 .cls）
- **数理笔记**: `templates/math-notes/`（独立体系，完整可用）

## 协作流程

1. 修改 .cls/.sty 后，编译所有示例验证
2. 新增文件后更新 `memory/MEMORY.md`
3. 遇到新踩坑后追加到 `.learnings/LEARNINGS.md` 和本文
4. 删除文件前确认无引用
