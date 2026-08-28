# super-diagram v2.0 方案：推翻 jieba 自动布局，改用 LLM 手工坐标 + 代码路由

> 创建时间：2026-08-09
> 状态：设计完成，待实施
> 前置调研：见本文件附录"调研结论摘要"

---

## 一、问题诊断（v1.0 为什么丑）

v1.0 用 arch-prompter + flowchart-generator，核心问题：

| 环节 | 工具 | 问题 |
|------|------|------|
| 解析自然语言 | arch-prompter 的 jieba 关键词匹配 | **不理解拓扑**，只拆词，不懂"A→B、C、D"是星型分发 |
| 布局算法 | _gen_style13 按 type 分层堆叠 | **机械铺排**，同类节点全塞一行，节点溢出画布 |
| 渲染 | flowchart-generator 的 SVG 模板 | 皮肤再好，骨架烂了也救不回来 |

**根因**：让 jieba 这种"分词器"做"空间布局"任务，抽象层级完全不匹配。

---

## 二、业界调研结论（简版）

详细调研见两份子任务报告，核心结论：

1. **没有任何主流方案让 LLM "裸输出"坐标**，都引入中间层
2. **三种范式**：
   - A: LLM 出 DSL（Mermaid）→ 引擎自动布局（布局不可控，会拉成纵链）
   - B: LLM 手工坐标（draw.io/raw SVG）→ 需要视觉自审门禁
   - C: LLM 出结构化数据 → 模板渲染（我们当前路线）
3. **本地两个参考项目的真相**：
   - archdiagramgen：**LLM 手写硬编码 SVG**，靠 SKILL.md 强规范约束（网格、间距、色板）
   - fireworks-tech-graph：**LLM 写死坐标 + 1500 行代码算箭头路由/避障**
4. **最适合 LLM 的混合方案**：
   - 节点坐标由 LLM 按"网格 + 层间距"规则手算（LLM 擅长语义分组）
   - 箭头路由/避障由代码确定性算法保证（LLM 算路径必交叉）
   - 质量契约拒绝烂图（0 交叉、2 拐上限、40px 间距）

---

## 三、v2.0 架构设计

### 3.1 核心改动：把布局权从 jieba 还给 LLM

```
v1.0: 自然语言 → jieba拆词 → 机械分层铺排 → 烂图
v2.0: 自然语言 → LLM理解拓扑 → LLM输出坐标 → 代码路由箭头 → 质量校验 → 好图
```

### 3.2 新的数据契约（LLM 输出）

LLM 直接输出如下 JSON（不再是 YAML 风格的隐式布局）：

```json
{
  "canvas": {"width": 960, "height": 600, "theme": "dark"},
  "title": "微服务架构",
  "subtitle": "API Gateway 分发到三个独立服务",
  "nodes": [
    {"id": "gateway", "en": "API Gateway", "zh": "API 网关", "x": 410, "y": 120, "w": 140, "h": 60, "type": "backend"},
    {"id": "user",    "en": "User Service", "zh": "用户服务", "x": 120, "y": 280, "w": 140, "h": 60, "type": "backend"},
    {"id": "order",   "en": "Order Service", "zh": "订单服务", "x": 410, "y": 280, "w": 140, "h": 60, "type": "backend"},
    {"id": "payment", "en": "Payment Svc",   "zh": "支付服务", "x": 700, "y": 280, "w": 140, "h": 60, "type": "backend"},
    {"id": "db_user", "en": "User DB",       "zh": "用户库",   "x": 120, "y": 420, "w": 140, "h": 50, "type": "db"},
    {"id": "db_order","en": "Order DB",      "zh": "订单库",   "x": 410, "y": 420, "w": 140, "h": 50, "type": "db"},
    {"id": "db_pay",  "en": "Payment DB",    "zh": "支付库",   "x": 700, "y": 420, "w": 140, "h": 50, "type": "db"}
  ],
  "edges": [
    {"from": "gateway", "to": "user",    "label": ""},
    {"from": "gateway", "to": "order",   "label": ""},
    {"from": "gateway", "to": "payment", "label": ""},
    {"from": "user",    "to": "db_user", "label": ""},
    {"from": "order",   "to": "db_order","label": ""},
    {"from": "payment", "to": "db_pay",  "label": ""}
  ]
}
```

**关键**：坐标是 LLM 算的，体现"星型分发 + 各服务独立数据库"的拓扑语义。

### 3.3 给 LLM 的布局规则（写进 prompt）

借鉴 archdiagramgen + fireworks 的规范：

