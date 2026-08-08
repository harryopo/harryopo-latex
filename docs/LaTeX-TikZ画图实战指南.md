# LaTeX TikZ 画图实战指南

> 版本：v1.0 | 日期：2026-07-07 | 来源：智配商业计划书架构图实践

---

## 一、这份指南能解决什么问题

在 LaTeX 文档中插入专业的架构图、流程图、框架图，不需要外部工具（draw.io、Visio），直接用 TikZ 原生绘制，保证：

- **排版一致**：字体、颜色、风格与文档主题完全统一
- **矢量高清**：PDF 中任意放大不失真
- **无需导出**：代码即文档，修改方便
- **中文友好**：配合 XeLaTeX + 中文字体，完美支持中文

---

## 二、环境准备

### 2.1 编译器

必须使用 **XeLaTeX** 编译器（支持中文的关键）。harryopo 模板的 `build.ps1` 默认使用 xelatex。

### 2.2 必须加载的 TikZ 库

在 `\documentclass` 之后、`\begin{document}` 之前加载：

```latex
\usetikzlibrary{
  positioning,    % 相对定位：right=of, below=of
  fit,            % 自动包裹节点：fit=(a)(b)(c)
  backgrounds,    % 背景层：on background layer
  arrows.meta     % 箭头样式：Stealth, Latex 等
}
```

> **踩坑提醒**：少加载 `arrows.meta` 会导致 `>=Stealth` 箭头头不显示，甚至整张图渲染异常（只有背景没有模块）。

### 2.3 颜色体系（harryopo 模板内置）

harryopo 模板已经定义好了一套蓝色系颜色，直接用就行：

| 颜色变量 | 色值 | 用途 |
|---------|------|------|
| `MainColor` | 深蓝 `#1A365D` | 主标题、边框、强调 |
| `SubColor` | 中蓝 `#2B6CB0` | 副标题、层边框 |
| `SmallColor` | 浅蓝 `#4299E1` | 次要元素 |
| `TinyColor` | 极浅蓝 `#EBF8FF` | 背景填充 |
| `DarkColor` | 深灰 `#1A202C` | 正文 |
| `AccentColor` | 红色 `#C53030` | 警告、强调 |

蓝色系混合色（TikZ 内置语法）：
- `blue!10` = 10% 蓝 + 90% 白（极浅蓝，做背景）
- `blue!20` = 20% 蓝 + 80% 白（浅蓝）
- `blue!50` = 50% 蓝 + 50% 白（中蓝）
- `blue!70!black` = 70% 蓝 + 30% 黑（深蓝）

---

## 三、核心概念

### 3.1 节点（Node）

TikZ 图的基本单位是**节点**（node），每个方框、文字都是一个节点。

```latex
\node[样式] (节点名) at (坐标) {内容};
```

示例：

```latex
\node[draw, rounded corners, fill=blue!10, text width=3cm, align=center] (box1) at (0,0)
  {这是一个方框\\第二行文字};
```

### 3.2 锚点（Anchor）

每个节点都有一系列锚点，用于定位和连线：

```
    .north west   .north   .north east
          +---------+---------+
          |                   |
    .west |       .center    | .east
          |                   |
          +---------+---------+
    .south west   .south   .south east
```

用法：`节点名.锚点名`，例如 `box1.south`、`box2.north`。

### 3.3 样式（Style）

把重复的属性定义成样式，代码更简洁：

```latex
\tikzset{
  mybox/.style={
    draw=MainColor,
    thick,
    rounded corners=3pt,
    fill=white,
    text width=2.5cm,
    minimum height=1.2cm,
    align=center,
    font=\small
  }
}
```

然后直接用：`\node[mybox] (a) {内容};`

### 3.4 相对定位（positioning 库）

不用算坐标，直接说"在谁的右边/下边"：

```latex
\node[mybox] (a) at (0,0) {模块A};
\node[mybox, right=10pt of a] (b) {模块B};   % 右边
\node[mybox, below=10pt of a] (c) {模块C};   % 下边
```

间距单位：`pt`（点，最小单位）、`cm`（厘米）、`em`（字宽）。

### 3.5 连线（Draw）

```latex
\draw[->, >=Stealth, thick] (a.south) -- (b.north);
```

