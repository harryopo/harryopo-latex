# 通用参赛作品说明书 LaTeX 模板（ distilled framework ）

> **蒸馏自** `知行读书 · 参赛作品说明书.docx`（2026-07-30）
> **蒸馏目标**：把 Word 中"看得见的格式"和"看不见的风格"全部沉淀为可复用的 LaTeX 模板
> **通用化**：支持 AI/软件 / 硬件 / 社会创新 三类参赛项目

---

## 1. 这是什么？

这是一份**可复用的参赛说明书 LaTeX 模板**，蒸馏自你之前在 Word 里手写的版本。

| 项     | 内容                                                                                   |
| ------ | -------------------------------------------------------------------------------------- |
| 文档类 | `harryopo-report.cls`（自带封面 + 摘要 + 目录 + 章节 + 页眉页脚）                    |
| 章节数 | 6 章 + 引言 + 可选章节（项目概述 / 详细介绍 / 附言模块库 / 数据合规 / 使用教程 / 致谢） |
| 字体   | 方正小标宋（标题）/ 方正楷体（页眉）/ 方正书宋（正文）/ XITS（英文）/ XITSMath（数学） |
| 主色   | 深蓝`#1A365D`（标题）、黑 `#1A202C`（正文）                                        |
| 编译   | xelatex 3 遍                                                                           |
| 大小   | PDF 约 6MB                                                                            |
| 页数   | 默认全开约 27 页                                                                       |

---

## 2. 5 分钟上手

```powershell
# 1. 进入蒸馏区
cd d:\ai\latex\蒸馏区

# 2. 编译（自动环境检查 + 3 遍 xelatex）
.\build.ps1

# 3. 看效果
explorer .\competition-statement-template.pdf
```

> 第一次编译会创建 `.aux`/`.toc`/`.out` 等临时文件，**直接删除 `*.pdf` 之外的临时文件**即可。

### 编译报错自查

| 报错                                                        | 原因           | 解决                                              |
| ----------------------------------------------------------- | -------------- | ------------------------------------------------- |
| `fontspec Error: The font "XITS-Regular" cannot be found` | 字体路径错     | 检查`templates/fonts/XITS-Regular.otf` 是否存在 |
| `Missing \begin{document}`                                | ctex 重复加载  | 已在`harryopo-base.sty` 中修复，确认是最新版    |
| `Overfull \hbox`                                          | 文字超出文本宽 | 缩短文字 / 用`\rlap` 缩进 / 启用 `microtype`  |

---

## 3. 改文字（替换占位）

