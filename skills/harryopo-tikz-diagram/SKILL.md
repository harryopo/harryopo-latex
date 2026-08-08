# harryopo-tikz-diagram

> 帮你快速用 TikZ 画专业的流程图、架构图、组织图，支持模板/DSL/自然语言多种输入方式

---

## 什么时候用这个 Skill

如果你遇到以下任何一种情况，这个 Skill 就能帮到你：

- 📝 **写 LaTeX 论文/报告需要插入架构图**，不想用外部工具（Visio、draw.io）来回导
- 🔄 **想把 Mermaid 图转成 TikZ 代码**，让风格和文档统一
- 🎨 **需要一张风格统一的系统架构图**，放在毕业设计或课程论文里
- 🤔 **画流程图不知道怎么开始**，对着空白 TikZ 代码发呆
- 📊 **做 PPT 需要高质量矢量图**，放大不糊的那种
- 🏢 **要画组织架构图**，部门层级关系展示
- 💡 **有个想法想用图表达出来**，但不知道怎么用 TikZ 写
- 🎯 **需要批量生成相似的图**，改几个参数就能出图
- 🐛 **TikZ 图编译报错或显示异常**，找不出原因
- 📚 **想学 TikZ 画图**，但官方文档太厚看不下去

> **💡 技巧**：只要你需要在 LaTeX 里画图，先试试这个 Skill —— 即使是很简单的图，用模板也比从零写快得多。

---

## 核心能力

### 📦 模板库：4 套模板直接用

不用从零开始写代码，复制模板改改内容就行：

| 模板 | 适用场景 | 特点 |
|------|----------|------|
| **分层架构图** | 系统架构、技术栈、产品模块 | 横向分层、每层虚线框、层间箭头 |
| **流程图** | 步骤流程、处理流程、算法流程 | 自上而下、判断节点、多种形状 |
| **组织架构图** | 部门结构、团队组成、层级关系 | 树形结构、父子节点、水平展开 |
| **UML 时序图** | 系统交互、消息传递、流程调用 | 生命线+激活条、同步/返回消息、自关联、alt/loop组合片段、阶段分区、三阶段智能布局（彻底解决文字遮盖） |

**所有模板默认采用蓝色主题：**
- 🎨 无衬线字体体系（中文微软雅黑、英文 Arial、代码 Consolas）
- 🎨 低饱和蓝灰色系（`#2C3E50` / `#B0C4DE` / `#F5F8FA`）
- 🎨 纯白模块 + 极淡蓝灰层背景 + 柔和灰蓝边框
- 🎨 6pt 圆角 + 轻阴影 + Stealth 箭头
- ✅ 完整可编译的代码
- ✅ 中文支持（XeLaTeX）
- ✅ 参数化调整（改个数就变样子）

### 🔧 DSL 转换器：YAML → TikZ

不想写 LaTeX 代码？用 YAML 描述你的图，转换器自动生成 TikZ 代码。

```yaml
type: layered-architecture
title: 我的系统架构
theme: blue
layers:
  - name: 前端层
    modules: [用户界面, 管理后台, 移动端]
  - name: 后端层
    modules: [API 服务, 业务逻辑, 数据访问]
  - name: 数据层
    modules: [数据库, 缓存, 文件存储]
```

运行一行命令，生成完整 TikZ 代码。

### 🎨 主题系统：2 套配色

| 主题 | 风格 | 适合场景 |
|------|------|----------|
| **蓝色主题**（默认） | 专业技术风，低饱和蓝灰 | 技术文档、学术论文、企业系统架构图 |
| **绿色主题** | 清新教学风 | 课件、教材、环保/生物主题 |

**蓝色主题（默认）**：

```latex
\definecolor{PaperBorder}{HTML}{B0C4DE}      % 柔和灰蓝边框
\definecolor{PaperFill}{HTML}{FFFFFF}        % 纯白模块填充
\definecolor{PaperTitle}{HTML}{2C3E50}       % 深蓝灰标题
\definecolor{PaperLayerBg}{HTML}{F5F8FA}     % 极淡蓝灰层背景
\definecolor{PaperLayerBorder}{HTML}{D8E3EE} % 层边框
\definecolor{PaperMuted}{HTML}{5D6D7E}       % 次要文字灰蓝
\definecolor{AccentOrange}{HTML}{D35400}     % 代码/强调色（柔和橙）
```

**字体配置（无衬线体系）**：
```latex
\setmainfont{Arial}[Ligatures=TeX]
\setsansfont{Arial}[Ligatures=TeX]
\setmonofont{Consolas}[Scale=0.92]
\setCJKsansfont{Microsoft YaHei}
\setCJKmainfont{Microsoft YaHei}
```

不用自己配色，模板已内置。如需自定义，改 `\tikzset` 中的颜色引用即可。

### 📖 最佳实践与踩坑指南

- 10+ 个常见问题的解决方案
- 画图前/中/后检查清单
- 调试技巧（网格对齐、红框定位、逐步调试）
- 常用速查表（节点属性、线条属性、定位语法）

---

## 使用流程（Step-by-Step）

### Step 0：信息蒸馏（用户输入杂乱时必做）

当用户给出的框架图/流程图说明**数据杂乱、不清晰、结构混乱**时，**禁止直接画图**，必须先执行信息蒸馏：

1. **提取核心实体**：从杂乱描述中识别出所有节点/模块/角色
2. **梳理层级关系**：谁在上层、谁在下层、谁包含谁
3. **识别连接关系**：谁连向谁、什么类型的连接（主流程/数据流/分支）
4. **过滤冗余信息**：去掉与图形结构无关的描述性文字

输出格式：一份精炼的节点列表 + 关系清单。

### Step 0.5：MD 示意图预审核（强制！）

**所有图形在生成 TikZ 代码前，必须先生成 Markdown 示意图给用户确认**。这是强制步骤，不得跳过。

#### 为什么要做 MD 预审核？

- 避免画完才发现结构理解错了（浪费 token 和时间）
- MD 示意图秒出，修改成本极低
- 用户可以直观看到层级和连接关系，快速纠正

#### MD 示意图格式

**分层架构图**——用缩进和分隔线表示层级：

```markdown
# 云-边-端三层架构

## 云层（Cloud Platform）
数据中心 / 云服务器
┌──────────┬──────────┬──────────┐
│ 数据存储  │ AI 训练   │ 监控中心  │
└──────────┴──────────┴──────────┘
       ↑ 聚合数据上报       ↓ 模型/结果下发
## 边缘层（Edge Computing）
边缘服务器 / 网关
┌──────────┬──────────┬──────────┐
│流处理引擎 │资源调度器 │ 缓存服务  │
└──────────┴──────────┴──────────┘
       ↑ 数据上报           ↓ 控制指令
## 端层（Edge Devices）
终端设备 / 感知节点
┌──────────┬──────────┬──────────┐
│  传感器   │ 移动设备  │ IoT 网关  │
└──────────┴──────────┴──────────┘
```

**流程图**——用箭头和缩进行表示流程走向：

```markdown
# 用户登录流程图

  ┌─────┐
  │ 开始 │
  └──┬──┘
     ↓
  ┌──────────┐
  │ 输入账号  │
  └────┬─────┘
       ↓
  ┌──────────────┐     ┌──────────────┐
  │账号格式正确？ │──否→│ 重新输入账号  │
  └────┬─────────┘     └──────┬───────┘
       │是                    │↑
       ↓                  回到上方
  ┌──────────┐
  │ 输入密码  │
  └────┬─────┘
       ↓
  ┌──────────────┐     ┌──────────────┐
  │账号密码匹配？ │──否→│ 提示错误信息  │
  └────┬─────────┘     └──────┬───────┘
       │是                    │↑
       ↓                  回到上方
  ┌──────────┐
  │ 登录成功  │
  └────┬─────┘
       ↓
  ┌─────┐
  │ 结束 │
  └─────┘
```

**组织架构图**——用缩进树表示层级：

```markdown
# 软件公司组织架构

总经理（👤）
├── 技术部（💻）
│   ├── 前端
│   ├── 后端
│   ├── 测试
│   └── 运维
├── 产品部（💡）
│   ├── 产品经理
│   └── UI设计
├── 市场部（📢）
│   ├── 推广
│   └── 销售
└── 人事部（👥）
```

**UML 时序图**——用竖向生命线表示：

```markdown
# 用户下单时序图

用户        前端         后端         数据库
 │          │            │            │
 │──下单──→ │            │            │
 │          │──创建订单→ │            │
 │          │            │──插入订单─→│
 │          │            │←──订单ID───│
 │          │←──订单信息──│            │
 │←─订单确认─│            │            │
 │          │            │            │
```

#### 预审核流程

1. **生成 MD 示意图**：使用上面的格式，清晰展示结构
2. **询问用户**：「以上 MD 示意图是否正确？请确认结构、节点名称、连接关系，确认后我将生成 TikZ 代码。」
3. **等待用户确认**：用户说"可以"/"确认"/"没问题"后才进入下一步
4. **如果有修改**：根据反馈修改 MD 示意图，再次确认
5. **确认后询问配色**：「请选择配色主题：蓝色（专业技术风，默认）还是绿色（清新教学风）？」
6. **确认后生成 TikZ**：严格按照确认后的 MD 结构和选定配色绘制

