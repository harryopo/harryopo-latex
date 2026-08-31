---
name: super-diagram
description: 超级图表生成器 v2.1 — 自然语言 → LLM 手工坐标布局 → 代码箭头路由 → archdiagramgen 暗色主题渲染。支持架构图（nodes+edges）与时序图（participants+messages）两大类型，默认白色系主题、可选暗色。借鉴 archdiagramgen 色板和 fireworks-tech-graph 质量契约。触发词：画图、画架构图、画流程图、生成图表、帮我画、画一个、diagram、architecture、flowchart、时序图、sequence。
---

# super-diagram v2.1

> **LLM 算坐标，代码算路由，质量契约兜底。**

## 核心流程

```
用户自然语言描述
    ↓
① LLM 理解拓扑 → 输出坐标 JSON（architecture: canvas+nodes+edges / sequence: canvas+participants+messages）
    ↓ [布局铁律约束 LLM]
② render_v2.py 代码处理
    ├─ 正交箭头路由 + 自动避障（architecture）
    ├─ 防字体遮盖布局（sequence：标签宽度自适应 + 行高独立 + 时间戳避让）
    ├─ 质量校验（不重叠/不出界/引用完整）
    └─ 双主题渲染（light 默认 / dark）
    ↓
③ 输出 HTML + SVG + PNG
```

## 类型路由

`render_v2.py` 按 `data.type` 自动路由：

| type | 数据形态 | 渲染器 | 用途 |
|------|----------|--------|------|
| `architecture`（或缺省） | `nodes` + `edges` | render_svg | 架构图/流程图/拓扑图 |
| `sequence` | `participants` + `messages` | render_sequence_svg | 时序图（消息交互） |

## 一、architecture 类型（nodes+edges）

## LLM 输出契约

收到用户描述后，**你（LLM）负责理解拓扑并计算坐标**，输出如下 JSON：

```json
{
  "type": "architecture",
  "canvas": {"width": 960, "height": 620, "theme": "light"},
  "title": "微服务架构",
  "subtitle": "一句话描述图的拓扑",
  "nodes": [
    {"id": "gateway", "en": "API Gateway", "zh": "API 网关", "x": 400, "y": 100, "w": 160, "h": 64, "type": "backend"},
    {"id": "user",    "en": "User Service", "zh": "用户服务", "x": 100, "y": 280, "w": 160, "h": 64, "type": "backend"},
    {"id": "db_user", "en": "User DB",      "zh": "用户库",   "x": 100, "y": 440, "w": 160, "h": 56, "type": "db"}
  ],
  "edges": [
    {"from": "gateway", "to": "user", "label": "HTTP"},
    {"from": "user",    "to": "db_user", "label": ""}
  ]
}
```

### 布局铁律（你计算坐标时必须遵守）

1. **网格对齐**：所有 x, y 必须是 **20 的倍数**
2. **层间垂直间距 ≥ 120px**（如网关层 y=100 → 服务层 y=280 → 数据层 y=440）
3. **同层水平间距 ≥ 150px**（节点中心到中心）
4. **画布留边 ≥ 40px**：所有节点必须在 width × height 内，右下侧留至少 40px
5. **体现拓扑语义**：
   - 星型分发：源节点居中，目标节点扇形展开
   - 线性流水：节点从左到右一字排开
   - 分层架构：上层依赖下层，垂直排列
6. **类型分组**：同类型节点对齐同一 y 坐标
7. **节点尺寸**：标准 160×64，数据库可矮些 160×56
8. **边标签空间**：带 `label` 的边，两端节点之间要有容纳标签的间隙——层间 ≥120px、同层 ≥150px 时天然满足。标签**不需要**你精确摆放：引擎会自动把标签落在线上并避让节点/其他标签（`place_edge_label` 兜底）

### 节点类型与颜色（自动映射，你只需填 type）

| type | 描边色 | 语义 |
|------|--------|------|
| `backend` | `#22d3ee` cyan | 后端服务 |
| `db` | `#a78bfa` violet | 数据库/存储 |
| `frontend` | `#34d399` emerald | 前端/用户端 |
| `bus` | `#fbbf24` amber | 消息总线/队列 |
| `security` | `#fb7185` rose | 安全/验证 |
| `external` | `#64748b` slate | 外部系统 |

### 边的属性

```json
{"from": "A", "to": "B", "label": "HTTP", "style": "solid"}
```
- `label`：可选，边的标注文字
- `style`：`solid`（默认）或 `dashed`（虚线，用于反馈/异步）

## 二、sequence 类型（participants+messages）

时序图数据契约：

```json
{
  "type": "sequence",
  "canvas": {"width": 1100, "height": 760, "theme": "light"},
  "title": "LLM Agent 时序图",
  "subtitle": "用户 → 意图识别 → 检索 → 生成 → 输出",
  "participants": [
    {"id": "user", "en": "User", "zh": "用户", "kind": "user"},
    {"id": "gateway", "en": "Gateway", "zh": "API 网关", "kind": "gateway"},
    {"id": "llm", "en": "LLM", "zh": "大模型", "kind": "db"}
  ],
  "messages": [
    {"from": "user", "to": "gateway", "en": "POST /chat", "zh": "发送问题", "time": "0ms"},
    {"from": "llm", "to": "gateway", "en": "LLMOutput", "zh": "生成回复", "async": true, "time": "1.2s"}
  ]
}
```

### participants 字段