```
【布局铁律】
1. 网格对齐：所有 x,y 必须是 20 的倍数
2. 层间垂直间距：≥ 120px（如 y=120 的网关层 → y=280 的服务层 → y=420 的数据层）
3. 同层水平间距：节点间 ≥ 150px（中心到中心）
4. 画布边界：所有节点必须在 width × height 内，右侧留 ≥ 40px 边距
5. 中心分支：主干节点居中，分支节点向上下两侧扩散（不要全塞一行）
6. 类型分组：同类型节点（backend/db/frontend）对齐同一 y 坐标

【视觉铁律】（由代码处理，LLM 不用管）
- 5 色语义色板：backend=cyan / db=violet / frontend=emerald / bus=amber / security=rose
- 暗色主题：#020617 背景 + 网格 + JetBrains Mono 字体
- 半透明填充 + 1.5px 描边 + rx=6 圆角

【质量契约】（代码校验，不达标拒绝渲染）
- 节点不重叠（间距 ≥ 20px）
- 节点不出界（在画布内）
- 箭头不穿框（正交路由 + 避障）
```

### 3.4 箭头路由算法（代码实现）

借鉴 fireworks 的简化版（不需要 1500 行，但要核心避障）：

```python
def route_edge(from_node, to_node, all_nodes):
    """正交路由：水平→垂直→水平，绕开其他节点"""
    sx, sy = from_node.right_center()  # 起点：源节点右边中点
    tx, ty = to_node.left_center()     # 终点：目标节点左边中点
    
    # 简单情况：同一行
    if abs(sy - ty) < 10:
        return [(sx, sy), (tx, ty)]
    
    # 一般情况：Z 形路由
    midx = (sx + tx) / 2
    # 检查 midx 是否撞上其他节点，撞上就偏移
    midx = avoid_nodes(midx, sy, ty, all_nodes)
    return [(sx, sy), (midx, sy), (midx, ty), (tx, ty)]
```

### 3.5 质量校验（代码实现）

```python
def validate_diagram(canvas, nodes, edges):
    errors = []
    # 1. 节点不重叠
    for a, b in combinations(nodes, 2):
        if rects_overlap(a, b, padding=20):
            errors.append(f"节点重叠: {a.id} 和 {b.id}")
    # 2. 节点不出界
    for n in nodes:
        if n.x + n.w > canvas.width - 40:
            errors.append(f"节点出界: {n.id}")
    # 3. 网格对齐
    for n in nodes:
        if n.x % 20 != 0 or n.y % 20 != 0:
            errors.append(f"未对齐网格: {n.id}")
    return errors
```

---

## 四、实施计划

### 阶段 1：新建 super-diagram v2 渲染引擎（核心）

**新文件**：`c:\Users\Lenovo\.trae-cn\skills\super-diagram\scripts\render_v2.py`

职责：
- 接收 LLM 输出的 JSON（canvas + nodes + edges）
- 正交箭头路由 + 基础避障
- 渲染 SVG（archdiagramgen 暗色主题）
- 质量校验

### 阶段 2：重写 SKILL.md 的 prompt（让 LLM 输出坐标）

**修改文件**：`c:\Users\Lenovo\.trae-cn\skills\super-diagram\SKILL.md`

核心改动：把"jieba 自动解析"改成"LLM 直接输出 JSON 坐标"，附布局铁律。

### 阶段 3：端到端验证

用三个测试用例验证：
1. 微服务架构（星型分发）
2. 数据管线（线性流水）
3. 智能体编排（多分支 + 反馈环）

每个用例都由 LLM 输出坐标 JSON，render_v2.py 渲染，质量校验通过。

---

## 五、与 v1.0 的关系

| 维度 | v1.0 | v2.0 |
|------|------|------|
| 布局决策者 | jieba + 机械模板 | LLM（理解拓扑） |
| 数据格式 | YAML（隐式布局） | JSON（显式坐标） |
| 箭头路由 | 硬编码/简单直线 | 正交路由 + 避障 |
| 质量保证 | 无 | 质量契约校验 |
| 渲染引擎 | flowchart-generator | render_v2.py（新） |

**保留**：archdiagramgen 暗色主题色板、JetBrains Mono 字体、网格背景（这些皮肤层面的东西 v1.0 已经做对了）

**废弃**：jieba 自动解析、_gen_style13 机械铺排、flowchart-generator 的 style13-18 YAML 数据格式

---

## 附录：调研结论摘要

### 范式对比

| 范式 | 谁布局 | 代表 | 可靠性 | 美感 |
|------|--------|------|--------|------|
| A: LLM 出 DSL | 引擎 | Mermaid | 高 | 中（布局不可控） |
| B: LLM 出坐标 | LLM | draw.io/raw SVG | 低（需自审） | 高 |
| C: 模板渲染 | 模板 | flowchart-generator | 高 | 中 |
| **混合 B+C** | **LLM 坐标 + 代码路由** | **本方案** | **中-高** | **高** |

### 本地参考项目

- archdiagramgen：`d:\ai\latex\opensource-reference\archdiagramgen\` — LLM 手写硬编码 SVG + SKILL.md 强规范
- fireworks-tech-graph：`d:\ai\latex\opensource-reference\fireworks-tech-graph\` — LLM 写死坐标 + 1500 行箭头路由
- 关键文件：
  - `fireworks-tech-graph/references/composition-quality-contract.md`（质量契约）
  - `fireworks-tech-graph/references/svg-layout-best-practices.md`（布局数字规范）
  - `fireworks-tech-graph/scripts/generate-from-template.py` 第 1335-1600 行（路由算法）