### Step 1：确定你要画什么图

先想清楚你的图属于哪种类型：

| 你的需求 | 推荐图类型 |
|----------|------------|
| 展示系统的分层结构（前端/后端/数据库） | 分层架构图 |
| 展示一个过程的步骤（登录流程、审批流程） | 流程图 |
| 展示部门/团队的层级关系 | 组织架构图 |
| 展示系统间/模块间的消息交互顺序 | UML 时序图 |

> **💡 技巧**：拿不准的时候，先在纸上画个草图，看看更像哪种。

### Step 2：选择输入方式

三种方式任选，按推荐程度排序：

| 方式 | 难度 | 速度 | 适合谁 |
|------|------|------|--------|
| **模板复制** | ⭐ | ⭐⭐⭐⭐⭐ | 初学者、赶时间 |
| **DSL 描述** | ⭐⭐ | ⭐⭐⭐⭐ | 喜欢简洁、批量生成 |
| **自然语言** | ⭐ | ⭐⭐⭐ | 完全不会 TikZ |

**模板复制**：从模板库复制代码，改文字和数量就行。
**DSL 描述**：用 YAML 写结构，运行转换器生成 TikZ。
**自然语言**：告诉我你想画什么，我帮你生成代码（需先过 MD 预审核）。

### Step 3：调整样式和主题

选好模板后，根据需要调整：

1. **改文字**：把模板里的模块名换成你自己的
2. **调数量**：增加/删除模块（复制粘贴节点代码）
3. **换主题**：改 `\def\theme{blue}` 为 `green`
4. **调大小**：改 `text width`、`minimum height`、间距
5. **调颜色**：参考主题系统，自定义颜色

### Step 4：编译验证

用 XeLaTeX 编译你的文档：

```bash
xelatex your-file.tex
```

> **⚠️ 注意**：必须用 XeLaTeX，中文才能正常显示。用 pdflatex 会乱码或空白。

如果编译报错，先看「常见问题」章节，80% 的问题都能在那里找到答案。

### Step 5：迭代优化

第一次画出来可能不满意，很正常。按这个顺序调整：

1. **布局对不对** → 调整模块位置、间距
2. **文字清不清** → 调整大小、换行、对齐
3. **颜色好不好** → 换主题、调深浅
4. **细节精致度** → 圆角、阴影、箭头样式

---

## 模板库使用指南

### 模板一：分层架构图（v2 Nature无衬线风格）

#### v2 设计原则（参考 example-paper-structure 布局经验）

| 原则 | 说明 |
|------|------|
| **无阴影** | 干净扁平，`drop shadow` 会造成视觉噪音，移除 |
| **居中对齐** | `align=center`，模块内容居中层次清晰 |
| **宽松内边距** | `inner sep=8pt`，不拥挤 |
| **标题浮于框上** | 层标题用 `$(box.north west)+(0,4pt)$` 偏移，不用 `fill=white` 打断虚线边框 |
| **图例嵌入内部** | 放在 tikzpicture 内部右下角，避免额外 center 环境 |
| **无hfuzz hack** | 不使用 `\hfuzz=60pt` 掩盖溢出，精确计算间距 |
| **全图无衬线** | Arial + Microsoft YaHei，不用 Times New Roman |

#### v2 间距常量

```latex
\def\ModW{4.0cm}       % 模块宽度
\def\ModH{1.5cm}       % 模块高度
\def\ModGap{0.55cm}    % 同层模块水平间距
\def\LayerGap{1.6cm}   % 层间距
\def\LayerPad{12pt}    % 层框内边距
```

#### 模块内容子样式

模块内用分组样式控制文字层次：
- `{\mod-title 模块名}` — 加粗深蓝灰标题
- `{\mod-desc 描述文字}` — 小号灰色描述
- `{\mod-tech 技术栈}` — 等宽橙色技术术语

```latex
\node[module] (L1a) {
    {\mod-title 数据存储}\\[2pt]
    {\mod-desc 海量数据持久化}\\[1pt]
    {\mod-desc 分布式文件系统}
};
```

#### 适用场景

- 系统架构图（前端/后端/数据库）
- 技术栈分层展示
- 产品模块图
- 任何有"层"概念的图

#### 参数说明

| 参数 | 在哪里改 | 说明 |
|------|----------|------|
| 层数 | 复制/删除层代码块 | 推荐 2-4 层 |
| 每层模块数 | 复制/删除 node | 推荐每层 2-5 个 |
| 模块宽度 | `\ModW` | 默认4.0cm，A4纸3列=13cm+边距 |
| 层间距 | `\LayerGap` | 默认1.6cm |
| 模块间距 | `\ModGap` | 默认0.55cm |
| 主题色 | 参考「主题系统」章节 | 整体配色 |

#### 最小复制粘贴示例（v2）

```latex
\usetikzlibrary{positioning, fit, backgrounds, arrows.meta, calc}

% Nature配色（已在导言区定义）
% \definecolor{PaperBorder}{HTML}{B0C4DE}
% \definecolor{PaperFill}{HTML}{FFFFFF}
% \definecolor{PaperTitle}{HTML}{2C3E50}
% \definecolor{PaperMuted}{HTML}{7F8C8D}
% \definecolor{AccentOrange}{HTML}{D35400}
% \definecolor{PaperLayerBg}{HTML}{F5F8FA}
% \definecolor{PaperLayerBorder}{HTML}{D8E3EE}

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
    node distance=0pt and 0.55cm, >=Stealth, line width=0.7pt,
    every node/.style={inner sep=0pt, outer sep=0pt},
    module/.style={rectangle,draw=PaperBorder,fill=PaperFill,line width=0.8pt,
        text width=4cm,minimum height=1.5cm,align=center,rounded corners=5pt,
        font=\small\sffamily,text=PaperTitle,inner sep=8pt},
    mod-title/.style={font=\small\sffamily\bfseries,text=PaperTitle},
    mod-desc/.style={font=\footnotesize\sffamily,text=PaperMuted},
    layer-box/.style={draw=PaperLayerBorder,fill=PaperLayerBg,line width=0.7pt,
        dashed,dash pattern=on 4pt off 3pt,rounded corners=8pt,inner sep=12pt},
    layer-title/.style={font=\normalsize\sffamily\bfseries,text=PaperTitle,
        anchor=north west,inner sep=0pt},
    arr/.style={->,>=Stealth,thick,PaperBorder},
]

% 第一层
\node[module] (L1a) at (0,0) {{\mod-title 模块A}\\[2pt]{\mod-desc 描述}};
\node[module, right=0.55cm of L1a] (L1b) {{\mod-title 模块B}\\[2pt]{\mod-desc 描述}};
\node[module, right=0.55cm of L1b] (L1c) {{\mod-title 模块C}\\[2pt]{\mod-desc 描述}};
\begin{scope}[on background layer]
  \node[layer-box, fit=(L1a)(L1b)(L1c)] (box1) {};
\end{scope}
\node[layer-title] at ($(box1.north west)+(0,4pt)$) {第一层：表示层};

% 第二层（定位关键：below=\LayerGap of L1a.south west, anchor=north west）
\node[module, below=1.6cm of L1a.south west, anchor=north west] (L2a) {{\mod-title 模块D}};
\node[module, right=0.55cm of L2a] (L2b) {{\mod-title 模块E}};
\begin{scope}[on background layer]
  \node[layer-box, fit=(L2a)(L2b)] (box2) {};
\end{scope}
\node[layer-title] at ($(box2.north west)+(0,4pt)$) {第二层：业务层};

% 箭头
\draw[arr] (L1a.south) -- (L2a.north);
\draw[arr] (L1b.south) -- (L2a.north);
\draw[arr] (L1c.south) -- (L2b.north);

\end{tikzpicture}
\caption{图标题}
\end{figure}
```

#### 修改示例：加一个模块

```latex
% 原来的三个模块
\node[module] (L1a) {...};
\node[module, right=0.55cm of L1a] (L1b) {...};
\node[module, right=0.55cm of L1b] (L1c) {...};

% 新增：在 C 的右边加 D
\node[module, right=0.55cm of L1c] (L1d) {{\mod-title 模块D}\\[2pt]{\mod-desc 描述}};

% 更新 fit！
\begin{scope}[on background layer]
\node[layer-box, fit=(L1a)(L1b)(L1c)(L1d)] (box1) {};  % 加了 L1d
\end{scope}
```

> **⚠️ 注意**：加了模块后，`fit=(...)` 里也要加上新节点的名字，否则虚线框包不住它！下一层第一个节点的 `below=of` 引用上一层第一个节点（如 L1a）保持对齐。

#### 右侧英文标签 + 箭头标签

