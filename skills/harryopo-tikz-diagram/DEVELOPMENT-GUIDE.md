# harryopo-tikz-diagram Skill 开发规范

> 本文件定义 Skill 的整体架构、编码规范和接口约定，所有子 agent 必须严格遵守。

---

## 一、项目概述

**Skill 名称**：harryopo-tikz-diagram（harryopo TikZ 画图助手）

**目标**：帮助用户在 LaTeX 中快速绘制专业的流程图、架构图、组织图等，支持多种输入方式（模板/DSL/Mermaid/自然语言）。

**技术栈**：
- LaTeX + TikZ（绘图引擎）
- Python（DSL 转换器）
- Markdown（Skill 文档）

---

## 二、目录结构

```
harryopo-tikz-diagram/
├── SKILL.md                  # Skill 主文件（Agent C 负责）
├── DEVELOPMENT-GUIDE.md      # 本文件，开发规范
├── templates/                # TikZ 模板库（Agent A 负责）
│   ├── layered-arch/         # 分层架构图模板
│   │   ├── template.tex      # 主模板
│   │   └── README.md         # 使用说明
│   ├── flowchart/            # 流程图模板
│   │   ├── template.tex
│   │   └── README.md
│   └── org-tree/             # 组织架构图模板
│       ├── template.tex
│       └── README.md
├── themes/                   # 主题配色系统（Agent D 负责）
│   ├── blue.yaml             # 蓝色主题
│   ├── green.yaml            # 绿色主题
│   ├── orange.yaml           # 橙色主题
│   └── README.md             # 主题使用说明
├── converter/                # DSL 转换器（Agent B 负责）
│   ├── dsl_to_tikz.py        # 主转换器
│   ├── schema.py             # DSL 数据结构定义
│   └── README.md             # 使用说明
├── examples/                 # 示例文件
│   ├── example-layered-arch.tex
│   ├── example-flowchart.tex
│   └── example-org-tree.tex
└── docs/                     # 额外文档
```

---

## 三、TikZ 编码规范

### 3.1 通用约定

1. **编译器**：XeLaTeX，必须支持中文
2. **基础库**：所有模板必须加载以下库
   ```latex
   \usetikzlibrary{positioning, fit, backgrounds, arrows.meta}
   ```
3. **坐标系**：第一个节点用绝对坐标 `at (0,0)`，其余用相对定位 `right=of`、`below=of`
4. **间距单位**：统一用 `pt` 做小间距，`cm` 做大间距
5. **中文支持**：所有示例必须包含中文，验证中文显示正常
6. **字体规范（Nature 风格）**：
   - 中文：Microsoft YaHei（无衬线）
   - 英文：Arial（无衬线）
   - 代码：Consolas（等宽）
   ```latex
   \setmainfont{Times New Roman}[Ligatures=TeX]
   \setsansfont{Arial}[Ligatures=TeX]
   \setmonofont{Consolas}[Scale=0.92]
   \setCJKsansfont{Microsoft YaHei}
   \setCJKmainfont{Microsoft YaHei}
   ```

### 3.2 样式命名规范

所有自定义样式必须遵循以下前缀：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `harryopo-` | 全局通用样式 | `harryopo-module` |
| `arch-` | 架构图专用 | `arch-layerbox` |
| `flow-` | 流程图专用 | `flow-decision` |
| `org-` | 组织图专用 | `org-person` |
| `paper-` | Nature 风格论文图 | `paper-module` |
| `layer-` | 层相关样式 | `layer-box` |
| `arrow-` | 箭头样式 | `arrow-label` |

### 3.3 颜色命名规范

**Nature 风格配色（推荐）**：
```
PaperBorder       - 柔和灰蓝边框（#B0C4DE）
PaperFill         - 纯白模块填充（#FFFFFF）
PaperTitle        - 深蓝灰标题（#2C3E50）
PaperLayerBg      - 层背景：极淡蓝灰（#F5F8FA）
PaperLayerBorder  - 层边框：更浅的灰蓝（#D8E3EE）
PaperMuted        - 次要文字：灰蓝（#5D6D7E）
AccentOrange      - 代码强调：柔和橙（#D35400）
LayerTitleColor   - 层标题色（#2C3E50）
ShadowColor       - 阴影色：极淡蓝灰（#E0E8F0）
```

