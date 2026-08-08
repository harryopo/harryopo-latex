# 学习记录 — d:\ai\latex

## 2026-06-21: 项目大清理

### correction: math-notes 应独立于通用模板体系
- **背景**: 原计划将 math-notes 作为 harryopo-notes.cls 的子集，后发现 math-notes 的定位完全不同
- **问题**: math-notes 使用 extarticle+9pt+twoside，方正+XITS字体，色块+侧边竖线定义块，mdframed边框体系 — 与 harryopo-notes.cls 的共享 base.sty 体系架构不兼容
- **纠正**: math-notes 保持为独立文档类 `harryopo-mathnotes.cls`，不走 base.sty 共享层，是独立的最佳实践
- **结论**: 两大最佳实践分支：(1) math-notes 独立体系 (2) 通用模板 base.cls 共享体系

### correction: 论文模板采用 ctexart 而非 ctexart+twocolumn 选项
- **背景**: 原设计担心 ctexart 原生 twocolumn 支持不好
- **结论**: harryopo-paper.cls 直接在 ctexart 上通过 `\DeclareOption{twocolumn}` 切换，效果良好
- **关键**: 使用 cuted strip 跨栏 + flushend 栏平衡

### learning: build.ps1 通过 TEXINPUTS 环境变量解决 .cls/.sty 搜索路径
- **方法**: `$env:TEXINPUTS = "$ScriptDir;.;"` 让 xelatex 在模板目录中查找 class/style 文件
- **优势**: 无需将 .cls/.sty 安装到 texmf 树，开箱即用

### correction: 清理前项目存在大量冗余
- **已删除**: 参考/（导数研究、极点极线、python-study、数据库学习笔记）
- **已删除**: 模板/（中文book、橙色书籍、双栏.tex）
- **已删除**: 根目录测试文件、harryopo-kao.sty、harryopo-kaobook.cls（旧kaobook体系）
- **保留的价值**: 调研报告（templates-research.md）和计划文档（2026-06-20-latex-templates.md）归档到 docs/

### best-practice: 两大最佳实践
1. **math-notes**: 色块+侧边竖线定义块、方正字体、XITS数学、宽边注(6cm)、3色标注(attention/tips/warns)、自嵌西文字体
2. **论文单双栏**: twocolumn选项、跨栏标题摘要(cuted strip)、算法伪代码(algorithm2e)、栏平衡(flushend)、3色主题(blue/green/dark)

---

## 2026-06-21: 中文book 子项目修复与优化

### correction: 侧边注字体从繁体仿宋修正为简体仿宋
- **背景**: kaoWinCJKsc.sty 中边注使用 `FZFSFW`（繁体仿宋），对简体中文文档不合适
- **纠正**: 改为 `方正仿宋_GBK`（简体仿宋），通过修补 `\@margin@par` 命令确保边注使用 `\fzfs`
- **影响**: 所有 marginfigure/marginnote/sidenote 字体自动切换为简体仿宋

### learning: 章节标题图片超边距的根因与修复
- **问题**: `\setchapterimage` 中 `\includegraphics[width=\paperwidth]` 的图片宽度超出 `\textwidth` 222pt
- **根因**: 图片以 `\paperwidth` 为宽度，但实际布局区域是 `\textwidth`，差值即溢出量
- **修复**: 用 `\rlap{}` 包裹 `\includegraphics`，让图片向右延伸到页边距内（不产生 overfull box）
- **影响**: 解决了全部 8 处章节标题图片的 222pt 溢出

### learning: `\hfuzz` 对显式 `\hbox to` 命令无效
- **背景**: 尝试用 `\hfuzz` 放宽 overfull 容忍度抑制警告
- **结论**: `\hfuzz` 仅对 TeX 段落自动断行产生的溢出有效，对显式 `\hbox to <dimen>` 命令产生的溢出无效
- **替代**: 必须通过调整内容宽度（如 `\rlap`）或修改 `\hbox to` 的目标尺寸来修复