```latex
% 右侧英文标签（与 layer-title 对称）
\node[layer-tag] at ($(box.north east)+(0,4pt)$) {English Label};
% layer-tag 样式：font=\footnotesize\sffamily\itshape, text=PaperMuted, anchor=north east

% 带标签的箭头
\draw[arr] (a.south) -- (b.north)
  node[midway, fill=white, inner sep=2pt, font=\footnotesize\sffamily\bfseries,
       text=PaperBorder, anchor=west, xshift=3pt] {数据流向};
```

---

### 模板二：流程图（v2 Nature无衬线风格）

#### v2 设计原则（参考 example-paper-structure 布局经验）

| 原则 | 说明 |
|------|------|
| **无阴影** | 移除 `drop shadow`，干净扁平 |
| **宽松间距** | 节点不重叠，决策分支清晰 |
| **扁平菱形** | `aspect=2.0`，决策节点横向更宽，文字不易换行 |
| **白色标签光晕** | `edge-label` 用 `fill=white` 遮盖下方箭头线条 |
| **图例嵌入内部** | 放在 tikzpicture 右下角，不额外用 center 环境 |
| **全图无衬线** | Arial + Microsoft YaHei，不用 Times New Roman |

#### v2 间距常量

```latex
\def\flowNodeW{3.6cm}      % 节点宽度
\def\flowNodeH{1.0cm}      % 节点高度
\def\flowVGap{0.9cm}       % 主流程节点垂直间距（避免菱形重叠）
\def\flowHGap{2.4cm}       % 分支节点水平偏移
\def\flowLoopBack{0.8cm}   % 分支返回线向内回退距离
\def\flowDecisionW{2.2cm}  % 菱形宽度
\def\flowDecisionH{1.2cm}  % 菱形高度
\def\flowDecisionAspect{2.0} % 宽高比：越大越扁平
```

#### 节点类型

| 节点样式 | 形状 | 用途 |
|----------|------|------|
| `flow-startend` | 圆角矩形 | 开始/结束 |
| `flow-process` | 矩形 | 处理步骤 |
| `flow-decision` | 扁平菱形 | 判断/条件 |
| `flow-io` | 梯形 | 输入/输出 |

#### 最小复制粘贴示例（v2）

```latex
\usetikzlibrary{positioning, arrows.meta, shapes.geometric, calc}

% Nature配色（已在导言区定义）
% \definecolor{PaperBorder}{HTML}{B0C4DE}
% \definecolor{PaperFill}{HTML}{FFFFFF}
% \definecolor{PaperTitle}{HTML}{2C3E50}
% \definecolor{PaperMuted}{HTML}{7F8C8D}
% \definecolor{AccentOrange}{HTML}{D35400}
% \definecolor{PaperLayerBg}{HTML}{F5F8FA}

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
    node distance = 0.9cm and 2.4cm, >=Stealth, line width=0.7pt,
    every node/.style={inner sep=0pt, outer sep=0pt},
    flow-startend/.style={rectangle, draw=AccentOrange, fill=AccentOrange!12,
        line width=1.0pt, rounded corners=16pt, minimum width=3.6cm,
        minimum height=1.0cm, align=center, font=\small\sffamily\bfseries,
        text=PaperTitle, inner sep=6pt},
    flow-process/.style={rectangle, draw=PaperBorder, fill=PaperFill,
        line width=0.8pt, rounded corners=5pt, minimum width=3.6cm,
        minimum height=1.0cm, align=center, font=\small\sffamily,
        text=PaperTitle, inner sep=8pt},
    flow-decision/.style={diamond, draw=PaperBorder, fill=PaperLayerBg,
        line width=0.8pt, aspect=2.0, minimum width=2.2cm, minimum height=1.2cm,
        align=center, font=\small\sffamily\bfseries, text=PaperTitle, inner sep=2pt},
    flow-arrow/.style={->,>=Stealth,thick,PaperBorder},
    flow-arrow-branch/.style={->,>=Stealth,thick,PaperMuted,dashed},
    flow-label/.style={fill=white, font=\footnotesize\sffamily\bfseries,
        text=PaperMuted, inner sep=2pt, outer sep=0pt},
]

% 开始
\node[flow-startend] (start) at (0,0) {开始};
\node[flow-process, below=0.9cm of start] (input) {输入账号};
\node[flow-decision, below=0.9cm of input] (check) {格式正确？};
\node[flow-process, below=0.9cm of check] (success) {登录成功};
\node[flow-startend, below=0.9cm of success] (end) {结束};

% 错误分支
\node[flow-process, left=2.4cm of check] (err) {提示错误};

% 连线
\draw[flow-arrow] (start) -- (input);
\draw[flow-arrow] (input) -- (check);
\draw[flow-arrow] (check.south) -- (success.north)
    node[flow-label, pos=0.5, anchor=west, xshift=3pt] {是};
\draw[flow-arrow] (success) -- (end);

\draw[flow-arrow-branch] (check.west) -- (err.east)
    node[flow-label, pos=0.5, anchor=south, yshift=2pt] {否};
\draw[flow-arrow-branch] (err.south) -- ++(0,-0.8cm) -| ($(input.west)+(-0.5cm,0)$)
    -- (input.west);

\end{tikzpicture}
\caption{用户登录流程图}
\end{figure}
```

#### v2 关键防重叠技巧

1. **决策节点扁平化**：`aspect=2.0` 让菱形更宽，避免"账号格式正确？"这种文字被挤成三行。
2. **主流程垂直间距 ≥ 0.9cm**：太小时菱形和上下矩形会视觉重叠。
3. **分支节点用 `left=\flowHGap of decision`**：不用 `xshift` hack，定位标准且可预测。
4. **返回线用 `-|` 折回**：从分支节点向下 → 再折回目标节点左侧，路径清晰不交叉。
5. **标签带 `fill=white`**：即使箭头从标签后方穿过，也能被白色光晕遮盖。

#### 修改示例：加一个判断步骤

在输入账号和登录成功之间加一个判断：

```latex
% 原来的步骤
\node[flow-process, below=\flowVGap of start] (input) {输入账号};

% 新增判断
\node[flow-decision, below=\flowVGap of input] (check-format) {账号格式正确？};

% 原来的成功节点改为从 check-format 下方定位
\node[flow-process, below=\flowVGap of check-format] (success) {登录成功};

% 新增连线
\draw[flow-arrow] (input.south) -- (check-format.north);
\draw[flow-arrow] (check-format.south) -- (success.north)
    node[flow-label, pos=0.5, anchor=west, xshift=3pt] {是};
```

---

### 模板三：组织架构图

#### 适用场景

- 公司部门结构
- 项目团队组成
- 学生会/社团架构
- 任何树形层级关系

#### 层级说明

- **第 0 层**：顶层（1 个节点，比如 CEO、总经理）
- **第 1 层**：一级部门（3-5 个）
- **第 2 层**：二级部门/小组（若干）

支持横向展开和纵向展开两种布局。

#### 最小复制粘贴示例

```latex
\usetikzlibrary{positioning, fit, arrows.meta, trees}

% ... 文档中间 ...

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  org-top/.style={
    draw=MainColor, very thick, rounded corners=3pt,
    fill=MainColor!20, text width=3cm, minimum height=1.2cm,
    align=center, font=\small\bfseries
  },
  org-dept/.style={
    draw=SubColor, thick, rounded corners=3pt,
    fill=white, text width=2.4cm, minimum height=1cm,
    align=center, font=\small
  },
  org-team/.style={
    draw=SmallColor, thin, rounded corners=2pt,
    fill=SmallColor!10, text width=2cm, minimum height=0.8cm,
    align=center, font=\footnotesize
  },
  arr/.style={-, >=Stealth, thick, MainColor!50!white}
]

% 顶层
\node[org-top] (ceo) at (0,0) {总经理};

% 第一层（部门）
\node[org-dept, below=30pt of ceo, xshift=-3cm] (tech) {技术部};
\node[org-dept, below=30pt of ceo] (product) {产品部};
\node[org-dept, below=30pt of ceo, xshift=3cm] (market) {市场部};

% 第二层（小组，以技术部为例）
\node[org-team, below=20pt of tech, xshift=-1.5cm] (fe) {前端组};
\node[org-team, below=20pt of tech, xshift=1.5cm] (be) {后端组};

% 连线
\draw[arr] (ceo.south) -- (tech.north);
\draw[arr] (ceo.south) -- (product.north);
\draw[arr] (ceo.south) -- (market.north);
\draw[arr] (tech.south) -- (fe.north);
\draw[arr] (tech.south) -- (be.north);

\end{tikzpicture}
\caption{公司组织架构图}
\end{figure}
```

#### 修改示例：给产品部加小组

```latex
% 产品部节点已存在
\node[org-dept, below=30pt of ceo] (product) {产品部};

% 新增两个小组
\node[org-team, below=20pt of product, xshift=-1.2cm] (pm) {产品经理组};
\node[org-team, below=20pt of product, xshift=1.2cm] (ui) {UI 设计组};

% 新增连线
\draw[arr] (product.south) -- (pm.north);
\draw[arr] (product.south) -- (ui.north);
```