常用箭头样式（需要 arrows.meta 库）：
- `Stealth`：三角箭头（推荐，现代风格）
- `Latex`：大箭头
- `To`：普通箭头

线型：
- `thick` / `very thick` / `ultra thick`：粗线
- `thin` / `very thin`：细线
- `dashed`：虚线
- `dotted`：点线

### 3.6 背景层（backgrounds 库）

层背景框要在**背景层**绘制，否则会盖住前面的节点：

```latex
\begin{scope}[on background layer]
  \node[draw, dashed, fit=(a)(b)(c), fill=blue!5] (bg) {};
\end{scope}
```

### 3.7 自动包裹（fit 库）

用 `fit=(a)(b)(c)` 让一个节点自动包裹多个子节点，做大框、背景框超方便：

```latex
\node[draw, dashed, fit=(a)(b)(c), inner sep=10pt] (bg) {};
```

- `inner sep`：内边距（框和内容的距离）

---

## 四、常见布局模式

### 模式一：横向三层架构图（最常用）

适用场景：系统架构、技术栈分层、产品模块图。

特点：
- 从上到下 2-4 层
- 每层内部模块横向排列
- 每层有一个虚线大框包裹
- 层之间有箭头连接

**完整模板**：

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  module/.style={
    draw=MainColor, very thick, rounded corners=3pt,
    fill=white,
    text width=2.4cm, minimum height=1.4cm,
    align=center, font=\small
  },
  widemodule/.style={
    draw=MainColor, very thick, rounded corners=3pt,
    fill=white,
    text width=7.0cm, minimum height=1.4cm,
    align=center, font=\small
  },
  arr/.style={
    ->, >=Stealth, thick, MainColor!70!black
  },
  layerbox/.style={
    draw=SubColor, thick, rounded corners=6pt, dashed,
    fill=blue!5, inner sep=14pt
  },
  layertitle/.style={
    font=\normalsize\bfseries, SubColor,
    anchor=north west, inner sep=2pt, yshift=2pt
  }
]

% ===== 第一层 =====
\node[module] (L1a) at (0,0)
  {\textbf{模块A标题}\\[4pt]
   描述第一行\\
   描述第二行};
\node[module, right=12pt of L1a] (L1b)
  {\textbf{模块B标题}\\[4pt]
   描述第一行\\
   描述第二行};
\node[widemodule, right=12pt of L1b] (L1c)
  {\textbf{宽模块标题}\\[4pt]
   子项1 \;|\; 子项2 \;|\; 子项3};

\begin{scope}[on background layer]
\node[layerbox, fit=(L1a)(L1b)(L1c)] (bg1) {};
\end{scope}
\node[layertitle] at (bg1.north west)
  {第一层：xxx 层（说明）};

% ===== 第二层 =====
\node[module, below=1.8cm of L1a] (L2a)
  {\textbf{模块D标题}\\[4pt]描述};
\node[module, right=12pt of L2a] (L2b)
  {\textbf{模块E标题}\\[4pt]描述};

\begin{scope}[on background layer]
\node[layerbox, fill=blue!10, fit=(L2a)(L2b)] (bg2) {};
\end{scope}
\node[layertitle] at (bg2.north west)
  {第二层：xxx 层（说明）};

% ===== 层间箭头 =====
\draw[arr] (L1a.south) -- (L2a.north);
\draw[arr] (L1b.south) -- (L2a.north);
\draw[arr] (L1c.south) -- (L2b.north);

\end{tikzpicture}
\caption{图标题}
\end{figure}
```

### 模式二：矩阵布局（matrix）

适用场景：规则的网格布局，每个格子大小一致。

```latex
\matrix (m) [matrix of nodes, nodes={mybox}, column sep=10pt, row sep=10pt] {
  左上 & 右上 \\
  左下 & 右下 \\
};
```

访问节点：`m-1-1`（第 1 行第 1 列）、`m-2-2`（第 2 行第 2 列）。

> **注意**：matrix 模式下所有节点样式必须统一（或者用 `|[style]|` 逐格覆盖），灵活性不如手动定位。

### 模式三：自上而下流程图

适用场景：步骤流程、处理流程。

```latex
\begin{tikzpicture}[
  step/.style={
    draw=MainColor, thick, rounded corners=4pt,
    fill=blue!10, text width=4cm, minimum height=1cm,
    align=center, font=\small
  },
  arr/.style={->, >=Stealth, thick, MainColor!70!black}
]

