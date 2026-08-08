# 流程图模板 (Flowchart)

## 概述

流程图模板用于绘制标准的业务流程图、算法流程图等。包含开始/结束、过程、决策、输入输出等标准节点，支持自上而下和自左而右两种布局方向。

**样式前缀：** `flow-`

---

## 模板文件

- `template.tex` — 主模板文件，包含完整的 TikZ 样式和示例代码

---

## 快速开始

### 基本使用

```latex
\documentclass{ctexart}
\usepackage{tikz}
\usetikzlibrary{positioning, fit, backgrounds, arrows.meta}
\usetikzlibrary{shapes.geometric, shapes.misc}

\begin{document}

\begin{figure}[htbp]
  \centering
  \input{templates/flowchart/template.tex}
  \caption{用户登录流程图}
\end{figure}

\end{document}
```

---

## 可调参数

### 颜色参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `MainColor` | 主色，用于连接线 | 深蓝 `#1A365D` |
| `SubColor` | 次色，用于过程框边框 | 中蓝 `#2B6CB0` |
| `SmallColor` | 辅助色，用于决策框边框 | 浅蓝 `#4299E1` |
| `TinyColor` | 极浅色，用于背景填充 | 淡蓝 `#EBF8FF` |
| `DarkColor` | 文字颜色 | 深灰 `#1A202C` |
| `AccentColor` | 强调色，用于开始/结束框 | 红色 `#C53030` |

### 布局参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\flowDirection` | 方向：`vertical`（自上而下）或 `horizontal`（自左而右） | `vertical` |
| `\flowNodeGap` | 节点之间的主方向距离 | `18pt` |
| `\flowSideGap` | 决策分支的侧方向偏移距离 | `30pt` |

### 节点尺寸参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\flowMinWidth` | 节点最小宽度 | `120pt` |
| `\flowMinHeight` | 节点最小高度 | `36pt` |
| `\flowTextWidth` | 节点文本宽度（自动换行） | `100pt` |
| `\flowDecisionSize` | 决策菱形的尺寸 | `60pt` |

### 线条参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\flowArrowThickness` | 箭头线粗细 | `1.5pt` |
| `\flowArrowTip` | 箭头形状 | `Stealth` |
| `\flowLabelFont` | 箭头标签字体 | `\footnotesize` |
| `\flowLabelFill` | 箭头标签背景色 | `white` |

---

## 节点类型

| 样式名 | 形状 | 用途 |
|--------|------|------|
| `flow-startend` | 圆角矩形 | 开始 / 结束 |
| `flow-process` | 直角矩形（微圆角） | 处理过程 / 操作步骤 |
| `flow-decision` | 菱形 | 判断 / 决策 |
| `flow-io` | 梯形 | 输入 / 输出 |
| `flow-subprocess` | 虚线矩形 | 子过程分组（背景框） |

---

## 连线类型

| 样式名 | 说明 |
|--------|------|
| `flow-arrow` | 带箭头的连接线 |
| `flow-label` | 箭头标签样式 |

### 连线语法

**直线连接：**
```latex
\draw[flow-arrow] (nodeA) -- (nodeB);
```

**折线连接（先横后竖）：**
```latex
\draw[flow-arrow] (nodeA.east) -| (nodeB.north);
```

**折线连接（先竖后横）：**
```latex
\draw[flow-arrow] (nodeA.south) |- (nodeB.west);
```

**带标签的连线：**
```latex
\draw[flow-arrow] (nodeA) -- (nodeB)
  node[flow-label, pos=0.5, right=4pt] {标签文字};
```

---

## 常见修改示例

### 1. 切换为水平方向

将节点定位从 `below=of` 改为 `right=of`：

```latex
% 开始节点
\node[flow-startend] (start) at (0,0) {开始};

% 向右排列
\node[flow-process, right=of start] (step1) {步骤一};
\node[flow-decision, right=of step1] (decide) {判断?};
\node[flow-process, right=of decide] (step2) {步骤二};

% 连线
\draw[flow-arrow] (start) -- (step1);
\draw[flow-arrow] (step1) -- (decide);
\draw[flow-arrow] (decide.east) -- (step2.west)
  node[flow-label, pos=0.5, above=2pt] {是};
```

### 2. 决策节点双分支

```latex
\node[flow-decision] (check) {是否通过?};

% "是"分支（右侧）
\node[flow-process, right=of check] (pass) {通过处理};
\draw[flow-arrow] (check.east) -- (pass.west)
  node[flow-label, pos=0.5, above=2pt] {是};

% "否"分支（下方）
\node[flow-process, below=of check] (fail) {失败处理};
\draw[flow-arrow] (check.south) -- (fail.north)
  node[flow-label, pos=0.5, right=4pt] {否};
```

### 3. 子过程分组

使用 `fit` 库将多个节点框在一个虚线背景中：

```latex
\begin{scope}[on background layer]
  \node[flow-subprocess, fit=(node1)(node2)(node3)] (sub) {};
  \node[above right=6pt of sub.north west, font=\small\bfseries, text=SubColor]
    {子过程：用户认证};
\end{scope}
```

### 4. 自定义节点大小

```latex
% 单独调整某个节点的宽度
\node[flow-process, minimum width=150pt] (wide-node) {这是一个较宽的节点};

% 调整决策菱形大小
\node[flow-decision, minimum width=80pt] (big-decision) {较大的判断};
```

### 5. 多条折线汇聚

```latex
% 三个错误节点都连到同一个结束点
\draw[flow-arrow] (err1.south) |- (end.west);
\draw[flow-arrow] (err2.south) |- (end.west);
\draw[flow-arrow] (err3.south) |- (end.west);
```

---

## 布局规则

1. **第一个节点**：使用绝对坐标 `at (0,0)` 放置
2. **垂直方向**：主流程使用 `below=of` 垂直排列
3. **水平方向**：主流程使用 `right=of` 水平排列
4. **决策分支**：
   - 垂直布局：分支放在左右两侧
   - 水平布局：分支放在上下两侧
5. **折线连接**：使用 `|-` 和 `-|` 绘制直角折线

---

## 注意事项

- 决策节点内的文字如果较长，用 `\\` 手动换行
- 箭头标签放在连线的右侧或上方，避免遮挡线条
- 复杂流程图建议使用子过程分组提高可读性
- 中文支持需要使用 XeLaTeX 编译器和 ctex 文档类
- 决策节点的 `aspect` 参数控制菱形的宽高比，默认为 1.3