> **💡 技巧**：如果同一层节点太多放不下，可以调整 `xshift` 让它们分散开，或者缩小 `text width`。

---

### 模板四：UML 时序图（v5.1 三阶段紧凑布局）

#### 适用场景

- API 调用流程（前后端交互、微服务通信）
- 一键部署流程（多服务编排）
- 业务流程交互（用户操作→系统响应）
- 任何需要展示对象间按时间顺序消息传递的场景

#### v5.1 核心创新：三阶段智能布局

时序图最大的痛点是**文字遮盖**（标签盖住箭头/生命线/激活条）。v5.1 采用**三阶段绘制架构**彻底解决：

| 阶段 | 开关 | 绘制内容 | 说明 |
|------|------|----------|------|
| **Pass 1 (Dry Run)** | `\geomfalse\lblfalse` | 仅推进Y游标、标记片段边界coordinate | 不绘制任何可见元素，计算最终Y位置 |
| **Pass 2 (Geometry)** | `\geomtrue\lblfalse` | 生命线、激活条、箭头、片段框、分隔线 | **所有几何元素，NO TEXT** |
| **Pass 3 (Labels)** | `\geomfalse\lbltrue` | 仅文字标签（fill=white光晕） | **最后绘制，白色光晕遮盖一切** |
| **Final Layer** | — | 参与者头部、片段名、条件标签、图例、标题 | 最最顶层 |

核心原理：**同一消息序列在3个Pass中重复调用3次**，通过`\ifgeom`/`\iflbl`开关控制每次绘制什么内容。标签最后绘制 → `fill=white, inner sep=2pt` 白色光晕100%遮盖下方几何元素。

#### 紧凑版间距常量（v5.1）

```latex
\def\seqGapMsg{0.88}    % 同步消息间距（cm）
\def\seqGapRet{1.00}    % 返回消息间距（cm）
\def\seqGapSelf{1.40}   % 自关联间距（cm）
\def\seqGapPhase{0.28}  % 阶段分隔线间距（cm）
\def\seqFragPad{0.15}   % 片段框内边距（cm）
\def\seqSelfLoopH{0.50} % 自关联U型高度（cm）
```

对比宽松版（v5），内容密度提升约40%，同等内容高度减少约35%。如需更宽松可乘1.3系数。

#### 宏速查表

| 宏 | 用途 | 参数说明 |
|----|------|----------|
| `\seqphase{名称}` | 阶段横线+左侧标签 | 阶段名 |
| `\seqmsg{from}{to}{文字}` | 同步消息 | from X坐标, to X坐标, 标签文字 |
| `\seqret{from}{to}{文字}` | 返回消息（虚线空心箭头） | 同上，无激活条 |
| `\seqself{x}{文字}` | 自关联（U型箭头） | 参与者X坐标, 标签文字 |
| `\seqadv{厘米数}` | 手动推进Y游标 | 推进距离 |
| `\seqmarkpt{名}{x,y}` | 标记coordinate点 | 点名, 坐标 |

#### UML 元素支持

- ✅ **激活条(Activation)**：自动在消息接收者生命线上绘制，第一个参与者（User）不画
- ✅ **组合片段 alt**：虚线圆角框 + 左上角五边形"alt"标签 + 分支条件 + 虚线水平分隔线
- ✅ **组合片段 loop**：虚线圆角框 + 五边形"loop"标签 + 循环条件
- ✅ **阶段分组**：水平分隔线 + 左侧加粗阶段名
- ✅ **自关联**：U型实线箭头 + 下方标签
- ✅ **右下角图例+术语表**：纯TikZ绘制，不嵌套tikzpicture，避免bbox错乱
- ✅ **标题内嵌**：图底部居中，中英文分两行，精确bbox控制

#### 纸张尺寸速查

| 参与者数 | 宽度 | 消息数 | 建议纸张尺寸 |
|----------|------|--------|-------------|
| 4个 | ~10cm | 10条 | 14cm × 20cm |
| 5个 | ~12cm | 15条 | 17cm × 25cm |
| 7个 | ~18cm | 20条 | 23cm × 31cm |

#### 完整示例

参见 `examples/example-sequence-diagram.tex`（一键部署模型时序图，7参与者完整演示）。

#### 时序图设计铁律（10条）

1. **三阶段架构**：消息序列必须在 Pass1/2/3 中保持**完全相同的调用顺序**，仅通过`\ifgeom`/`\iflbl`开关控制绘制内容。
2. **标签最后绘制**：所有文字标签在 Pass3/Final Layer 绘制，`fill=white+inner sep=2pt`白色光晕遮盖一切。
3. **禁止嵌套tikzpicture**：图例中用`\makebox+\rule`简单符号代替，否则bbox计算错误。
4. **第一个参与者不画激活条**：`\seqmsg`宏自动判断`#2`是否等于`\seqFirstActor`。
5. **条件标签在Final Layer定位**：不要通过Y游标在消息流中绘制条件标签，在Final Layer基于fragbox坐标精确定位。
6. **标签偏移量**：同步消息标签在箭头中点上方2pt，返回消息在中点下方2pt，自关联在U型底下方1pt。
7. **组合片段边界**：Pass1中用`\seqmarkpt`标记nw/ne/sw/se四角，Pass2在background layer用fit库自动包裹。
8. **alt分支分隔**：上分支结束后`\seqadv{0.35}`→`\seqmarkpt{alt-mid}`→`\seqadv{0.08}`→下分支→`\seqadv{0.22}`→标记sw/se。
9. **五边形折角尺寸**：alt用`(0.60,0)--(0,-0.32)--(-0.18,-0.18)--(-0.42,0)`，loop用`(0.95,0)--(0,-0.32)--(-0.18,-0.18)--(-0.77,0)`。
10. **标题内嵌bbox**：标题放在tikzpicture内部底部，用`(title-cx |- title-pos)`语法定位，bbox通过`bb-bottom`坐标精确控制。
11. **视觉丰富性取舍**：参与者头部用`fill=ActorFill`（淡紫`#E8E4F3`）而非纯白，自关联保留`ActColor`激活条填充，标签加`fill=white`光晕防遮挡——这些细节让图"有质感"但不杂乱。若追求极简，可去掉激活条和标签背景。
12. **PDF空白页修复**：若编译后出现空白页，检查`paperheight`是否足够容纳内容（建议32cm），以及`\path[use as bounding box]`的顶部Y坐标是否过小（建议≥1.2cm）。

---

## DSL 使用指南

### 什么是 DSL？为什么用它？

DSL（Domain Specific Language，领域特定语言）就是用一种简单的格式描述你的图，然后让程序自动生成 TikZ 代码。

**为什么用 DSL？**

- ✅ **更简洁**：几十行 YAML 顶几百行 TikZ 代码
- ✅ **更易读**：不用懂 TikZ 语法也能看懂结构
- ✅ **更好维护**：改一个地方，自动更新所有相关代码
- ✅ **批量生成**：改几个参数就能出一堆相似的图

**什么时候不用 DSL？**

- 只画一次，以后不改 → 直接用模板复制
- 布局特别复杂，自由度要求高 → 手写 TikZ

### 运行转换器

```bash
cd converter
python dsl_to_tikz.py your-diagram.yaml > output.tex
```

然后把 `output.tex` 里的内容复制到你的 LaTeX 文档里。

### 图类型一：分层架构图 DSL

#### DSL 格式

```yaml
type: layered-architecture     # 固定值
title: 图标题                   # 可选，图的标题
theme: blue                    # 主题：blue / green

layers:                        # 层列表，从上到下
  - name: 第一层名称            # 层的名字（显示在左上角）
    description: 层说明         # 可选，括号里的说明文字
    modules:                   # 该层的模块
      - name: 模块1名称         # 模块名（加粗）
        desc: 模块描述          # 可选，模块下面的描述
      - name: 模块2名称
        desc: 模块描述
      # ... 更多模块

  - name: 第二层名称
    modules:
      - name: 模块3名称
        desc: 模块描述
      # ...

options:                       # 可选，自定义参数
  module_width: 2.4cm          # 模块宽度
  module_height: 1.4cm         # 模块高度
  layer_spacing: 1.8cm         # 层间距
  module_spacing: 12pt         # 模块间距
```

#### 完整示例

```yaml
type: layered-architecture
title: 智配产品架构图
theme: blue

layers:
  - name: 智配桌面安装器
    description: Electron 桌面应用
    modules:
      - name: 硬件检测模块
        desc: GPU / 显存 / 内存\\CPU / 操作系统
      - name: 模型推荐引擎
        desc: 根据硬件推荐\\最佳模型方案
      - name: 一键部署器
        desc: 自动化安装\\Ollama + UI
      - name: 管理后台
        desc: 模型管理 | 监控 | 知识库

  - name: 后端服务
    description: Python FastAPI
    modules:
      - name: 部署引擎
        desc: Ollama 管理\\模型管理
      - name: 运维监控
        desc: GPU/内存采样\\进程守护
      - name: API 服务
        desc: FastAPI\\REST 接口

  - name: 开源生态
    description: 底层依赖
    modules:
      - name: Ollama
        desc: 推理引擎
      - name: Open WebUI
        desc: 聊天界面
      - name: 模型文件
        desc: GGUF 格式
```