**通用学术配色（备选）**：
```
MainColor  - 主色（边框、强调）
SubColor   - 次色（次要边框、标题）
SmallColor - 辅助色
TinyColor  - 极浅色（背景填充）
DarkColor  - 文字色
AccentColor - 强调色（警告、重点）
```

### 3.4 模板参数化

每个模板必须可通过以下方式调整：
- 节点数量（最少 2 个，最多 8 个）
- 模块宽度（`text width`）
- 间距（`node distance`）
- 颜色主题（通过 `\def\theme{blue}` 切换）

**Nature 风格推荐参数**：
```latex
\def\ColW{4.5cm}        % 模块宽度
\def\ColGap{0.5cm}      % 模块间距
\def\ModH{1.7cm}        % 模块高度
\def\WideH{0.95cm}      % 宽模块高度
\def\IntraGap{1.5cm}    % 层内模块垂直间距
\def\InterGap{2.0cm}    % 层间垂直间距
\def\LayerPadX{16pt}    % 层左右内边距
\def\LayerPadY{14pt}    % 层上下内边距
```

---

## 四、DSL 转换器规范（Agent B 负责）

### 4.1 输入格式：YAML

```yaml
type: layered-architecture  # 图类型：layered-arch | flowchart | org-tree
title: 图标题               # 可选
theme: blue                 # 主题：blue | green | orange

# 以下根据 type 不同而不同
```

### 4.2 输出格式

输出完整的 `tikzpicture` 环境代码（不含 `\begin{figure}` 等外层）。

### 4.3 函数接口

```python
def generate_tikz(dsl: dict) -> str:
    """
    将 DSL 字典转换为 TikZ 代码字符串
    
    Args:
        dsl: 符合 schema 的字典
        
    Returns:
        TikZ 代码字符串（tikzpicture 环境）
    """
```

### 4.4 必须支持的图类型

1. **layered-architecture**：分层架构图
2. **flowchart**：标准流程图
3. **org-tree**：组织架构树

---

## 五、SKILL.md 规范（Agent C 负责）

### 5.1 结构要求

参考官方 Skill 规范，必须包含：
1. Skill 名称和一句话描述
2. 触发场景（什么时候用这个 Skill）
3. 核心能力列表
4. 使用流程（step-by-step）
5. 模板库使用说明
6. DSL 使用说明
7. 调试技巧和常见问题
8. 最佳实践

### 5.2 写作风格

- 中文，面向学生和初学者
- 多示例，少理论
- 每个示例都有完整可编译的代码
- 踩坑提醒用 `> **注意**：` 标记

---

## 六、主题系统规范（Agent D 负责）

### 6.1 YAML 格式

```yaml
name: blue
display_name: 蓝色主题
description: 专业蓝色系，适合技术文档、学术论文
colors:
  main: "#1A365D"      # 主色
  sub: "#2B6CB0"       # 次色
  small: "#4299E1"     # 辅助色
  tiny: "#EBF8FF"      # 极浅（背景）
  dark: "#1A202C"      # 深色文字
  accent: "#C53030"    # 强调色
```

### 6.2 LaTeX 映射

每个主题对应一套 `\def` 命令：
```latex
\def\MainColor{#1A365D}
\def\SubColor{#2B6CB0}
% ...
```

---

## 七、验证标准

每个模块完成后必须满足：

1. **编译通过**：所有 .tex 示例能用 XeLaTeX 编译通过，无 error
2. **中文正常**：中文文字正确显示，无乱码
3. **无警告**：尽量消除 Overfull/Underfull 警告
4. **代码整洁**：有适当注释，缩进一致

---

## 八、交付物清单

| Agent | 交付物 |
|-------|--------|
| Agent A | 3 套模板（layered-arch/flowchart/org-tree）+ 3 个示例 |
| Agent B | Python 转换器 + 测试用例 |
| Agent C | SKILL.md 主文件 |
| Agent D | 3 套主题配色 + 主题加载器 |

---

*最后更新：2026-07-07*
