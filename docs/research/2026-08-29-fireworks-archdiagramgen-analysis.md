# 源码分析：fireworks-tech-graph × archdiagramgen × 自研改良对比

**日期**：2026-08-29
**背景**：用户反馈自研流程图（flowchart-generator / super-diagram）"画得丑"，要求对比原版。
**结论**：改良坏的根本原因 = 从"模板美学"退化到"算法生成"，丢失形状语言/装饰/语义色。

---

## 一、两个原版项目深度分析

### 1. fireworks-tech-graph（yizhiyanhua-ai / 本地 opensource-reference/fireworks-tech-graph）

| 项 | 内容 |
|---|---|
| 定位 | Agent Skill（Codex + Claude Code 通用），自然语言 → 几何质检的 SVG/PNG/GIF/交互 HTML |
| 规模 | 11 个生成器风格 + 1 个 AI 手绘风格（Dark Luxury）；14 种图类型；UML 全支持 |
| 渲染机制 | `fireworks.py render <mode> <input.json> <output.svg>` → `generate-from-template.py`（158KB）Jinja2 填充手工设计模板 |
| 输入 | JSON IR（schema-v1）：nodes / containers / arrows，坐标由 AI 计算 |
| 质检 | `fireworks.py check`：xml / markers / geometry / composition 四层；composition 分 standard（宽松）与 showcase（严格：node_gap≥40 / container_gutter≥20 / segment≥16 / bends≤2） |
| 样式体系 | 12 风格：1 Flat Icon · 2 Dark Terminal · 3 Blueprint · 4 Notion Clean · 5 Glassmorphism · 6 Claude Official · 7 OpenAI Official · 8 Dark Luxury · 9 C4 Review · 10 Cloud Fabric · 11 Event Transit · 12 Ops Pulse |

**节点形状语言（kind，generate-from-template.py 支持 15+）**：
`rect` / `circle` / `double_rect`（双层框=编排器）/ `terminal` / `cylinder`（圆柱=存储）/ `speech`（气泡）/ `document` / `folder` / `hexagon` / `icon_box` / `user_avatar` / `bot` / `circle_cluster`

**箭头语义（flow）**：`read` / `control` / `write` / `feedback` → 自动配色 + 线型 + 图例。

### 2. archdiagramgen（Cocoon-AI / 本地 opensource-reference/archdiagramgen）

| 项 | 内容 |
|---|---|
| 定位 | 暗色主题架构图 HTML skill（自包含 HTML+SVG） |
| 设计系统 | 背景 `#020617` + 40px 网格；组件 rx=6 / 1.5px 描边 / 半透明填充；语义色（frontend cyan-400 / backend emerald-400 / database violet-400 / aws amber-400 / security rose-400 / msg-bus orange-400 / generic slate-400）；JetBrains Mono（12/9/8/7px） |
| 要点 | 箭头画在背景后（z-order）、安全组虚线、区域大虚线 |

> 我们的 super-diagram 暗色主题（`#020617` 背景 + 网格 + JetBrains Mono）即借鉴自它，但细节丢失（rx、虚线组、z-order）。

---

## 二、我们"改良坏"的根因（代码层证据）

对比原版 style5/6 产物与我们 style13/14 产物的 SVG 元素统计：

| 维度 | 原版 | 我们 | 影响 |
|---|---|---|---|
| 形状语言 | speech/double_rect/terminal/cylinder 多种 | 统一圆角矩形 | 视觉单调 |
| 装饰元素 | circle/ellipse 徽章 4-7 个、阴影滤镜 | 0 个 | 缺层次感 |
| 语义色 | flow→箭头颜色/线型 + 图例 | 颜色硬编码 | 信息层级弱 |
| 字号层级 | 30/14/9.5/8.5px 完整层级 | 层级弱 | 标题不醒目 |
| 生成机制 | 手工设计模板 + 数据填充 | 代码算坐标拼 SVG | 设计感丢失 |

**一句话**：原版 = 设计师做模板 + AI 填数据；我们 = AI 算坐标。功能上我们更"智能"（正交路由/避让/质检），但视觉设计体系全部丢失。

---

## 三、方案 A 落地：YAML → 原版引擎（已完成并验证）

### 交付物：`scripts/yaml2ir.py`

把 flowchart-generator 的 YAML（含坐标）转换为原版 JSON IR（schema-v1），直接获得原版 12 风格渲染 + 组合质检。

**转换映射**：
- 节点 → kind 启发式映射（关键词表：coordinator/编排→double_rect，memory/存储→cylinder，terminal/沙箱→terminal，其余→rect）
- 边 → flow 语义（label 关键词 + dashed：tool_call/inference→write，dispatch/task→control，result/feedback→feedback，默认 read）
- 容器 → 每层 groups 生成 container
- 端点匹配：箭头坐标点 → 节点 id（点在内优先，否则最近）；端口按几何对齐推断（避免微段）
- 风格映射：13/14→5（Glassmorphism），15/16→6（Claude Official），17→4（Notion Clean）

**使用**：
```
python scripts/yaml2ir.py input.yaml --style 13 --target-style 5 --render --out-dir output/
python scripts/yaml2ir.py input.yaml --style 13 --target-style 2   # 暗色 Dark Terminal
```

### 验证结果（07-agent-architecture.yaml，49 节点 / 21 箭头）

| 检查项 | 结果 |
|---|---|
| 转换 + 原版渲染 | ✅ 成功 |
| 原版质检 4 项（xml/markers/geometry/composition） | ✅ 全过 |
| 中文（51 个中文节点） | ✅ 无乱码（font 栈 -apple-system/Segoe UI fallback 微软雅黑） |
| 字号层级 | ✅ 30/14/13/12/9.5/8.5 完整 |
| style5（玻璃拟态）/ style2（暗色终端）换肤 | ✅ 同一 YAML 直接换 |

### 中文专属验证（agent-arch-zh.json）

- 原版直接渲染中文 fixture：34 个中文节点无乱码
- showcase 质检通过（需手动保证节点距容器边 ≥20、端口对齐 ≥16px）

---

## 四、使用注意事项（踩坑）

1. **原版质检严格**：showcase 要求 node_gap≥40 / container_gutter≥20 / segment≥16 / bends≤2。自动转换的密集布局建议 `--profile standard`；要 showcase 需放宽间距或手调坐标。
2. **坐标由 AI 提供**：原版不做自动布局（normalize_diagram 只校验）。我们的 YAML 坐标直接复用，sx 侧边栏偏移需折叠（`x+sx`）。
3. **节点间隔**：原版图例/页脚字段可选，标题副标题从 meta 提取（title_en 优先）。
4. **字符串 items**：L1 等组的 `items` 是标签字符串（非矩形），转换时跳过。
5. **时序图（style18）不在转换范围**：原版用 sequence 模式单独处理。

---

## 五、后续可做

- style14（agent 编排）、style16（数据流）、style15（管线）的转换器分支
- 转换器接入 harryopo-office 的 diagram_render（`super-diagram` 块 → 原版渲染）
- 用原版 `motion.py` 生成 SVG→GIF 动效（我们未使用的能力）
- 把原版 12 风格模板反哺 flowchart-generator 的 styles/（若需保留自研渲染）