---

### 图类型二：流程图 DSL

#### DSL 格式

```yaml
type: flowchart               # 固定值
title: 图标题                  # 可选
theme: blue                   # 主题

nodes:                        # 节点列表（按顺序）
  - id: s1                    # 节点 ID（唯一，用于连线）
    type: start               # 类型：start / process / decision / io / end
    text: 开始                # 显示文字

  - id: s2
    type: process
    text: 输入账号密码

  - id: s3
    type: decision
    text: 信息是否正确？

  - id: s4
    type: process
    text: 登录成功

  - id: s5
    type: end
    text: 结束

edges:                        # 连线列表
  - from: s1                  # 起点节点 ID
    to: s2                    # 终点节点 ID
    label: ""                 # 可选，连线上的文字

  - from: s2
    to: s3

  - from: s3
    to: s4
    label: 是

  - from: s3
    to: s2
    label: 否
    style: dashed             # 可选：dashed / dotted
```

#### 完整示例

```yaml
type: flowchart
title: 用户注册流程
theme: green

nodes:
  - id: s1
    type: start
    text: 开始注册

  - id: s2
    type: process
    text: 填写邮箱和密码

  - id: s3
    type: decision
    text: 邮箱格式是否正确？

  - id: s4
    type: process
    text: 发送验证邮件

  - id: s5
    type: decision
    text: 是否验证成功？

  - id: s6
    type: process
    text: 注册完成，跳转登录

  - id: s7
    type: end
    text: 结束

edges:
  - from: s1
    to: s2
  - from: s2
    to: s3
  - from: s3
    to: s4
    label: 是
  - from: s3
    to: s2
    label: 否
    style: dashed
  - from: s4
    to: s5
  - from: s5
    to: s6
    label: 是
  - from: s5
    to: s4
    label: 重发
    style: dashed
  - from: s6
    to: s7
```

---

### 图类型三：组织架构图 DSL

#### DSL 格式

```yaml
type: org-tree                # 固定值
title: 图标题                  # 可选
theme: blue                   # 主题

root:                         # 顶层节点
  name: 总经理
  children:                   # 子节点列表
    - name: 技术部
      children:
        - name: 前端组
        - name: 后端组
        - name: 测试组
    - name: 产品部
      children:
        - name: 产品经理组
        - name: UI 设计组
    - name: 市场部
    - name: 人事部
```

#### 完整示例

```yaml
type: org-tree
title: 软件公司组织架构
theme: green

root:
  name: 总经理
  children:
    - name: 技术部
      children:
        - name: 前端开发组
        - name: 后端开发组
        - name: 测试组
        - name: 运维组
    - name: 产品部
      children:
        - name: 产品经理组
        - name: UI/UX 设计组
    - name: 市场部
      children:
        - name: 市场推广组
        - name: 销售组
    - name: 行政人事部
      children:
        - name: 人事组
        - name: 行政组
```

---

## 主题系统

### 两套主题速览

| 主题 | 主色调 | 风格 | 适合 |
|------|--------|------|------|
| **蓝色主题**（默认） | 深蓝灰 → 浅蓝灰 | 专业、稳重、技术感 | 学术论文、技术文档、企业系统架构图 |
| **绿色主题** | 深绿 → 浅绿 | 清新、自然、教学感 | 课件、教材、环保/生物主题 |

### 蓝色主题（默认）

```latex
\definecolor{PaperBorder}{HTML}{B0C4DE}      % 柔和灰蓝边框
\definecolor{PaperFill}{HTML}{FFFFFF}        % 纯白模块填充
\definecolor{PaperTitle}{HTML}{2C3E50}       % 深蓝灰标题
\definecolor{PaperLayerBg}{HTML}{F5F8FA}     % 极淡蓝灰层背景
\definecolor{PaperLayerBorder}{HTML}{D8E3EE} % 层边框
\definecolor{PaperMuted}{HTML}{5D6D7E}       % 次要文字灰蓝
\definecolor{AccentOrange}{HTML}{D35400}     % 代码/强调色
```

---

### 绿色主题（清新教学风）

```latex
\definecolor{PaperBorder}{HTML}{9AE6B4}      % 柔和绿边框
\definecolor{PaperFill}{HTML}{FFFFFF}        % 纯白模块填充
\definecolor{PaperTitle}{HTML}{22543D}       % 深绿标题
\definecolor{PaperLayerBg}{HTML}{F0FFF4}     % 极淡绿层背景
\definecolor{PaperLayerBorder}{HTML}{C6F6D5} % 层边框
\definecolor{PaperMuted}{HTML}{276749}       % 次要文字深绿
\definecolor{AccentOrange}{HTML}{DD6B20}     % 强调色
```

---

### 怎么切换主题

**方法一：直接替换颜色定义**

把上面某套主题的 `\definecolor` 代码复制到你的文档开头，替换掉原来的就行。

**方法二：用主题加载器**

```latex
\input{themes/theme-loader.tex}
\loadtikzsiztheme{green}  % blue 或 green
```

> **💡 技巧**：不确定选哪个主题？默认用蓝色，最安全、最通用。

---

## 常见问题与踩坑指南

### Q1：中文不显示，变成空白或方块？

**症状**：方框里的中文看不见，或者显示成一个个小方块。

**原因**（按概率排序）：
1. 用了 pdflatex 而不是 xelatex
2. 中文字体没配置

**解决方案**：

1. **确认编译器是 XeLaTeX**：
   ```bash
   xelatex your-file.tex   % 正确
   pdflatex your-file.tex  % 错误，中文会乱码
   ```

2. **确保加载了字体包**：
   ```latex
   \usepackage{fontspec}
   \setCJKmainfont{SimSun}  % 宋体，Windows 自带
   % 或
   \setCJKmainfont{Microsoft YaHei}  % 微软雅黑
   ```

> **⚠️ 注意**：harryopo 模板已经配置好了字体和 xelatex，直接用 `build.ps1` 编译就行。

---

### Q2：图太宽，右边超出页面了？

**症状**：图的右边被切掉了，或者飘到页边距外面。

**原因**：A4 纸正文宽度大约 15-16cm，模块摆太多、太宽。

**解决方案（按优先级）**：

1. **减少模块数**：合并次要模块，这是最好的办法
2. **缩小模块宽度**：`text width=2cm` 改成 `text width=1.8cm`
3. **缩小模块间距**：`right=12pt of` 改成 `right=8pt of`
4. **缩小字体**：`font=\small` 改成 `font=\footnotesize`
5. **减少描述文字**：去掉次要的描述行
6. **横向页面**（最后手段）：
   ```latex
   \usepackage{rotating}
   \begin{sidewaysfigure}
     % 你的图
   \end{sidewaysfigure}
   ```

> **💡 技巧**：先试试第 2-4 条，通常组合起来就能省出 2-3cm 宽度。

---

### Q3：箭头位置不对，从框中间穿过去了？

**症状**：箭头不是从边框上出发，而是从节点中心穿出来。

**原因**：没指定锚点，TikZ 默认用 `.center`。

**修复**：明确指定锚点：

```latex
% 正确（从下边中点出发，到上边中点结束）
\draw[arr] (a.south) -- (b.north);

% 错误（从中心出发，穿过边框）
\draw[arr] (a) -- (b);
```

**常用锚点**：
- `.north` 上、`.south` 下、`.east` 右、`.west` 左
- `.north east` 右上、`.south west` 左下（四个角）
- `.center` 中心（一般不用）

---

### Q4：背景框盖住了内容？

**症状**：背景填充色把前面的模块文字盖住了，模块看不见。

**原因**：背景框在前景层绘制，后画的盖住先画的。

**修复**：用 `on background layer` 环境把背景框放到背景层：

```latex
% 先画前景节点
\node[module] (a) {模块 A};

% 再画背景框（在背景层）
\begin{scope}[on background layer]
  \node[layerbox, fit=(a)(b)] (bg) {};
\end{scope}
```

> **⚠️ 注意**：`on background layer` 需要加载 `backgrounds` 库！
> ```latex
> \usetikzlibrary{backgrounds}
> ```

---

### Q5：虚线框（fit）大小不对，太大或太小？

**症状**：`fit=(a)(b)` 的框要么太大留白多，要么太小包不住。

**原因**：默认 `inner sep` 是固定值，内容少时框就小。

**修复**：显式设置 `inner sep`：

```latex
% 内边距 14pt（框和内容的距离）
\node[fit=(a)(b)(c), inner sep=14pt] (bg) {};
```

- 内容多 → `inner sep` 调小一点（10pt）
- 内容少 → `inner sep` 调大一点（16-20pt）
- 想让框高一点 → 加 `minimum height=2cm`

---

### Q6：多行文字不换行，`\\` 没用？

**症状**：写了 `\\` 但文字还是堆在一行。

**原因**：没设置 `align` 属性。

**修复**：加 `align=center`（或 `left` / `right`）：