\node[step] (s1) {第一步：xxx};
\node[step, below=12pt of s1] (s2) {第二步：xxx};
\node[step, below=12pt of s2] (s3) {第三步：xxx};

\draw[arr] (s1.south) -- (s2.north);
\draw[arr] (s2.south) -- (s3.north);

\end{tikzpicture}
```

---

## 五、踩坑记录与解决方案

### 坑 1：模块框看不见，只有背景层

**症状**：整张图只有虚线大框和箭头，里面的小模块完全看不到。

**原因**：几乎一定是 **`arrows.meta` 库没加载**。`>=Stealth` 用不了会导致 TikZ 解析异常，连带其他节点渲染也出问题。

**修复**：确保 `\usetikzlibrary{..., arrows.meta}` 加了。

### 坑 2：中文不显示或显示乱码

**症状**：方框里的中文变成空白或方块。

**原因**：
1. 用了 pdflatex 而不是 xelatex
2. 中文字体没配置

**修复**：
- harryopo 模板自带字体和 xelatex 配置，用 `build.ps1` 编译就行
- 自定义文档要确保 `\usepackage{fontspec}` + `\setCJKmainfont{...}`

### 坑 3：多行文本不换行

**症状**：`\\` 写了但文字还是一行堆着。

**原因**：没有设置 `align=center`（或 `align=left` / `align=right`）。

**修复**：节点样式加 `align=center`。

```latex
% 正确
\node[text width=3cm, align=center] {第一行\\第二行};

% 错误（不换行）
\node[text width=3cm] {第一行\\第二行};
```

### 坑 4：背景框盖住了内容

**症状**：背景填充色把前面的模块盖住了。

**原因**：背景框在前景层绘制的，后画的盖住先画的。

**修复**：用 `on background layer` 环境：

```latex
\begin{scope}[on background layer]
  \node[...] (bg) {};
\end{scope}
```

### 坑 5：fit 的框大小不对

**症状**：`fit=(a)(b)` 的框要么太大要么太小。

**原因**：默认 `inner sep` 是固定值（通常 0.333em），内容少的话框就小。

**修复**：显式设置 `inner sep`：

```latex
\node[fit=(a)(b), inner sep=12pt] (bg) {};
```

### 坑 6：图太宽超出页面

**症状**：右边被切掉了。

**原因**：A4 正文宽度约 15-16cm，模块摆太多了。

**修复方案（按优先级）**：
1. 减少模块数，合并次要模块
2. 减小 `text width`，让文字换更多行
3. 减小模块间距（`right=8pt of` 而不是 12pt）
4. 用 `\small` 或 `\footnotesize` 缩小字体
5. 改成横向布局（`sidewaysfigure`，不推荐）

### 坑 7：箭头起点/终点位置不对

**症状**：箭头从框中间穿过去了，或者没接在框上。

**原因**：没指定锚点，用了默认的 `.center`。

**修复**：明确指定锚点：

```latex
% 正确
\draw[arr] (a.south) -- (b.north);

% 错误（从中心出发）
\draw[arr] (a) -- (b);
```

### 坑 8：figure 环境乱跑

**症状**：图不在你写的位置，跑页面别的地方去了。

**原因**：LaTeX 浮动体（float）的自动排版机制。

**修复**：
- 加 `[htbp]` 选项（h=here, t=top, b=bottom, p=page）
- 非要精确位置用 `[H]`（需要 `float` 包，harryopo 已加载）

---

## 六、完整实战示例：智配三层架构图

这是本次商业计划书用的最终版本，横向三层、模块清晰、配色和谐。

### 6.1 最终效果描述

- 第一层（最上层）：智配桌面安装器 —— 4 个模块，最右边一个宽模块
- 第二层：后端服务 —— 3 个模块
- 第三层（最下层）：开源生态 —— 3 个模块
- 每层有虚线框 + 左上角标题
- 层之间有箭头连接

### 6.2 完整代码

```latex
\usetikzlibrary{positioning, fit, backgrounds, arrows.meta}

