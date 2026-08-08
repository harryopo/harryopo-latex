# LaTeX 框架图/流程图 调研报告（2026-07）

> 调研时间：2026-07-07
> 目的：为智配桌面安装器项目寻找最佳的 LaTeX 画图方案
> 项目：d:\ai\latex

---

## 一、核心工具栈（已选）

| 用途 | 工具/宏包 | 状态 |
|------|----------|------|
| 通用绘图 | **TikZ** + PGF | ✅ 已使用 |
| 架构图 | TikZ + `positioning` + `fit` + `backgrounds` | ✅ 已使用 |
| 时序图 | **pgf-umlsd** | ✅ 已使用 |
| 类图 | pgf-umlcd | 可用 |
| UI 图标 | **fontawesome5** | ✅ 已使用 |
| 字体 | fontspec + Times New Roman + Courier New | ✅ 已使用 |

---

## 二、调研发现

### 2.1 架构图最佳实践（IEEE/ACM 风格）

**来源**：DrawFig 2026 网络图指南、CSDN TikZ 教程、PGF/TikZ 官方手册

**核心原则**：
1. **正交网格布局** —— 水平/垂直线，无斜线 → 消除交叉误解
2. **统一模块尺寸** —— `text width` + `minimum height` 固定，避免视觉错位
3. **between origins 对齐** —— `\matrix [row sep={1cm, between origins}, ...]` 强制中心对齐
4. **细密虚线分层** —— 层级背景框用 `dashed` + `dash pattern=on 3pt off 2pt`
5. **悬停标签定位** —— `label` + `anchor` + `xshift/yshift` 精确放标签
6. **图例分离** —— 图例独立放右下安全区，不遮挡主图

**配色方案**（学术风）：
```
主色  #2C5282 (深蓝)
辅色  #EDF2F7 (浅灰)
强调  #DD6B20 (橙红)
暗色  #1A202C (近黑)
```

### 2.2 时序图（pgf-umlsd）

**来源**：pgf-umlsd 官方手册 v0.7

**核心 API**：
```latex
\begin{sequencediagram}
  \newinst{id}{显示名称}     % 定义实例
  \begin{call}{A}{消息}{B}{返回}  % 同步调用
  \mess{A}{消息}{B}             % 异步消息
\end{sequencediagram}
```

**已知限制**：
- ⚠️ pgf-umlsd **不能与 TikZ `backgrounds` 库同时使用**（已知冲突）
- ⚠️ call/mess 内部不能使用带参数的自定义命令（参数解析冲突）
- 解决：内部用 `\texttt{}` 而不是 `\code{}` 自定义宏

### 2.3 UI 图标库

**fontawesome5（推荐）**：
- 安装：`tlmgr install fontawesome5`
- 使用：`\faIcon{github}` 或 `\faGithub`
- 文档：https://ctan.org/pkg/fontawesome5

**本项目使用的图标**：
- `\faMicrochip` 硬件
- `\faBrain` AI/推荐
- `\faRocket` 部署
- `\faCogs` 引擎
- `\faChartLine` 监控
- `\faCode` API
- `\faServer` 服务
- `\faComments` 聊天
- `\faFileArchive` 文件
- `\faColumns` 后台

### 2.4 字体策略

**Nature 风格无衬线体（最新基准）**：
- 中文 → **Microsoft YaHei**（微软雅黑）—— 现代无衬线
- 英文/数字 → **Arial**（无衬线）—— 与中文协调
- 计算机术语 → **Consolas**（等宽）—— 代码风格高亮
- 数学符号 → 默认跟随文档类

**fontspec 配置**：
```latex
\usepackage{fontspec}
\setmainfont{Times New Roman}[Ligatures=TeX]
\setsansfont{Arial}[Ligatures=TeX]
\setmonofont{Consolas}[Scale=0.92]
% 中文无衬线体（微软雅黑）
\setCJKsansfont{Microsoft YaHei}
\setCJKmainfont{Microsoft YaHei}
```

**图标命令**：
```latex
\newcommand{\icon}[1]{{\footnotesize\color{PaperBorder}#1}}
\newcommand{\code}[1]{{\sffamily\ttfamily\color{AccentOrange}#1}}
```

**编译器**：必须用 **XeLaTeX** 或 **LuaLaTeX**（fontspec 需要）

**与学术衬线体对比**：
| 场景 | 英文字体 | 中文字体 | 代码字体 |
|------|----------|----------|----------|
| Nature 风格（推荐） | Arial | Microsoft YaHei | Consolas |
|  IEEE 学术风格 | Times New Roman | SimSun/宋体 | Courier New |

### 2.5 横平竖直箭头（Orthogonal Routing）