```latex
% 正确
\node[text width=3cm, align=center] {第一行\\第二行};

% 错误（不换行）
\node[text width=3cm] {第一行\\第二行};
```

> **💡 技巧**：只要你用了 `\\` 换行，就必须加 `align=xxx`。

---

### Q7：图乱跑，不在我写的位置？

**症状**：图不在正文对应的位置，跑到页面顶部或底部去了。

**原因**：LaTeX 浮动体（float）的自动排版机制。

**解决方案**：

1. **推荐**：加 `[htbp]` 选项，让 LaTeX 灵活选择：
   ```latex
   \begin{figure}[htbp]
   % h=here 尽量放当前位置
   % t=top  放页面顶部
   % b=bottom 放页面底部
   % p=page 单独放一页
   ```

2. **强制放当前位置**（不推荐，可能留白）：
   ```latex
   \begin{figure}[H]  % 大写 H，需要 float 包
   ```

> **⚠️ 注意**：`[H]` 选项需要 `\usepackage{float}`，harryopo 模板已经加载了。

---

### Q8：模块看不见，只有背景和箭头？

**症状**：整张图只有虚线大框和箭头，小模块完全消失了。

**原因**：99% 是 `arrows.meta` 库没加载！`>=Stealth` 解析失败会导致整张图渲染异常。

**修复**：确保四个库都加载了：

```latex
\usetikzlibrary{
  positioning,    % 相对定位
  fit,            % 自动包裹
  backgrounds,    % 背景层
  arrows.meta     % 箭头样式 ← 这个最容易忘！
}
```

> **💡 技巧**：这是最常见的坑，没有之一。只要图显示异常，先检查这四个库加载了没。

---

### Q9：怎么改单个模块的颜色？

**需求**：想让某个模块突出显示，颜色和其他不一样。

**方法**：在节点上直接覆盖样式：

```latex
% 普通模块
\node[module] (a) {普通模块};

% 突出显示的模块（红色边框，浅红背景）
\node[module, draw=red, fill=red!10] (b) {重要模块};
```

或者定义一个新样式：

```latex
\tikzset{
  module/.style={...},          % 普通模块
  module-highlight/.style={     % 高亮模块
    module,                      % 继承 module 的所有属性
    draw=AccentColor,           % 覆盖边框颜色
    fill=AccentColor!10         % 覆盖背景色
  }
}
```

---

### Q10：怎么加更多模块/层？

**方法**：复制粘贴，三步走：

**加模块**（同一层）：
1. 复制一个已有的模块节点代码
2. 改节点名（比如 `L1d`）和文字
3. 更新 `fit=(L1a)(L1b)(L1c)(L1d)`，加上新节点

**加层**：
1. 复制一整层的代码（模块 + 背景框 + 标题）
2. 改层编号（比如 `L3a`、`bg3`）
3. 调整 `below=1.8cm of L2a` 的参照节点
4. 加层间箭头

---

### Q11：箭头太丑，怎么调好看？

**推荐箭头样式**：

```latex
% 现代三角箭头（最推荐）
arr/.style={->, >=Stealth, thick}

% 大箭头
arr/.style={->, >=Latex, thick}

% 普通箭头
arr/.style={->, >=To, thick}
```

**颜色建议**：
- 用主色的 70% 深度：`MainColor!70!black`
- 不要用纯黑，太突兀
- 不要太浅，看不清

---

### Q12：编译太慢怎么办？

**原因**：TikZ 图复杂的话，编译确实会慢一点。

**优化建议**：
1. 用 `\tikzexternalize` 外部化编译（复杂图推荐）
   ```latex
   \usetikzlibrary{external}
   \tikzexternalize
   ```
2. 调试时先注释掉复杂的图，只保留你正在改的那张
3. 图不要太多太复杂，论文里 3-5 张就够了

---

## 最佳实践清单

### 画图前

- [ ] **明确图的目的**：这张图要表达什么？给谁看？
- [ ] **选对图类型**：架构图？流程图？组织图？别混用
- [ ] **先画草稿**：在纸上或记事本里画个大概布局，确认没问题再写代码
- [ ] **确认信息流方向**：从上到下？从左到右？保持一致
- [ ] **准备好内容**：模块名、描述文字先写好，别边画边想

### 画图中

- [ ] **样式复用**：重复的属性定义成 style，不要每个节点写一堆参数
- [ ] **相对定位**：用 `right=of`、`below=of`，别硬编码坐标（第一个节点除外）
- [ ] **锚点明确**：连线时写清楚 `.south`、`.north`，别用默认的 center
- [ ] **背景层正确**：大框、底色都放 `on background layer` 里
- [ ] **中文换行**：多行文本必须加 `align=center`
- [ ] **间距统一**：同级别模块间距一致（比如都是 `12pt`）
- [ ] **层级分明**：重要的内容用粗体、深色，次要的用浅色、小字体
- [ ] **颜色和谐**：不超过 3 种主色，用同色系的深浅变化

### 画图后

- [ ] **编译检查**：用 XeLaTeX 编译，确认没有 error 和 warning
- [ ] **检查溢出**：图有没有超出页边距？文字有没有溢出节点？
- [ ] **文字清晰**：所有文字都能看清吗？字体是不是太小了？
- [ ] **箭头合理**：箭头方向符合逻辑流吗？有没有交叉？
- [ ] **对齐整齐**：同一行/列的模块对齐了吗？
- [ ] **风格统一**：所有图的配色、字体、间距一致吗？

### 调试技巧

1. **先画框再加文字**：确认布局没问题了再填内容
2. **网格对齐法**：临时画个网格，方便对齐
   ```latex
   \draw[help lines, gray!30] (0,0) grid (10,5);  % 调试完删掉
   ```
3. **红框定位法**：节点加 `draw=red` 看清楚边界
   ```latex
   \node[module, draw=red] (test) {测试};  % 调试用
   ```
4. **逐步添加**：一次只加一层或一组，加错了马上知道是哪的问题
5. **最小化复现**：图太复杂时，先做个最简版本跑通，再慢慢加东西

---

## 速查表

### 常用 TikZ 库列表

| 库名 | 用途 | 必加 |
|------|------|------|
| `positioning` | 相对定位（`right=of` 等） | ✅ |
| `fit` | 自动包裹节点（做大框） | ✅ |
| `backgrounds` | 背景层（`on background layer`） | ✅ |
| `arrows.meta` | 箭头样式（`Stealth` 等） | ✅ |
| `shapes.geometric` | 几何形状（菱形、椭圆等） | 流程图用 |
| `shapes.misc` | 杂项形状（圆角矩形等） | 可选 |
| `matrix` | 矩阵布局 | 可选 |
| `calc` | 坐标计算 | 高级用 |
| `trees` | 树状布局 | 组织图用 |
| `external` | 外部化编译（加速） | 可选 |

加载方式：
```latex
\usetikzlibrary{positioning, fit, backgrounds, arrows.meta}
```

---

### 常用节点属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `draw` | 画边框 | `draw=MainColor` |
| `fill` | 填充色 | `fill=blue!10` |
| `text width` | 文本宽度（自动换行） | `text width=3cm` |
| `minimum height` | 最小高度 | `minimum height=1.2cm` |
| `minimum width` | 最小宽度 | `minimum width=2cm` |
| `align` | 对齐方式 | `align=center` / `left` / `right` |
| `font` | 字体设置 | `font=\small` / `\bfseries` |
| `rounded corners` | 圆角 | `rounded corners=3pt` |
| `inner sep` | 内边距 | `inner sep=6pt` |
| `outer sep` | 外边距 | `outer sep=2pt` |
| `text` | 文字颜色 | `text=DarkColor` |
| `opacity` | 透明度 | `opacity=0.8` |
| `anchor` | 锚点（定位基准） | `anchor=north west` |

---

### 常用连线属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `thick` | 粗线 | — |
| `very thick` | 很粗 | — |
| `thin` | 细线 | — |
| `line width` | 线宽 | `line width=1pt` |
| `dashed` | 虚线 | — |
| `dotted` | 点线 | — |
| `->` | 后向箭头 | — |
| `<-` | 前向箭头 | — |
| `<->` | 双向箭头 | — |
| `>=Stealth` | 箭头样式 | 需 arrows.meta |
| `bend left` | 向左弯曲 | `bend left=30` |
| `bend right` | 向右弯曲 | — |
| `in` / `out` | 进出角度 | `in=0, out=90` |

---

### 定位语法速查

| 语法 | 说明 |
|------|------|
| `right=10pt of a` | 在 a 的右边 10pt |
| `left=10pt of a` | 在 a 的左边 10pt |
| `below=10pt of a` | 在 a 的下边 10pt |
| `above=10pt of a` | 在 a 的上边 10pt |
| `below right=10pt and 20pt of a` | 在 a 的右下（10pt 下，20pt 右） |
| `above left=10pt and 20pt of a` | 在 a 的左上 |
| `node distance=10pt` | 默认间距（全局） |
| `at (0,0)` | 绝对坐标（第一个节点用） |

---

