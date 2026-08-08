# 组织架构图模板 (Organization Tree)

## 概述

组织架构图模板用于绘制树形的组织架构图、团队结构图等。支持 2-3 层级，每个节点可包含职位和姓名。使用直角分叉连接线，美观专业。

**样式前缀：** `org-`

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
\usetikzlibrary{trees}

\begin{document}

\begin{figure}[htbp]
  \centering
  \input{templates/org-tree/template.tex}
  \caption{公司组织架构图}
\end{figure}

\end{document}
```

---

## 可调参数

### 颜色参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `MainColor` | 主色，用于根节点和连接线 | 深蓝 `#1A365D` |
| `SubColor` | 次色，用于二级节点 | 中蓝 `#2B6CB0` |
| `SmallColor` | 辅助色，用于三级节点 | 浅蓝 `#4299E1` |
| `TinyColor` | 极浅色，用于背景填充 | 淡蓝 `#EBF8FF` |
| `DarkColor` | 文字颜色 | 深灰 `#1A202C` |
| `AccentColor` | 强调色 | 红色 `#C53030` |

### 布局参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\orgTreeGrow` | 树的生长方向：`down`/`up`/`left`/`right` | `down` |
| `\orgLevelOneSep` | 第一层到第二层的距离 | `60pt` |
| `\orgLevelTwoSep` | 第二层到第三层的距离 | `50pt` |
| `\orgSiblingOneSep` | 第一层子节点间距 | `20pt` |
| `\orgSiblingTwoSep` | 第二层子节点间距 | `15pt` |

### 节点尺寸参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\orgNodeWidth` | 普通节点文本宽度 | `90pt` |
| `\orgNodeHeight` | 节点最小高度 | `50pt` |
| `\orgRootWidth` | 根节点文本宽度 | `120pt` |

### 线条参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\orgLineThickness` | 连接线粗细 | `1.2pt` |
| `\orgLineColor` | 连接线颜色 | `MainColor` |

---

## 节点类型

| 样式名 | 级别 | 说明 |
|--------|------|------|
| `org-root` | 根节点 | 最高级别，深色填充，白色文字 |
| `org-level2` | 二级节点 | 浅色背景，用于部门总监 |
| `org-level3` | 三级节点 | 白色背景，用于基层团队 |
| `org-groupbox` | - | 部门分组虚线背景框 |
| `org-edge` | - | 连接线样式 |

---

## Tree 语法说明

### 基本结构

```latex
\node[org-root] at (0,0) {根节点内容}
  child {
    node {子节点1}
    child { node {孙节点1} }
    child { node {孙节点2} }
  }
  child {
    node {子节点2}
  };
```

### 节点内容格式

每个节点默认包含两行：
```latex
node {
  \textbf{职位名称} \\
  姓名
}
```

也可以只放一行文本：
```latex
node {部门名称}
```

---

## 常见修改示例

### 1. 增加层级（3 层 → 更多）

在子节点中继续嵌套 child：

```latex
\node[org-root] {CEO}
  child {
    node {CTO}
    child {
      node {前端负责人}
      child { node {初级工程师} }
      child { node {高级工程师} }
    }
  };
```

> **注意**：超过 3 层可能导致排版拥挤，需要调大 `level distance` 和减小节点宽度。

### 2. 调整子节点数量

增删 `child { node { ... } }` 块，同时调整 `sibling distance`：

```latex
% 如果子节点很多，增大 sibling distance
level 1/.style = {
  sibling distance = 120pt,  % 调大间距
  ...
}
```

### 3. 改变树的生长方向

修改 `\orgTreeGrow` 的值：

| 值 | 方向 | 根位置 |
|----|------|--------|
| `down` | 自上而下 | 顶部 |
| `up` | 自下而上 | 底部 |
| `right` | 从左到右 | 左侧 |
| `left` | 从右到左 | 右侧 |

```latex
\def\orgTreeGrow{right}  % 横向布局
```

### 4. 部门分组背景框

使用 `fit` 库给某组节点加背景框：

```latex
\begin{scope}[on background layer]
  \node[org-groupbox, fit=(tech1)(tech2)(tech3)] (tech-group) {};
  \node[below right=6pt of tech-group.north west,
        font=\small\bfseries,
        text=SubColor]
    {技术中心};
\end{scope}
```

> 需要先给对应的节点命名（如 `child { node (tech1) { ... } }`）。

### 5. 自定义节点样式

在节点上覆盖默认样式：

```latex
% 单独调整某个节点的宽度
child {
  node[org-level2, text width=110pt, minimum height=60pt] {
    \org-position{技术总监} \\
    \org-name{李工}
  }
}
```

### 6. 修改连接线样式

**直线连接（默认直角分叉）：**
```latex
edge from parent fork down,  % 直角分叉
```

**直线连接（非分叉）：**
移除 `edge from parent fork down`，使用默认直线。

**自定义线宽和颜色：**
```latex
level 1/.style = {
  edge from parent/.style = {
    draw = red,
    line width = 2pt,
  },
}
```

---

## 布局规则

1. **根节点**：使用绝对坐标 `at (0,0)` 放置
2. **层级关系**：通过 `child` 嵌套表示上下级
3. **同级间距**：通过 `sibling distance` 控制
4. **层级间距**：通过 `level distance` 控制
5. **连接线**：默认使用 `edge from parent fork down` 实现直角分叉

---

## 注意事项

- 使用 `trees` 库的 tree 语法时，注意括号的匹配，每个 `child` 对应一组大括号
- 根节点后面的分号 `;` 不要遗漏
- 节点命名时，名字放在 `node` 后面，如 `node (name) {内容}`
- 同级节点数量过多时，需要增大 `sibling distance` 或减小节点宽度
- 中文支持需要使用 XeLaTeX 编译器和 ctex 文档类
- 如需给节点命名以便后续引用，使用 `node (节点名) {内容}` 语法