**两种实现方式**：

**方式 1**：用 `|-` 和 `-|` 操作符
```latex
\draw[->] (A) |- (B);   % 先垂直后水平
\draw[->] (A) -| (B);   % 先水平后垂直
\draw[->] (A) -- (B) -| (C) |- (D);  % 混合路径
```

**方式 2**：用 `\coordinate` 辅助点
```latex
\coordinate (M) at ($(A)!0.5!(B)$);
\draw[->] (A) -- (M) -- (B);
```

**项目应用**：本项目架构图每层用大垂直箭头连接，自然横平竖直

### 2.6 顶刊架构图设计原则（2026-07-26 新增）

**参考样本**：
1. 地理空间仿真顶刊（Cellular Automata + PLUS 模型）
2. IROS 2024 HPHS 探索算法框架图
3. IEEE TIV HYDRO-3D 协同感知架构图

**8 条顶刊铁律**：

| # | 原则 | 实现方法 |
|---|------|---------|
| 1 | **层标题左对齐** | 三个层标题在同一条垂直线上，位于虚线框外左上角 |
| 2 | **模块列严格对齐** | 同列模块上下一条线，`text width` 统一 |
| 3 | **箭头完全正交** | 只有水平和垂直线，无斜线。用 `|-` `-|` 或直接垂直连线 |
| 4 | **虚线框留白** | 虚线框比内容宽，左右内边距 12-16pt，呼吸感强 |
| 5 | **层间箭头居中** | 每层之间一个居中大箭头，简洁不杂乱 |
| 6 | **统一尺寸常量** | 用 `\def\ColW` `\def\ColGap` 等宏定义，一处修改全局生效 |
| 7 | **低饱和配色** | 深蓝边框 + 浅灰背景，黑白打印也清晰 |
| 8 | **衬线英文** | 英文/数字用 Times New Roman，技术术语用等宽体 |

**布局算法**：
```
左基线对齐法：
  - 每层第一个模块的左边界对齐
  - 每层内部用 right=<gap> of <prev> 水平排布
  - 下一层用 below=<gap> of <upper_left>.south west, anchor=north west
  - 虚线框用 fit + inner xsep 自动产生左右留白
  - 箭头从 box.south 到 box.north，自动居中垂直
```

### 2.7 最新开源替代方案（已评估）

| 工具 | 类型 | 优势 | 劣势 | 结论 |
|------|------|------|------|------|
| **TikZ** | LaTeX 原生 | 论文级矢量、与 LaTeX 完美集成 | 学习曲线陡 | ✅ 采用 |
| **DrawFig** | 在线 + TikZ 导出 | 可视化拖拽、中文友好 | 收费导出 | 📌 可作为辅助 |
| **tikz-academic-diagrams** | npm 包 | 学术图模板丰富 | 偏 ML 架构 | 📌 参考 |
| **Mermaid** | Markdown 转图 | 流程图友好 | 不支持 LaTeX | ❌ 不采用 |
| **draw.io** | 在线 GUI | 免费、易用 | 不是 LaTeX 原生 | 📌 草稿阶段用 |

---

## 三、项目交付物

### 3.0 文件清单（2026-07-26 整理）

| 类别 | 文件 | 说明 |
|------|------|------|
| **架构图** | `demo-zhipei-arch-paper.tex` / `.pdf` | v12 Nature 风格，三层架构，无衬线字体 |
| **时序图** | `demo-zhipei-sequence.tex` / `.pdf` | v6 紧凑横向顶刊风格 |
| **文档** | `DEVELOPMENT-GUIDE.md` | 开发指南与编码规范 |
| **文档** | `RESEARCH-NOTES.md` | 调研报告与设计原则（本文档） |
| **文档** | `SKILL.md` | Skill 定义文件 |
| **模板** | `templates/flowchart/template.tex` | 流程图模板 |
| **模板** | `templates/layered-arch/template.tex` | 分层架构图模板 |
| **模板** | `templates/org-tree/template.tex` | 组织树图模板 |
| **主题** | `themes/blue.yaml` / `green.yaml` / `orange.yaml` | 配色方案 |
| **主题** | `themes/theme-loader.tex` | 主题加载器 |
| **转换器** | `converter/dsl_to_tikz.py` | YAML DSL → TikZ 转换 |
| **示例** | `examples/example-*.tex` | 4 个示例文件 |
| **测试** | `converter/test_dsl.py` | DSL 转换测试 |

> **已清理的旧文件**：
> - `demo-zhipei-arch-paper-1.png`（旧截图）
> - `demo-zhipei-arch-paper.aux` / `.log`（编译中间文件）
> - `examples/example-*.aux` / `.log`（编译中间文件）
> - 旧版流程图和架构图文件（v1-v3）