### 颜色混合速查

| 语法 | 说明 |
|------|------|
| `blue!20` | 20% 蓝 + 80% 白（浅蓝） |
| `blue!50` | 50% 蓝 + 50% 白（中蓝） |
| `blue!20!red` | 20% 蓝 + 80% 红 |
| `blue!70!black` | 70% 蓝 + 30% 黑（深蓝） |
| `MainColor!70!white` | 70% 主色 + 30% 白 |
| `MainColor!20!TinyColor` | 20% 主色 + 80% 极浅色 |

> **💡 技巧**：数字越小颜色越浅，数字越大颜色越深。背景用 `!5` 到 `!20`，边框用 `!70` 到 `!100`。

---

## 完整示例

以下三个示例都可以直接复制到你的 LaTeX 文档中使用（确保加载了必要的 TikZ 库）。

---

### 示例一：智配桌面安装器系统架构图（Nature 风格分层架构）

```latex
\documentclass[12pt,a4paper]{ctexart}

\usepackage{geometry}
\geometry{left=2cm,right=2cm,top=1.8cm,bottom=1.8cm}

\usepackage{fontspec}
\usepackage{fontawesome5}
\usepackage{tikz}
\usepackage{multirow}
\usetikzlibrary{positioning, fit, backgrounds, arrows.meta, calc, shadows, matrix}

% 字体设置：全部无衬线体
\setmainfont{Times New Roman}[Ligatures=TeX]
\setsansfont{Arial}[Ligatures=TeX]
\setmonofont{Consolas}[Scale=0.92]
% 中文无衬线体（微软雅黑）
\setCJKsansfont{Microsoft YaHei}
\setCJKmainfont{Microsoft YaHei}

\newcommand{\icon}[1]{{\footnotesize\color{PaperBorder}#1}}
\newcommand{\code}[1]{{\sffamily\ttfamily\color{AccentOrange}#1}}

% 全局 TikZ 样式
\tikzset{
    flow-arrow/.style={
        -{Stealth[length=9pt, width=8pt]},
        PaperBorder,
        line width=1.4pt,
    },
    dep-arrow/.style={
        -{Stealth[length=9pt, width=8pt]},
        PaperMuted,
        line width=1.4pt,
    },
}

% 颜色（Nature 风格：极淡蓝灰 + 纯白模块 + 柔和灰蓝边框）
\definecolor{PaperBorder}{HTML}{B0C4DE}      % 柔和灰蓝边框（较浅）
\definecolor{PaperFill}{HTML}{FFFFFF}        % 纯白模块填充
\definecolor{PaperTitle}{HTML}{2C3E50}       % 深蓝灰标题
\definecolor{PaperLayerBg}{HTML}{F5F8FA}     % 层背景：极淡蓝灰
\definecolor{PaperLayerBorder}{HTML}{D8E3EE} % 层边框：更浅的灰蓝
\definecolor{PaperMuted}{HTML}{5D6D7E}       % 次要文字：灰蓝
\definecolor{AccentOrange}{HTML}{D35400}     % 代码强调：柔和橙
\definecolor{LayerTitleColor}{HTML}{2C3E50}  % 层标题色
\definecolor{ShadowColor}{HTML}{E0E8F0}      % 阴影色：极淡蓝灰

% 布局常量
\def\ColW{4.5cm}
\def\ColGap{0.5cm}
\def\ModH{1.7cm}
\def\WideH{0.95cm}
\def\IntraGap{1.5cm}
\def\InterGap{2.0cm}
\def\LayerPadX{16pt}
\def\LayerPadY{14pt}

\begin{document}

\hfuzz=60pt

% 标题
\begin{center}
  {\Large\bfseries\textcolor{PaperTitle}{智配桌面安装器系统架构图}}\\[0.3em]
  {\small\itshape\textcolor{PaperMuted}{\sffamily Zhipei Desktop Installer --- System Architecture}}
\end{center}

\vspace{0.5em}

% 架构图主体
\begin{center}
\begin{tikzpicture}[
    >=Stealth,
    line width=0.8pt,
    % ===== 模块样式 =====
    module/.style={
        rectangle,
        draw=PaperBorder,
        fill=PaperFill,
        text=PaperTitle,
        line width=0.8pt,
        text width=\ColW,
        minimum height=\ModH,
        font=\small\sffamily,
        align=left,
        rounded corners=4pt,
        inner sep=5pt,
        drop shadow={
            shadow xshift=1.5pt,
            shadow yshift=-1.5pt,
            opacity=0.05,
            color=ShadowColor
        },
    },
    module-wide/.style={
        module,
        text width=3*\ColW + 2*\ColGap,
        minimum height=\WideH,
    },
    % ===== 层虚线框 =====
    layer-box/.style={
        draw=PaperLayerBorder,
        fill=PaperLayerBg,
        line width=0.6pt,
        dashed,
        dash pattern=on 4pt off 3pt,
        inner xsep=\LayerPadX,
        inner ysep=\LayerPadY,
        rounded corners=6pt,
    },
    layer-title/.style={
        font=\normalsize\bfseries\color{LayerTitleColor}\sffamily,
        fill=white,
        inner xsep=4pt,
        inner ysep=1pt,
        outer sep=0pt,
        anchor=south west,
        xshift=4pt,
        yshift=2pt,
    },
    layer-tag/.style={
        font=\footnotesize\itshape\color{PaperMuted}\sffamily,
        fill=white,
        inner xsep=4pt,
        inner ysep=1pt,
        outer sep=0pt,
        anchor=south east,
        xshift=-4pt,
        yshift=2pt,
    },
    % ===== 箭头标签 =====
    arrow-label/.style={
        font=\small\bfseries\itshape\sffamily,
        text=PaperBorder,
        fill=white,
        inner xsep=3pt,
        inner ysep=1pt,
        anchor=west,
        xshift=8pt,
    },
]

    % ============================================================
    %  第一层：智配桌面安装器
    % ============================================================

    \node[module] (L1a) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faMicrochip}}} & \textbf{硬件检测模块}\\
                                             & \code{GPU} / \code{VRAM} / \code{RAM}\\
                                             & \code{CPU} / \code{Operating System}
        \end{tabular}
    };

    \node[module, right=\ColGap of L1a] (L1b) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faBrain}}} & \textbf{模型推荐引擎}\\
                                                           & 根据硬件推荐\\
                                                           & 最佳模型方案
        \end{tabular}
    };

    \node[module, right=\ColGap of L1b] (L1c) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faRocket}}} & \textbf{一键部署器}\\
                                                            & 自动化安装\\
                                                            & \code{Ollama} + \code{WebUI}
        \end{tabular}
    };

    % 第二行：管理后台
    \node[module-wide, below=\IntraGap of L1a.south west, anchor=north west] (L1w) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{2}{*}{\raisebox{0.5\baselineskip}{\icon{\faColumns}}} & \textbf{管理后台 (Web Dashboard)}\\
                           & 模型管理 \quad$\bullet$\quad 运维监控 \quad$\bullet$\quad 知识库 \quad$\bullet$\quad 日志
        \end{tabular}
    };

    % 第一层背景框
    \begin{scope}[on background layer]
        \node[layer-box, fit=(L1a) (L1c) (L1w)] (box1) {};
    \end{scope}

    % 层标签
    \node[layer-title] at (box1.north west) {智配桌面安装器};
    \node[layer-tag] at (box1.north east) {\sffamily Electron 桌面应用};

    % ============================================================
    %  第二层：后端服务
    % ============================================================

    \node[module, below=\InterGap of L1w.south west, anchor=north west] (L2a) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faCogs}}} & \textbf{部署引擎}\\
                                                           & \code{Ollama} 管理\\
                                                           & 模型生命周期管理
        \end{tabular}
    };

    \node[module, right=\ColGap of L2a] (L2b) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faChartLine}}} & \textbf{运维监控}\\
                                                                & \code{GPU} / 内存采样\\
                                                                & 进程守护与告警
        \end{tabular}
    };

    \node[module, right=\ColGap of L2b] (L2c) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faCode}}} & \textbf{API 服务}\\
                                                           & \code{FastAPI} 框架\\
                                                           & \code{RESTful} 接口
        \end{tabular}
    };

    % 第二层背景框
    \begin{scope}[on background layer]
        \node[layer-box, fit=(L2a) (L2c)] (box2) {};
    \end{scope}

    % 层标签
    \node[layer-title] at (box2.north west) {后端服务};
    \node[layer-tag] at (box2.north east) {\sffamily Python};

    % ============================================================
    %  第三层：开源生态
    % ============================================================

    \node[module, below=\InterGap of L2a.south west, anchor=north west] (L3a) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faServer}}} & \textbf{\code{Ollama}}\\
                                      & 本地大模型推理引擎\\
                                      & 支持多模型管理
        \end{tabular}
    };

    \node[module, right=\ColGap of L3a] (L3b) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faComments}}} & \textbf{Open WebUI}\\
                                                                 & 可扩展聊天界面\\
                                                                 & \code{RAG} / 多模态支持
        \end{tabular}
    };

    \node[module, right=\ColGap of L3b] (L3c) {
        \begin{tabular}{@{}c@{\hspace{0.2em}}l@{}}
        \multirow{3}{*}{\raisebox{1.15\baselineskip}{\icon{\faFileArchive}}} & \textbf{模型文件}\\
                                                                   & \code{Qwen} / \code{Llama} 等\\
                                                                   & \code{GGUF} 量化格式
        \end{tabular}
    };

    % 第三层背景框
    \begin{scope}[on background layer]
        \node[layer-box, fit=(L3a) (L3c)] (box3) {};
    \end{scope}

    % 层标签
    \node[layer-title] at (box3.north west) {开源生态};
    \node[layer-tag] at (box3.north east) {\sffamily 底层依赖};

    % ============================================================
    %  层间箭头
    % ============================================================

    \draw[flow-arrow]
        (box1.south) -- (box2.north)
        node[midway, arrow-label] {调用};

    \draw[dep-arrow]
        (box2.south) -- (box3.north)
        node[midway, arrow-label] {依赖};

\end{tikzpicture}
\end{center}

% 图例
\vspace{0.8em}
\begin{center}
\begin{tikzpicture}[baseline=-0.5ex]
    \node[font=\small\bfseries\sffamily, text=PaperBorder] (A1) at (0,0) {调用关系};
    \draw[flow-arrow] ([xshift=4pt]A1.east) -- ++(1.8em,0);

    \node[font=\small\bfseries\sffamily, text=PaperMuted] (A2) at (9em,0) {底层依赖};
    \draw[dep-arrow] ([xshift=4pt]A2.east) -- ++(1.8em,0);
\end{tikzpicture}
\end{center}

\end{document}
```