% ...

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  module/.style={
    draw=MainColor, very thick, rounded corners=3pt,
    fill=white,
    text width=2.4cm, minimum height=1.4cm,
    align=center, font=\small
  },
  widemodule/.style={
    draw=MainColor, very thick, rounded corners=3pt,
    fill=white,
    text width=7.0cm, minimum height=1.4cm,
    align=center, font=\small
  },
  arr/.style={
    ->, >=Stealth, thick, MainColor!70!black
  },
  layerbox/.style={
    draw=SubColor, thick, rounded corners=6pt, dashed,
    fill=blue!5, inner sep=14pt
  },
  layertitle/.style={
    font=\normalsize\bfseries, SubColor,
    anchor=north west, inner sep=2pt, yshift=2pt
  }
]

% ===== 第一层：智配桌面安装器 =====
\node[module] (L1a) at (0,0)
  {\textbf{硬件检测模块}\\[4pt]
   GPU / 显存 / 内存\\
   CPU / 操作系统};
\node[module, right=12pt of L1a] (L1b)
  {\textbf{模型推荐引擎}\\[4pt]
   根据硬件推荐\\
   最佳模型方案};
\node[module, right=12pt of L1b] (L1c)
  {\textbf{一键部署器}\\[4pt]
   自动化安装\\
   Ollama + UI};
\node[widemodule, right=12pt of L1c] (L1d)
  {\textbf{管理后台 (Web Dashboard)}\\[4pt]
   模型管理 \;|\; 运维监控 \;|\; 知识库 \;|\; 日志};

\begin{scope}[on background layer]
\node[layerbox, fit=(L1a)(L1b)(L1c)(L1d)] (bg1) {};
\end{scope}
\node[layertitle] at (bg1.north west)
  {第一层：智配桌面安装器（Electron 桌面应用）};

% ===== 第二层：后端服务 =====
\node[module, below=1.8cm of L1a] (L2a)
  {\textbf{部署引擎}\\[4pt]
   Ollama 管理\\
   模型管理};
\node[module, right=12pt of L2a] (L2b)
  {\textbf{运维监控}\\[4pt]
   GPU/内存采样\\
   进程守护};
\node[module, right=12pt of L2b] (L2c)
  {\textbf{API 服务}\\[4pt]
   FastAPI\\
   REST 接口};

\begin{scope}[on background layer]
\node[layerbox, fill=blue!10, fit=(L2a)(L2b)(L2c)] (bg2) {};
\end{scope}
\node[layertitle] at (bg2.north west)
  {第二层：后端服务（Python FastAPI）};

% ===== 第三层：开源生态 =====
\node[module, below=1.8cm of L2a] (L3a)
  {\textbf{Ollama}\\[4pt]
   推理引擎};
\node[module, right=12pt of L3a] (L3b)
  {\textbf{Open WebUI}\\[4pt]
   聊天界面};
\node[module, right=12pt of L3b] (L3c)
  {\textbf{模型文件（Qwen 等）}\\[4pt]
   GGUF 格式};

\begin{scope}[on background layer]
\node[layerbox, fill=blue!3, fit=(L3a)(L3b)(L3c)] (bg3) {};
\end{scope}
\node[layertitle] at (bg3.north west)
  {第三层：开源生态（底层依赖）};

% ===== 层间箭头 =====
\draw[arr] (L1a.south) -- (L2a.north);
\draw[arr] (L1b.south) -- (L2a.north);
\draw[arr] (L1c.south) -- (L2b.north);
\draw[arr] (L1d.south) -- (L2c.north);

\draw[arr] (L2a.south) -- (L3a.north);
\draw[arr] (L2b.south) -- (L3b.north);
\draw[arr] (L2c.south) -- (L3c.north);

