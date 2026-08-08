# 分层架构图模板 (Layered Architecture)

## 概述

分层架构图模板用于绘制 2-5 层的系统架构图，每层包含若干模块，层之间用箭头连接。适用于软件系统架构、技术栈分层、网络协议栈等场景。

**样式前缀：** `arch-`

---

## 模板文件

- `template.tex` — 主模板文件，包含完整的 TikZ 样式和示例代码

---

## 快速开始

### 基本使用

将模板内容复制到你的 LaTeX 文档中，或使用 `\input` 引入：

```latex
\input{templates/layered-arch/template.tex}
```

### 完整示例结构

```latex
\documentclass{ctexart}
\usepackage{tikz}
\usetikzlibrary{positioning, fit, backgrounds, arrows.meta}

\begin{document}

% 在此处插入模板内容

\end{document}
```

---

## 可调参数

所有参数都在模板顶部的「可调整参数」区域定义：

### 颜色参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `MainColor` | 主色，用于层边框和标题背景 | 深蓝 `#1A365D` |
| `SubColor` | 次色，用于模块边框 | 中蓝 `#2B6CB0` |
| `SmallColor` | 辅助色 | 浅蓝 `#4299E1` |
| `TinyColor` | 极浅色，用于背景填充 | 淡蓝 `#EBF8FF` |
| `DarkColor` | 文字颜色 | 深灰 `#1A202C` |
| `AccentColor` | 强调色，用于警告/重点 | 红色 `#C53030` |

修改示例：
```latex
\definecolor{MainColor}{HTML}{22543D}  % 改为深绿色
```

### 间距参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\archLayerGap` | 层与层之间的垂直距离 | `1.2cm` |
| `\archModuleGap` | 同一层内模块之间的水平距离 | `10pt` |
| `\archBoxPadding` | 层背景框的内边距 | `14pt` |
| `\archTitleShift` | 层标题相对于背景框左上角的偏移 | `8pt` |

### 尺寸参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\archModuleWidth` | 普通模块的文本宽度 | `80pt` |
| `\archWideModuleWidth` | 宽模块的文本宽度 | `180pt` |
| `\archModuleHeight` | 模块的最小高度 | `36pt` |

### 箭头参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `\archArrowThickness` | 箭头线粗细 | `1.5pt` |
| `\archArrowTip` | 箭头形状 | `Stealth` |

可选箭头形状：`Stealth`, `Latex`, `Triangle`, `To`, `Kite` 等。

---

## 样式列表

| 样式名 | 用途 |
|--------|------|
| `arch-module` | 普通模块样式 |
| `arch-wide-module` | 宽模块样式（横跨整层） |
| `arch-layerbox` | 层背景虚线框 |
| `arch-layertitle` | 层标题样式 |
| `arch-arrow` | 双向箭头 |
| `arch-arrow-up` | 向上箭头 |
| `arch-arrow-down` | 向下箭头 |

---

## 常见修改示例

### 1. 增加/减少层数

**增加第 4 层：** 复制第 3 层的代码块，修改节点名称和内容。

```latex
% 第 4 层 —— 基础设施层
\node[arch-wide-module, below=of data-db] (infra-server) {云服务器集群};

\begin{scope}[on background layer]
  \node[arch-layerbox, fit=(infra-server)] (layer4-box) {};
\end{scope}
\node[arch-layertitle, anchor=north west, ...] at (layer4-box.north west) {基础设施层};

% 添加箭头
\draw[arch-arrow-down] (data-db.south) -- (infra-server.north);
```

**减少层数：** 删除对应的层代码块，同时删除相关的箭头连接。

### 2. 增加同层模块

```latex
% 在 ui-mobile 右侧增加一个模块
\node[arch-module, right=of ui-mobile] (ui-mini) {小程序};

% 更新 fit 中的节点列表
\node[arch-layerbox, fit=(ui-web)(ui-mobile)(ui-mini)(ui-admin)] (layer1-box) {};
```

### 3. 使用宽模块

将 `arch-module` 替换为 `arch-wide-module`：

```latex
\node[arch-wide-module, below=of biz-order] (api-gateway) {API 网关};
```

### 4. 双向箭头

使用 `arch-arrow` 样式（上下都有箭头）：

```latex
\draw[arch-arrow] (biz-user.south) -- (data-db.north -| biz-user.south);
```

### 5. 折线连接

使用 `|-`（先竖后横）或 `-|`（先横后竖）：

```latex
% 先垂直向下，再水平向右
\draw[arch-arrow-down] (biz-user.south) |- (data-db.west);

% 先水平向右，再垂直向下
\draw[arch-arrow-down] (biz-msg.east) -| (data-db.south);
```

---

## 布局规则

1. **第一个节点**：使用绝对坐标 `at (0,0)` 放置在第一层第一个位置
2. **同层节点**：使用 `right=of <前一个节点名>` 水平排列
3. **下一层节点**：使用 `below=of <上一层对应节点名>` 垂直定位
4. **背景框**：使用 `fit` 库包裹本层所有节点，放在背景层
5. **层标题**：定位在背景框的左上角

---

## 注意事项

- 每次增加或删除模块后，务必更新 `fit` 中的节点列表
- 层背景框必须放在 `on background layer` 环境中，否则会遮挡节点
- 箭头的 `-|` 和 `|-` 语法：`-|` 表示先水平后垂直，`|-` 表示先垂直后水平
- 中文支持需要使用 XeLaTeX 编译器和 ctex 文档类