**特点**：
- Nature 风格：极淡蓝灰层背景 + 纯白模块 + 柔和灰蓝边框
- 全部无衬线体：中文微软雅黑、英文 Arial、代码 Consolas
- UI 图标左侧垂直居中，根据字体大小动态调整
- 技术术语统一用等宽体高亮（`\code{}`）
- 层间只有大箭头，简洁不杂乱
- 管理后台为宽模块，横跨三列

---

**特点**：
- 三层结构，层次清晰
- 白框深蓝边，专业稳重
- 层背景从浅到深再浅，有节奏感
- 虚线大框 + 实线小框，对比分明

---

### 示例二：用户登录流程图（流程图）

```latex
\usetikzlibrary{positioning, arrows.meta, shapes.geometric}

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  flow-start/.style={
    draw=MainColor, very thick, rounded corners=12pt,
    fill=MainColor!15, text width=2.8cm, minimum height=1cm,
    align=center, font=\small\bfseries
  },
  flow-process/.style={
    draw=MainColor, thick, rounded corners=3pt,
    fill=white, text width=3.5cm, minimum height=1cm,
    align=center, font=\small
  },
  flow-decision/.style={
    diamond, draw=SubColor, thick,
    fill=SubColor!10, text width=2.2cm, align=center,
    font=\small, inner sep=2pt, aspect=1.4
  },
  arr/.style={->, >=Stealth, thick, MainColor!70!black},
  arr-back/.style={->, >=Stealth, dashed, MainColor!50!white}
]

% 节点定义
\node[flow-start] (s1) {开始};

\node[flow-process, below=14pt of s1] (s2)
  {用户输入账号和密码};

\node[flow-decision, below=18pt of s2] (s3)
  {账号格式\\是否正确？};

\node[flow-process, below=18pt of s3] (s4)
  {向服务器发送登录请求};

\node[flow-decision, below=18pt of s4] (s5)
  {账号密码\\是否匹配？};

\node[flow-process, below right=14pt and 2.5cm of s5] (s6)
  {生成 Token，保存登录状态};

\node[flow-process, below=14pt of s6] (s7)
  {跳转至首页};

\node[flow-start, below=14pt of s7] (s8)
  {登录成功};

\node[flow-process, below left=14pt and 2.5cm of s5] (s9)
  {提示错误：账号或密码不正确};

% 连线
\draw[arr] (s1.south) -- (s2.north);
\draw[arr] (s2.south) -- (s3.north);

\draw[arr] (s3.south) -- node[right, font=\footnotesize] {是} (s4.north);
\draw[arr-back] (s3.west) -- ++(-1.2,0) |- node[above, pos=0.25, font=\footnotesize] {否} (s2.west);

\draw[arr] (s4.south) -- (s5.north);

\draw[arr] (s5.east) -- node[above, font=\footnotesize] {是} (s6.north);
\draw[arr] (s5.west) -- node[above, font=\footnotesize] {否} (s9.north);

\draw[arr] (s6.south) -- (s7.north);
\draw[arr] (s7.south) -- (s8.north);

\draw[arr-back] (s9.south) -- ++(0,-1) -| (s2.east);

\end{tikzpicture}
\caption{用户登录流程图}
\end{figure}
```

**特点**：
- 开始/结束用圆角矩形，醒目
- 判断节点用菱形，符合规范
- 错误返回路径用虚线，区分主流程
- 连线上有"是/否"标注，清晰易懂

---

### 示例三：软件公司组织架构图（组织树）

```latex
\usetikzlibrary{positioning, fit, arrows.meta}

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  org-ceo/.style={
    draw=MainColor, very thick, rounded corners=4pt,
    fill=MainColor!20, text width=3cm, minimum height=1.2cm,
    align=center, font=\small\bfseries
  },
  org-dept/.style={
    draw=SubColor, thick, rounded corners=3pt,
    fill=white, text width=2.4cm, minimum height=1cm,
    align=center, font=\small
  },
  org-team/.style={
    draw=SmallColor, thin, rounded corners=2pt,
    fill=SmallColor!10, text width=2cm, minimum height=0.8cm,
    align=center, font=\footnotesize
  },
  arr/.style={-, >=Stealth, thick, MainColor!40!white},
  arr-sub/.style={-, >=Stealth, thin, SubColor!40!white}
]

% 顶层
\node[org-ceo] (ceo) at (0,0) {总经理};

% 第一层：部门
\node[org-dept, below=30pt of ceo, xshift=-4.5cm] (tech) {技术部};
\node[org-dept, below=30pt of ceo, xshift=-1.5cm] (product) {产品部};
\node[org-dept, below=30pt of ceo, xshift=1.5cm] (market) {市场部};
\node[org-dept, below=30pt of ceo, xshift=4.5cm] (hr) {行政人事部};

% 第二层：小组（技术部）
\node[org-team, below=20pt of tech, xshift=-1.8cm] (fe) {前端开发组};
\node[org-team, below=20pt of tech, xshift=0cm] (be) {后端开发组};
\node[org-team, below=20pt of tech, xshift=1.8cm] (test) {测试组};

% 第二层：小组（产品部）
\node[org-team, below=20pt of product, xshift=-1.2cm] (pm) {产品经理组};
\node[org-team, below=20pt of product, xshift=1.2cm] (ui) {UI 设计组};

% 第二层：小组（市场部）
\node[org-team, below=20pt of market, xshift=-1.2cm] (promo) {市场推广组};
\node[org-team, below=20pt of market, xshift=1.2cm] (sales) {销售组};

% 第二层：小组（行政人事部）
\node[org-team, below=20pt of hr, xshift=-1.2cm] (personnel) {人事组};
\node[org-team, below=20pt of hr, xshift=1.2cm] (admin) {行政组};

% 连线（顶层 → 部门）
\draw[arr] (ceo.south) -- (tech.north);
\draw[arr] (ceo.south) -- (product.north);
\draw[arr] (ceo.south) -- (market.north);
\draw[arr] (ceo.south) -- (hr.north);

% 连线（部门 → 小组）
\draw[arr-sub] (tech.south) -- (fe.north);
\draw[arr-sub] (tech.south) -- (be.north);
\draw[arr-sub] (tech.south) -- (test.north);

\draw[arr-sub] (product.south) -- (pm.north);
\draw[arr-sub] (product.south) -- (ui.north);

\draw[arr-sub] (market.south) -- (promo.north);
\draw[arr-sub] (market.south) -- (sales.north);

\draw[arr-sub] (hr.south) -- (personnel.north);
\draw[arr-sub] (hr.south) -- (admin.north);

\end{tikzpicture}
\caption{软件公司组织架构图}
\end{figure}
```

**特点**：
- 三级层级：总经理 → 部门 → 小组
- 每级样式不同（颜色深浅、粗细），层次分明
- 同级别节点对齐整齐，视觉舒适
- 连线颜色逐级变浅，不抢注意力

---

## 学习资源

- **TikZ 官方文档**：命令行输入 `texdoc tikz` 直接打开，最权威
- **TikZ 示例库**：https://texample.net/tikz/examples/ （大量现成例子）
- **PGF/TikZ 教程**：B站/知乎搜索 "TikZ 教程"，入门级资源很多

---

*版本：v2.1 | 更新日期：2026-07-27 | 默认风格：Nature 无衬线学术风 | UML时序图支持alt/loop/激活条*