打开 [competition-statement-template.tex](file:///d:/ai/latex/蒸馏区/competition-statement-template.tex)，搜索 `{占位}` 即可定位所有待替换的占位文字。

### 3.1 配置区（文件顶部，先改这里）

```latex
% === 配置区，约第 20-50 行 ===
\newcommand{\projectType}{AISOFTWARE}   % AISOFTWARE / HARDWARE / SOCIAL
\newcommand{\reviewDims}{...}            % 评审维度，按比赛要求修改
\showteamtrue                            % 团队介绍开关
\showexecsummarytrue                     % Executive Summary 开关
\showbibtrue                             % 参考文献开关
\showfaqtrue                             % FAQ 开关
\showappendixtrue                        % 附录开关
\showtoolstrue                           % 工具经验总结开关
\showthoughtstrue                        % 个人想法开关
\showcompetitorstrue                     % 竞品差异开关
\showreviewdetailtrue                    % 评审详细对标开关
\showvaluetrue                           % 应用价值开关
\showfuturetrue                          % 未来规划开关
```

**项目类型说明**：
- `AISOFTWARE` — AI/软件/互联网项目（默认）
- `HARDWARE` — 硬件/嵌入式/机器人项目
- `SOCIAL` — 社会创新/设计/文创项目

### 3.2 封面信息

```latex
% === 作品信息区，约第 88-96 行 ===
\title{知行读书——AI 驱动的阅读成长 Agent}    % ← 改项目名
\subtitle{帮每一位读者构建自我成长型系统}    % ← 改副标题
\author{张三\quad 计算机应用技术专业\quad 2025000101}  % ← 改作者
\institute{示例大学\quad 计算机学院}    % ← 改单位
\date{2026年7月}                            % ← 改日期
\fundproject{参赛项目：XXX}                 % ← 改项目
```

### 3.3 摘要

```latex
% === 摘要自动按 \projectType 切换模板 ===
% 无需手动修改，配置区改 \projectType 即可
\begin{abstract}
% 自动填充对应模板
\end{abstract}
```

### 3.4 关键词

```latex
% === 约第 130-137 行 ===
\keywords{关键词1；关键词2；关键词3；关键词4；关键词5}
```

### 3.5 各章节占位

全文共 **30+ 处 `{占位}`** 标记，按章节分布：

| 章节             | 占位数量 | 主要内容                                       |
| ---------------- | -------- | ---------------------------------------------- |
| 第 1 章 项目概述 | 4        | 一句话定位 / 是什么-解决什么-怎么做 / 评审对标 |
| 第 2 章 详细介绍 | 9        | 痛点对照 / 5 大创新 / 架构图注 / 流水线细节 / 示意图占位 |
| 第 3 章 附言     | 8        | 个人想法 / 与竞品差异 / 评审对标 / 应用价值    |
| 第 4 章 数据合规 | 0        | 无占位（已蒸馏完整）                           |
| 第 5 章 使用教程 | 1        | FAQ 答案（已蒸馏 20 条）                       |
| 第 6 章 致谢     | 1        | 致谢全文                                       |
| 可选章节         | 3        | 团队介绍 / 执行摘要 / 参考文献                 |

**替换方法**：直接覆盖 `{占位}` 文字即可，LaTeX 自动断行，无需手动换行。

---

## 4. 加图片（最重要）

### 4.1 占位原理

模板已经把**所有图片位置都预留好**了。你只需要：

1. 把图片放进 `figures/` 目录
2. **不需要改任何 .tex 代码**——图片会自动出现
3. 重新编译，PDF 同步更新

### 4.2 图片清单

| 文件                | 章节            | 位置     | 原图尺寸   | 模板中的占位   | 你需要做的         |
| ------------------- | --------------- | -------- | ---------- | -------------- | ------------------ |
| `img_000.png`     | 2.4.1 系统架构  | 流程大图 | 3840×3000 | 0.95\textwidth | 替换为你的架构图   |
| `img_001.png`     | 2.4.1 三进程    | 流程小图 | 683×566   | 0.55\textwidth | 替换为三进程示意图 |
| `img_002.png`     | 2.4.2 IPC       | 横长图   | 889×208   | 0.85\textwidth | 替换为 IPC 通道图  |
| `img_003.png`     | 2.5.1 编排      | 流程大图 | 3840×1964 | 0.95\textwidth | 替换为编排流程图   |
| `img_004.png`     | 2.5.1 时序      | 时序图   | 861×1161  | 0.45\textwidth | 替换为时序图       |
| `img_005~008.png` | 3.1 Trae IDE    | 4 张截图 | 2550×1365 | 2×2 网格      | 替换为 IDE 截图    |
| `img_009~011.png` | 3.1 Trae IDE    | 3 张截图 | 2550×1365 | 2+1 网格       | 替换为 IDE 截图    |
| `img_012~013.png` | 3.1 Trae work   | 2 张截图 | 2528×1362 | 1×2 横排      | 替换为 work 截图   |
| `img_014.png`     | 3.1 Trae Design | 1 张截图 | 2556×1369 | 0.48\textwidth | 替换为 Design 截图 |
| `img_100.png`     | 2.2 功能全景    | 演示图   | 自定义     | 0.95\textwidth | 替换为作品演示图   |
| `img_101.png`     | 2.2 功能全景    | 商业模式 | 自定义     | 0.95\textwidth | 替换为商业模式图   |

### 4.3 替换步骤

**方式 A：直接覆盖文件名（推荐）**

```powershell
# 把你自己的图片重命名为约定格式后，复制到 figures/ 覆盖
Copy-Item "我的架构图.png" "d:\ai\latex\蒸馏区\figures\img_000.png" -Force
```

**方式 B：修改 .tex 引用**

打开 `.tex` 文件，把 `\includegraphics{...}` 里的文件名改掉即可：

```latex
% 原占位
\includegraphics[width=0.95\textwidth]{figures/img_000.png}

% 改为你自己的图（建议仍放 figures/ 目录）
\includegraphics[width=0.95\textwidth]{figures/my-architecture.png}
```

### 4.4 图片规格建议

| 维度     | 建议                                            |
| -------- | ----------------------------------------------- |
| 格式     | **PNG**（首选）/ JPG（备选）/ PDF（矢量） |
| 命名     | `img_NNN.png` 格式（与占位一致）              |
| 宽度     | 系统架构图建议 ≥ 3000px，时序图 ≥ 800px       |
| 比例     | 系统架构图 4:3 或 16:9，时序图纵向 3:4          |
| 文件大小 | 单图 ≤ 2MB（避免 PDF 过大）                    |

### 4.5 调整图片大小

如果某张图实际比例和占位不匹配，可以改 `width` 参数：

```latex
% 全宽（适合横长图）
\includegraphics[width=\textwidth]{...}

% 90% 宽（适合 16:9 大图）
\includegraphics[width=0.9\textwidth]{...}

% 半宽（适合 3:4 纵向图）
\includegraphics[width=0.5\textwidth]{...}

% 指定高度
\includegraphics[height=8cm]{...}
```

---

## 5. 改样式（进阶）

### 5.1 主题色

打开 [harryopo-base.sty](file:///d:/ai/latex/蒸馏区/templates/cls/harryopo-base.sty) 第 93-108 行：

```latex
% 当前主题：blue（深蓝主色）
\def\harryopo@settheme@blue{%
    \definecolor{MainColor}{HTML}{1A365D}    % 标题色
    \definecolor{SubColor}{HTML}{2B6CB0}     % 副标题
    \definecolor{AccentColor}{HTML}{C53030}  % 强调色（红）
}
```

改成紫色（参赛获奖配色）：

```latex
% 切换为 dark 主题
\def\harryopo@settheme@dark{%
    \definecolor{MainColor}{HTML}{322659}    % 深紫
    \definecolor{SubColor}{HTML}{553C9A}     % 中紫
    \definecolor{AccentColor}{HTML}{D69E2E}  % 金色
}
```

或在 .tex 文件头部切换：

```latex
\def\harryopo@theme{dark}    % 加载 base.sty 前切换
\documentclass[12pt,a4paper,nomath]{harryopo-report}
```

### 5.2 字体切换

如果不想用方正字体，改用系统字体：

```latex
% 在 .tex 文件头部加：
\setCJKmainfont{SimSun}     % 宋体
\setCJKsansfont{SimHei}     % 黑体
\newCJKfontfamily\fzkt{STKaiti}   % 楷体
```

### 5.3 章节标题字号

打开 `harryopo-base.sty`，搜索 `\titleformat`，调整 `12pt` 等数字。

### 5.4 可选章节裁剪（通用化核心）

模板内置 **11 个开关**，在 `.tex` 文件顶部配置区控制：

```latex
% 项目类型
\newcommand{\projectType}{AISOFTWARE}   % AISOFTWARE / HARDWARE / SOCIAL

% 章节开关（true=显示，false=隐藏）
\showteamtrue        % 团队介绍
\showexecsummarytrue % Executive Summary
\showbibtrue         % 参考文献
\showfaqtrue         % FAQ
\showappendixtrue    % 附录（数据合规/使用教程）
\showtoolstrue       % 工具使用与经验总结
\showthoughtstrue    % 个人想法
\showcompetitorstrue % 与竞品的差异化
\showreviewdetailtrue% 评审标准对标（详细）
\showvaluetrue       % 应用价值
\showfuturetrue      % 未来规划
```

**裁剪示例**：
- 硬件项目：`\showtoolstrue` 改为 `\showtoolsfalse`（去掉 AI 工具经验），`\projectType HARDWARE`
- 社创项目：`\showfuturefalse`（去掉未来规划），`\projectType SOCIAL`

### 5.5 评审维度自定义

```latex
% 在配置区修改评审维度
\newcommand{\reviewDims}{%
    创意性 & 25\% & 设计是否新颖 \\%
    技术难度 & 25\% & 实现复杂度 \\%
    社会价值 & 25\% & 影响力评估 \\%
    可持续性 & 25\% & 长期运营计划 \\%
}
```

---

## 6. 排错工具箱

### 6.1 编译日志

```powershell
# 看最后一次编译日志
notepad .\competition-statement-template.log

# 搜索 fatal 错误
Select-String "Fatal|!|Missing" .\competition-statement-template.log
```

### 6.2 清理临时文件

```powershell
.\build.ps1 -Clean
```

### 6.3 强制重新编译

```powershell
.\build.ps1 -Clean
.\build.ps1
```

### 6.4 看 PDF 页数

```powershell
# 用 SumatraPDF 看（更轻量）
Start-Process "C:\Program Files\SumatraPDF\SumatraPDF.exe" .\competition-statement-template.pdf

# 或直接在 VS Code / Typst 预览
```

---

## 7. 文件结构

```
蒸馏区/
├── README.md                          ← 你正在看的
├── 蒸馏报告.md                         ← 方法论归档
├── build.ps1                          ← 编译脚本
├── competition-statement-template.tex ← 主模板
├── competition-statement-template.pdf ← 编译产物（27页）
├── 知行读书 · 参赛作品说明书.docx     ← 蒸馏源（保留）
│
├── figures/                           ← 图片占位目录
│   ├── img_000.png                    ← 系统架构大图
│   ├── img_001.png                    ← 三进程小图
│   ├── img_002.png                    ← IPC 横长图
│   ├── img_003.png                    ← 编排流程大图
│   ├── img_004.png                    ← 时序图
│   ├── img_005~014.png                ← Trae IDE/work/Design 截图
│   ├── img_100.png                    ← 作品演示图/场景图（通用槽位）
│   └── img_101.png                    ← 商业模式图/画布图（通用槽位）
│
├── templates/                         ← 编译环境（独立打包）
│   ├── cls/
│   │   ├── harryopo-base.sty
│   │   ├── harryopo-paper.cls
│   │   └── harryopo-report.cls
│   └── fonts/                         ← 16 个字体文件
│
├── distill-docx.py                    ← Word 蒸馏工具
└── distill-output/                    ← 蒸馏中间产物
    ├── distill-output.txt             ← 段落级结构 + 样式
    ├── distill-structure.json         ← 图片/表格结构化数据
    └── distill-images/                ← 原图（保留）
```

---

## 8. 下次复用：场景化快速复用

### 场景 1：另一个项目也写参赛说明书

```powershell
# 1. 复制整个蒸馏区
Copy-Item d:\ai\latex\蒸馏区 d:\ai\latex\新项目-蒸馏区 -Recurse

# 2. 改 .tex 顶部作者/标题/项目
# 3. 替换 figures/ 里的图
# 4. 编译
cd d:\ai\latex\新项目-蒸馏区
.\build.ps1
```

### 场景 2：蒸馏另一份 Word 文档

```powershell
# 1. 准备新文档
Copy-Item "D:\其它\我的项目.docx" "d:\ai\latex\蒸馏区2\"

# 2. 改 distill-docx.py 的输入路径
# 3. 运行蒸馏
python distill-docx.py
```

### 场景 3：Word 改完想同步到 LaTeX

1. Word 改完 → 重新跑 `distill-docx.py`
2. 比对 `distill-output.txt` 与当前 `.tex` 差异
3. 手动同步到 `.tex`（LaTeX 编译快于 Word 调格式）

---

## 9. 关键设计决策（WHY）

| 决策                                         | 原因                                                          |
| -------------------------------------------- | ------------------------------------------------------------- |
| 用`harryopo-report.cls` 而不是 `ctexart` | 已有现成模板，统一风格（封面/页眉/脚注/图表）开箱即用         |
| 章节`\chapter` + `\section` 双层         | 蒸馏自原 Word 的"1 章 + 1.x 节"结构，2 级足够，再多级反而累赘 |
| 表格用`tabularx` 而不是 `tabular`        | 自适应列宽，避免长内容溢出                                    |
| 字号`12pt`                                 | 参赛说明书普遍要求，比正文`10.5pt` 略大，更易读             |
| `nomath` 选项                              | 全文无数学公式，禁用 unicode-math 减少包冲突风险              |
| 关键词用`\newcommand` 自定义               | 蒸馏自原 Word 风格："关键词："加粗 + 黑体 + 半角分号分隔      |
| 题目小标题用`\subhead`                     | 蒸馏自 Word 里的"题目小标题"样式（黑体 11pt 加粗）            |
| 图片占位用同名 .png                          | 用户覆盖图片无需改 .tex，降低编译门槛                         |
| 编译从`templates/` 子目录运行              | 让`fonts/ Path=fonts/` 相对路径生效                         |
| 配置区集中管理                             | 项目类型/评审维度/开关集中在文件顶部，不改正文结构            |
| 可选章节用`\newif` 开关                    | 硬件/社创/软件项目可按需裁剪，保持骨架稳定                    |
| 摘要模板按`\projectType` 自动切换          | 3 套摘要模板覆盖 AI/硬件/社创，降低用户思考成本                |
| 评审维度`\reviewDims` 可配置              | 不同比赛评审标准不同，用户可直接替换维度                      |
| 新增示意图/商业模式占位                    | 硬件/社创项目需要展示场景/商业模式，不局限于软件截图          |

---

## 10. 升级路线

- [ ] 蒸馏更多 Word 文档（读书笔记、复习资料、报告模板）
- [ ] 写一个"按 docx 目录自动生成 .tex 章节"的脚本
- [ ] 支持自定义主题色（用户选色 → 自动生成主题）
- [ ] 集成 VS Code 任务（`Ctrl+Shift+B` 直接编译）
- [ ] 蒸馏"代码风格 / 排版习惯"到 `preamble` 片段库

---

**最后**：如果你改了模板觉得好用，记得更新 `蒸馏报告.md` 里的"复用清单"，让下一个人少走弯路。