### learning: `silence` 包无法过滤 TeX 原语级别的 Overfull \hbox 警告
- **背景**: 尝试用 `silence` 包过滤剩余的小额溢出（1-2pt）
- **结论**: `silence` 包只能过滤 LaTeX 层次的警告，对 TeX 原语级别（`\hbox to`）的 `Overfull \hbox` 无能为力
- **替代**: 必须逐一调整内容宽度解决

### learning: kaobook 边注浮动警告是正常行为
- **背景**: 编译后出现 `marginpar moved` 警告（第8/9/12页）
- **结论**: 这是 kaobook 边注浮动机制的正常行为——当边注无法放入当前页面时 LaTeX 会移动到下一页，产生信息性警告
- **处理**: 可忽略，不影响输出

---

## 2026-07-27: harryopo-tikz-diagram 时序图 v5.1 三阶段紧凑布局

### best-practice: 三阶段绘制架构彻底解决时序图文字遮盖
- **核心原理**: 同一消息序列在3个Pass中重复调用，通过`\ifgeom`/`\iflbl`开关控制每次绘制内容
  - Pass 1 (Dry Run): 仅推进Y游标、标记片段边界coordinate，不绘制任何可见元素
  - Pass 2 (Geometry): 绘制所有几何元素（生命线/激活条/箭头/片段框），NO TEXT
  - Pass 3 (Labels): 仅绘制文字标签（fill=white光晕在最顶层）
  - Final Layer: 参与者头部、片段名、条件标签、图例、标题
- **关键**: 标签最后绘制 → `fill=white, inner sep=2pt`白色光晕100%遮盖下方几何元素
- **Z-order分层**: Layer 0(片段框fill+生命线) → Layer 1(phase线+激活条+箭头+自关联) → Layer 2(片段边框+五边形) → Layer 3(文字标签) → Final(参与者头部+片段名+条件+图例+标题)

### best-practice: v5.1紧凑版间距常量
- **GapMsg=0.88cm** (同步消息), **GapRet=1.00cm** (返回消息), **GapSelf=1.40cm** (自关联)
- **GapPhase=0.28cm** (阶段分隔), **FragPad=0.15cm** (片段内边距), **SelfLoopH=0.50cm** (U型高度)
- 对比v5宽松版(GapMsg=1.75等)，内容密度提升约40%，高度减少约35%
- 激活条高度=0.58cm与GapMsg联动，避免空隙过大

### best-practice: 五边形折角标签尺寸校准
- alt片段五边形: `(0.60,0)--(0,-0.32)--(-0.18,-0.18)--(-0.42,0)`
- loop片段五边形: `(0.95,0)--(0,-0.32)--(-0.18,-0.18)--(-0.77,0)`
- 折角45度，垂直段0.32cm，文字放置于`(+0.16,-0.24)`(alt)/`(+0.30,-0.24)`(loop)
- 五边形必须用PaperBg填充+PaperBorder虚线描边，尺寸需精确匹配文字宽度

### learning: 标题内嵌tikzpicture消除LaTeX排版额外间距
- **问题**: 标题放在`\end{tikzpicture}`外用center环境会产生不可控的垂直间距
- **解决**: 标题放在tikzpicture内部底部，用`(title-cx |- title-pos)`坐标语法精确定位
- bbox通过bb-bottom坐标精确控制：`\path (title-en-pos) ++(0,-0.4cm) coordinate (bb-bottom)`

### learning: 图例术语表禁止嵌套tikzpicture
- **问题**: 在legend/glossary node中嵌套`\begin{tikzpicture}`会导致bounding box计算错误
- **解决**: 用`\makebox[0.9cm][l]{\textcolor{...}{\rule...}$\rightarrow$}`纯文本+简单规则符号绘制
- 紧凑版: inner sep=4pt, font=\scriptsize, \\[0.5pt]/\\[1pt]控制行间距