### 3.1 架构图（demo-zhipei-arch-paper.tex）

- **v12 Nature 风格**（2026-07-26）：Nature 期刊配色 + 全部无衬线字体 + UI 图标垂直居中
- 三层架构：桌面端 / 后端 / 开源生态
- 10 个统一尺寸模块（三列对齐 + 管理后台跨三列）
- Font Awesome 图标 + Microsoft YaHei + Arial + Consolas
- 8 条顶刊铁律 + 字体规范全部遵循
- 无 Overfull \hbox，文字不溢出卡片

### 3.2 时序图（demo-zhipei-sequence.tex）

- **v6 紧凑横向顶刊风格**（2026-07-26）：在 v5 过度放宽后回退到紧凑比例，保留字体与圆角优化
- 7 个参与方：用户、智配安装器、硬件检测、推荐引擎、部署器、后端、Ollama
- 9 个阶段：启动 → 检测 → 推荐 → 确认 → 请求 → 安装 → 拉取 → WebUI → 完成
- 圆角矩形实例框（rounded corners=5pt）+ 虚线生命线 + 阶段垂直分隔线
- 同步/异步消息区分（实线深蓝 vs 虚线灰蓝）
- 阶段标签为顶部简洁水平小字，去掉冗余圆角徽章
- 图例与术语表集成在图右侧安全区
- 全部英文/数字强制使用 Times New Roman（`\rmfamily\selectfont`），代码术语使用 Courier New
- 核心布局参数：纸张 32cm、参与方间距 0.65cm、阶段间距 2.3cm

### 3.3 时序图设计方法论

**横向时序图 vs 竖向时序图**：

| 维度 | 竖向 | 横向 |
|------|------|------|
| 适合参与方数量 | ≤ 5 | ≥ 6 |
| 适合步骤数量 | ≤ 12 | ≤ 20 |
| 页面利用 | 适合 A4 竖版 | 适合宽屏/自定义宽页 |
| 阅读顺序 | 从上到下 | 从左到右 |
| 顶刊偏好 | 流程短时用 | 多参与方、复杂流程 |

**时序图顶刊铁律**：
1. 实例框用 **大圆角矩形**（rounded corners=5-8pt），内边距充足（inner sep≥4pt）
2. 生命线用 **虚线**，颜色比边框浅，不抢主体
3. 消息标签放在箭头 **上方**（同步）或 **下方**（返回），加白色背景避免被线穿过
4. 同一水平位置尽量只画一条消息，避免重叠；多参与方时优先采用 **横向时间轴**
5. 用垂直分隔虚线标注 **阶段**（Phase），阶段标签水平置于顶部更易读
6. 术语表和图例放在图内或右侧安全区，不占正文空间
7. **字体必须区分**：英文/数字用 Times New Roman（`\rmfamily\selectfont`），代码/技术术语用 Courier New，中文用宋体/黑体
8. **解决拥挤的核心参数**：拥挤时只需微调 10-20%，参与方间距 0.6-0.7cm、阶段间距 2.2-2.5cm、纸张宽度 30-34cm 为宜，避免过度放宽导致空洞

---

## 四、踩坑记录

| 问题 | 解决方案 |
|------|---------|
| TikZ node 中西文未使用 Times New Roman | 在 `font=` 中显式使用 `\rmfamily\selectfont` 强制切换 |
| TikZ `style` 在 node 内部不生效 | 用 `\newcommand` 定义 LaTeX 命令而非 `/.style` |
| 跨 tikzpicture 样式不共享 | 用 `\tikzset{...}` 在 preamble 全局定义 |
| `\faTachometerAlt` 图标不存在 | 改用 `\faTachometer` 或 `\faColumns` |
| `\code{}` 在 pgf-umlsd 内冲突 | 内部用 `\texttt{}` 直接调用 |
| 图整体超宽 Overfull | 用 `\hfuzz=40pt` 抑制小溢出警告 |

---

## 五、参考资料

1. PGF/TikZ 官方手册 — https://tikz.dev/
2. pgf-umlsd 手册 — http://code.google.com/p/pgf-umlsd/
3. fontawesome5 — https://ctan.org/pkg/fontawesome5
4. DrawFig 网络图指南 — https://www.drawfig.com/blog/2026-03-09-network-diagram-guide.html
5. tikz-academic-diagrams — https://www.npmjs.com/package/tikz-academic-diagrams
6. pgf-umlcd — https://github.com/pgf-tikz/pgf-umlcd

---

**调研人**：Trae AI
**项目路径**：`d:\ai\latex\skills\harryopo-tikz-diagram\`