- `id`：参与者唯一 ID（消息 from/to 引用它）
- `en` / `zh`：双语名称（两行显示）
- `kind`：参与者类型 → 自动映射 token 色卡

| kind | 亮色填充 | 描边 | 语义 |
|------|----------|------|------|
| `user` | `#fffbeb` | `#d97706` | 用户/终端 |
| `backend` | `#eff6ff` | `#2563eb` | 后端服务 |
| `db` | `#f0fdf4` | `#16a34a` | 数据库/存储 |
| `gateway` | `#f5f3ff` | `#7c3aed` | 网关 |
| `external` | `#fff1f2` | `#e11d48` | 外部系统 |
| `default` | `#f8fafc` | `#475569` | 其他 |

### messages 字段

- `from` / `to`：消息方向（引用参与者 id）
- `en` / `zh`：双语消息文本
- `async`：`true` = 异步返回（灰虚线），缺省 = 同步调用（主色实线）
- `time`：可选，时间戳标签（自动放在消息标签下方空隙，不重叠）

### 时序图防字体遮盖设计（引擎自动处理）

1. **标签宽度自适应**：`max(70, 文本宽+28)`，上限=消息跨度-56 → 长文本不溢出白底框
2. **行高独立**：双行消息 52px / 单行 40px → 相邻标签永不重叠
3. **首行不遮参与者**：`msg_top = header_h + ph + 30`，标签完全落在参与者框下方
4. **时间戳避让**：放消息标签下方空隙（`my + bh/2 + 13`），不与其他文本相撞
5. **标签背景不盖生命线**：只盖自身文本区域，生命线虚线保留

### 时序图布局常量

| 常量 | 值 | 说明 |
|------|-----|------|
| 参与者框 | 132×44 | 居中于生命线 |
| 生命线间距 | 168px | 相邻生命线 |
| 首行消息 | header_h+ph+30 | 不遮参与者框 |
| 双行行高 | 52px | 含中文副标签 |
| 单行行高 | 40px | 仅英文标签 |

## 渲染命令

```bash
python scripts/render_v2.py input.json -o output.svg
python scripts/render_v2.py input.json -o output.png --scale 2        # 高清 PNG
python scripts/render_v2.py input.json -o output.html                 # HTML 预览
python scripts/render_v2.py input.json -o out.png --no-validate       # 跳过质量校验
```

> 主题在 JSON 的 `canvas.theme` 里设置：`"theme": "light"`（默认）/ `"theme": "dark"`。未设置时默认 **light**（白色系）。

## 质量校验（代码自动执行）

render_v2.py 会校验以下规则，**不达标直接拒绝渲染**：

1. ❌ 节点重叠（间距 < 20px）
2. ❌ 节点出界（超出画布 - 40px 边距）
3. ❌ 边引用不存在的节点
4. ❌ 时序图消息引用不存在的参与者（from/to）

## 渲染特性（代码自动处理，你不用管）

- **主题**：时序图支持 light（默认，白底）/ dark（`#020617` 背景 + 语义色板）双主题，由 `canvas.theme` 控制；架构图当前为 light 主题
- **5 色语义色板**：按 type/kind 自动映射描边色和填充色
- **双层 rect 遮罩**：暗色主题下先画 `#0f172a` 底层挡住穿过箭头，再画半透明上层
- **正交箭头路由**：Z 形/L 形自动选择，垂直走廊避障
- **边标签自动避让**：标签框沿最长段中心 ±22px 步进搜索，不盖任何节点（含端点）、不盖其他标签、不超画布；全部位置都撞时选"盖节点面积最小"处兜底（论文图规范：标注落线且不叠压方块）
- **底部图例**：自动统计使用的类型并生成图例

## 工作流程（给 AI Agent 的指令）

1. **询问用户（关键，先确认再画）**：先向用户确认图的内容、类型与风格，给出**文字拓扑描述**（节点清单 + 连接关系 + 每条边的标注），用户确认后再计算坐标：
   - 架构/流程/拓扑 → architecture（nodes+edges）
   - **消息交互/调用链/时序** → sequence（participants+messages）
   - 默认 light（白底论文风）；用户要暗色/大屏/演示用 dark
   - 用户不需要图 → 跳过，不擅自生成
2. 按对应契约计算坐标，输出完整 JSON
3. 调用 `render_v2.py` 渲染（PNG 高清用 `--scale 2`）
4. 如果质量校验失败，根据错误信息**调整坐标/消息引用**后重试
5. **展示确认（关键闭环）**：渲染成功后把 PNG/HTML **展示给用户确认是否满意**；用户满意 → 继续进入文档链路（插入 md → 再生成 word/latex）；不满意 → 按反馈调整拓扑/坐标重新渲染，直到用户满意再继续
6. 默认白色系；用户要暗色/大屏/演示时用 dark

## 与 v1.0 的区别

| 维度 | v1.0 (废弃) | v2.x (当前) |
|------|-------------|-------------|
| 布局决策者 | jieba 分词 + 机械模板 | **LLM（理解拓扑）** |
| 数据格式 | YAML（隐式布局） | **JSON（显式坐标）** |
| 箭头路由 | 硬编码/简单直线 | **正交路由 + 避障** |
| 质量保证 | 无 | **质量契约校验** |
| 渲染引擎 | flowchart-generator | **render_v2.py** |
| 图表类型 | 仅架构图 | **架构图 + 时序图** |
| 主题 | 仅暗色 | **light（默认）+ dark** |