\end{tikzpicture}
\caption{智配产品三层架构图}
\end{figure}
```

### 6.3 设计思路

1. **白框 + 深色边框**：模块白底深蓝边，在任何背景上都清晰可见
2. **标题加粗 + 描述普通**：视觉层次分明，第一眼看到模块名
3. **层背景从浅到深**：上层浅（`blue!5`）、中层稍深（`blue!10`）、下层最浅（`blue!3`），形成节奏
4. **虚线大框 + 实线小框**：线型对比，区分层级和模块
5. **箭头颜色 70% 蓝**：不抢模块的风头，但清晰可见

---

## 七、最佳实践清单

### 画图前

- [ ] 明确图的类型（架构图 / 流程图 / 框架图）和信息流方向
- [ ] 先在纸上或 ASCII 里画个草稿，确认布局
- [ ] 确认 TikZ 库都加载了（positioning, fit, backgrounds, arrows.meta）

### 画图中

- [ ] **样式复用**：重复属性定义成 style，不要每个节点写一堆参数
- [ ] **相对定位**：用 `right=of`、`below=of`，别硬编码坐标（第一个节点除外）
- [ ] **锚点明确**：连线时写清楚 `.south`、`.north`，别用默认
- [ ] **背景层**：大框、底色都放 `on background layer` 里
- [ ] **中文换行**：多行文本必须加 `align=center`
- [ ] **间距统一**：同级别模块间距一致（如都是 `12pt`）

### 画图后

- [ ] 编译一下，确认没有 warning
- [ ] 检查是否超出页边距
- [ ] 所有文字是否清晰可读（不要太小）
- [ ] 颜色是否和谐（不超过 3 种主色）
- [ ] 箭头方向是否符合逻辑流

### 调试技巧

1. **先画框再加文字**：确认布局没问题了再填内容
2. **用 `\draw (0,0) grid (10,5);`**：临时画个网格，对齐用
3. **节点加 `draw=red`**：调试时把边框涂红，看节点到底在哪
4. **逐步加内容**：一次只加一层或一组，加错了马上知道是哪的问题

---

## 八、常用速查表

### 8.1 节点属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `draw` | 画边框 | `draw=MainColor` |
| `fill` | 填充色 | `fill=blue!10` |
| `text width` | 文本宽度（自动换行） | `text width=3cm` |
| `minimum height` | 最小高度 | `minimum height=1.2cm` |
| `minimum width` | 最小宽度 | `minimum width=2cm` |
| `align` | 对齐方式 | `align=center` / `left` / `right` |
| `font` | 字体大小 | `font=\small` / `\footnotesize` / `\bfseries` |
| `rounded corners` | 圆角 | `rounded corners=3pt` |
| `inner sep` | 内边距 | `inner sep=6pt` |
| `outer sep` | 外边距 | `outer sep=2pt` |

### 8.2 线条属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `thick` | 粗线 | — |
| `very thick` | 很粗 | — |
| `thin` | 细线 | — |
| `line width` | 线宽 | `line width=1pt` |
| `dashed` | 虚线 | — |
| `dotted` | 点线 | — |
| `->` | 箭头（后） | — |
| `<-` | 箭头（前） | — |
| `<->` | 双向箭头 | — |
| `>=Stealth` | 箭头样式 | 需 arrows.meta |

### 8.3 定位语法

| 语法 | 说明 |
|------|------|
| `right=10pt of a` | 在 a 右边 10pt |
| `left=10pt of a` | 在 a 左边 10pt |
| `below=10pt of a` | 在 a 下边 10pt |
| `above=10pt of a` | 在 a 上边 10pt |
| `below right=10pt and 20pt of a` | 右下 10pt 下 / 20pt 右 |

### 8.4 颜色混合

| 语法 | 说明 |
|------|------|
| `blue!20` | 20% 蓝 + 80% 白 |
| `blue!20!red` | 20% 蓝 + 80% 红 |
| `blue!70!black` | 70% 蓝 + 30% 黑 |
| `MainColor!70!white` | 70% 主色 + 30% 白 |

---

## 九、学习资源

- **TikZ 官方文档**：`texdoc tikz`（命令行直接打开，最权威）
- **TikZ 示例库**：https://texample.net/tikz/examples/ （大量现成例子）
- **"TikZ 入门" 教程**：B站/知乎搜 "TikZ 教程"，入门级

---

## 十、版本迭代记录

| 版本 | 日期 | 内容 |
|------|------|------|
| v1.0 | 2026-07-07 | 初版，基于智配商业计划书架构图实践，包含三层架构图模板和 8 个踩坑记录 |