### best-practice: 分层架构图v2布局经验（从paper-structure迁移）
- **核心原则**: 无阴影(clean flat) + 居中对齐(align=center) + 宽松内边距(inner sep=8pt)
- **层标题**: 用`$(box.north west)+(0,4pt)$`偏移到虚线框上方，禁止`fill=white`打断边框
- **图例**: 嵌入tikzpicture内部右下角(anchor=north east at south east偏移)，禁止单独tikzpicture
- **字体**: 全图无衬线Arial+Microsoft YaHei，禁止Times New Roman
- **间距常量**: ModW=4.0cm, ModH=1.5cm, ModGap=0.55cm, LayerGap=1.6cm, LayerPad=12pt
- **模块内容层次**: mod-title(加粗深灰) + mod-desc(小号灰色) + mod-tech(等宽橙色)替代fontawesome+multirow
- **禁止hfuzz=60pt**: 这是掩盖溢出的hack，精确计算间距才是正解
- **层间定位**: 下一层第一个节点必须用`below=\LayerGap of <上一层>.south west, anchor=north west`保持左对齐
- **典型错误**: 使用fontawesome5图标(依赖额外宏包)、drop shadow(视觉噪音)、multirow+tabular(脆弱)、Times New Roman(违反Nature风格)

---

## 2026-07-30: harryopo-tikz-diagram 工作流程优化 + examples 修复

### workflow: MD示意图预审核工作流（强制步骤）
- **核心规则**: 所有图形在生成TikZ前必须先生成Markdown示意图给用户确认
- **MD格式规范**:
  - 分层架构图：用 ┌─┬─┐ 表格字符画层和模块
  - 流程图：用 ┌─┐/↓/──否→/│↑回到上方 表示走向
  - 组织架构图：用 ├──/└──/│ 缩进树
  - 时序图：用竖向生命线 ┃ 加箭头表示消息
- **流程**: 生成MD → 询问确认 → 等待用户说"可以/确认" → 才生成TikZ
- **蒸馏步骤**: 用户输入杂乱时，先提取实体→梳理层级→识别连接→过滤冗余，再画MD

### best-practice: 流程图错误分支返回线规范（v3）
- **错误**: v2版本错误分支返回线从分支节点向下绕回目标节点，视觉上与主流程方向冲突
- **正确做法（标准UML）**: 返回线从分支节点**顶部向上**走，再右拐接入目标节点左侧偏上
- **实现**: `\draw[arrow-loop] (branch.north) -- ++(0,\LoopUp) -| ($(target.west)+(0,0.15cm)$);`
- **间距**: FlowHGap需≥3.0cm（v2是2.4cm），FlowLoopUp=0.7cm，确保绕回弧线不与其他元素重叠
- **样式**: 分支/返回线统一用灰色虚线(dash pattern=on 5pt off 3pt)，主流程用蓝色实线1.2pt

### learning: TikZ style命名避免与内置键冲突
- **冲突键名**: `cap`（line cap键）、`as`（arrow tip键）、`in`/`out`（曲线方向键）
- **解决**: 自定义样式名用≥3字符或加后缀（capn/ast/snds），避免两字母通用名

### learning: xcolor RGB语法陷阱
- **错误**: `{RGB}{107,174,85}` 在TikZ node style中会报"Undefined color"
- **正确**: 先 `\definecolor{Name}{HTML}{6BAE55}` 定义命名色，再在style中用 `draw=Name`

### correction: 放弃复杂fontawesome5+多彩曲线的agent流程图
- **教训**: 过度设计（多色箭头+曲线数据流+图标）反而丑，不如简洁的方框+直线
- **保留的3个高质量examples**: example-flowchart(v3)、example-org-tree(v2)、example-architecture-full
- **org-tree优化**: 去掉Times New Roman和drop shadow，统一Arial+无衬线+浅灰填充，间距加大(node distance=1.0cm/0.8cm)
