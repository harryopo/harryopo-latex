# 我们的图表 skill 与 archify 的系统性差距诊断

> 诊断日期：2026-08-14
> 对照对象：`flowchart-generator/scripts/gen.py`（2167 行）、`super-diagram/scripts/render_v2.py` vs `archify/`（v2.14）
> 诊断态度：诚实指出我们的问题，同时不盲目吹捧 archify——它也有代价

---

## 一、一句话诊断

**我们的核心问题不是某个算法差，而是架构层面"先有样式后有抽象"**——每个 style 都是独立孤岛，导致质量校验、路由、文本适配这些应该共享的能力全部各自为政或干脆缺失。archify 是"先定义 5 类图的统一 IR，再为每类写渲染器"，共享层（geometry/text-fit/validator/utils）一次实现五处复用。

**用户感觉"我们有很多问题"是准确的**——但根因比想象中更深一层。

---

## 二、具体差距（按严重程度排序）

### 🔴 P0-1：质量校验近乎为零（最严重）

| 维度 | archify | flowchart-generator | super-diagram |
|---|---|---|---|
| 校验函数数量 | 8+ 类纯函数 | **1 个**（`validate_svg` 仅查 XML 合法） | **3 项**（重叠/出界/引用） |
| 边穿节点检测 | `clean-flow/edge-through-node` **硬失败** | ❌ 无 | 有 `_line_blocked` 但 validate 没调用 |
| 标签遮盖检测 | `composition/label-route-clearance` | ❌ 无 | ❌ 无 |
| 字号溢出检测 | `minimumNodeTextWidth` 拒绝 | ❌ 无 | ❌ 无 |
| 错误信息形态 | 错误码 + subject + evidence + supportedFixes | `❌ 渲染失败: {e}` 一行字符串 | `节点重叠: a ↔ b`（无证据无修复建议） |
| 质量分级 | `quality_profile: standard\|showcase` | ❌ 无 | ❌ 无 |

**代码证据**：
- gen.py:1628 `validate_svg` 只做 4 件事：XML 解析、标签平衡、marker 引用、viewBox/xmlns 检查。**全是语法层，零语义层**。
- render_v2.py:62 `validate` 只检查重叠/出界/引用，**边穿节点这个最关键的硬失败完全没校验**——尽管 `_line_blocked` 函数已经写好了（112 行），却没在 validate 里调。

**用户反复反馈的"卡片大文字空""字体遮盖"本质就是这个闭环缺失**——问题发生时检测不到，LLM 拿不到可操作的修复建议，只能肉眼调试。

### 🔴 P0-2：箭头共享端点全部堆叠

| archify | 我们 |
|---|---|
| `automaticPortSpread`：按对端坐标排序、对称分布、`spacing=min(14, (边长-2×16gutter)/(n-1))`、16px 角留白 | flowchart-generator：style13 的 arrows 直接 `M{x1},{y1} L{x2},{y2}` 两点直线，**多条共端点全部重叠** |
| `automaticPortRhythmBridge`：近平行端口用 24px stub + 16px 外部通道桥 | style14 有简陋扇出（固定 12px 间距），但无角留白、无对端排序 |
| `routeHonorsEndpointSides`：侧是方向契约，首尾段垂直进出 | style15/16 固定右出左入 dogleg，不避让中间节点 |

**super-diagram 的 `route_edge`（render_v2.py:311）已经接近 archify 的思路**：16 种出口组合 + 走廊偏移候选 + 全段碰撞校验 + 按段数排序。但它**没有端点侧契约、没有回头线消除、没有自动端口扇出**——多对端点共用一个组件时还是会堆在同一点。

### 🟡 P1-3：文本宽度估算粗糙，渲染时不缩字号

| archify | 我们 |
|---|---|
| `fittedNodeFontSize(text, width, preferred, minimum)`：渲染时按 `(width-8)/(textUnits×0.6)` **动态缩小字号**到 [preferred, minimum] 之间 | gen.py 字号写死在 CSS class 里（`.en=15px`/`.zh=13px`/`.item=12.5px`），**渲染时不变** |
| `minimumNodeTextWidth`：缩到最小仍放不下才报错 | ❌ 无下限校验 |
| `textUnits`：CJK/emoji 按 2 单位（统一正则），全渲染器共享 | `_text_w` 在 gen.py 一份、render_v2 又一份估算，**各自为政** |

**这就是"卡片大文字空"的另一半根因**——我们用 `_text_w` 反推盒子尺寸，一旦估算偏差或 YAML 给了显式小尺寸，字号却不会跟着缩小，文字就溢出或留白。archify 反过来：**盒子尺寸固定，字号自适应缩小**，更稳健。

### 🟡 P1-4：没有统一的中间表示（IR）

archify 五类图有明确 schema（`schemas/*.schema.json`）：
```
architecture: components[{id,type,label,pos[2],size[2],sublabel,tag}] + connections[{from,to,variant,fromSide,toSide,via,label}] + boundaries[{wraps,label,kind}]
sequence:     participants[{id,en,sublabel,kind}] + messages[{from,to,y,label,variant}] + segments + activations
```

我们的字段结构每个 style 都不同：
```
style13: layers[{id,y,groups[{en,items,sub_items}]}] + arrows[{from[2],to[2],label}]
style14: main_flow[{x,y,w,h,en,zh,items}] + intents + sources + tools
style15: steps[{type,en,zh,items}] + arrows
style16: nodes[{id,type,x,y,en,zh,items}] + edges[{from,to,label}]
style17: lanes + stages + tasks
```

**后果**：
- 每加一个 style 要从头写一遍渲染 + 路由 + 校验（因为数据结构不一样）
- 共享层（geometry/text-fit/validator）无法复用
- 字段拼错不报错（没有 schema），`data.get("xxx")` 静默用默认值

### 🟢 P2-5：渲染函数 monolith，布局/路由/渲染没分离

archify 的 `render-architecture.mjs` 明确分四阶段：
- `measureComponent`（测量：pos+size→{x,y,w,h,cx,cy}）
- `validateArchitecture`（校验：problems[]）
- `pathFor`/`routeVia`（路由：多候选+过滤）
- `renderComponent`/`renderBoundary`（渲染：只画）

我们的 `build_style13_svg`（gen.py:368-614，**247 行一个函数**）把虚线框计算、组高统一、卡片渲染、文字定位、箭头全揉在一起。改一处怕动全身。

### 🟢 P2-6：没有原子交付和质量收据

archify 的 `deliver`：读 spec → 写私密快照 → 渲染 → 跑检查 → **全过才原子替换** → SHA-256 收据。失败保留旧版。

我们直接 `write_text`，失败不回滚。对 LLM 自愈场景，没有"冻结的候选 + 收据"意味着每次重渲染都可能引入新问题而无法追踪。

---

## 三、我们已经做对的地方（不妄自菲薄）

客观讲，我们的 skill 不是全盘皆输：

1. **super-diagram 的 `route_edge` 已经是正交路由的正确范式**——16 种出口组合 + 走廊偏移候选 + 全段碰撞校验 + 段数排序。这比 flowchart-generator 进步一大截，思路和 archify `routeVia` 同源，只差端点侧契约和回头线消除。

2. **v0.4.0 回归显式坐标的决策对了**——和 archify "布局判断靠 agent" 的哲学一致。估算兜底分支确实存在，但显式优先已经让我们避开了"自动布局"这个最难的坑。

3. **D 盘产物重定向 `_OUT_ROOT`** 解决了 C 盘膨胀——这是工程素养，archify 没这个考虑（它在 skill 包内写作产物）。

4. **暗色主题 + 网格背景 + 语义色板**的视觉方向正确，和 archify 的 classic 预设体感接近。

5. **CJK 文本估算** `o > 0x2E80` 判定也基本对齐 archify 的 textUnits 思路（虽然没它覆盖全）。

---

## 四、archify 的代价（不盲目照搬）

诚实讲，archify 的设计也有它的问题：

1. **它的校验体系是为"LLM 写 JSON → CLI 渲染"的线性流程设计的**——假设 LLM 会根据单据自愈迭代。我们 flowchart-generator 是"YAML → 独立 .py 脚本"的产物形态，校验闭环要改造适配。

2. **它的 schema 用 ajv（JSON Schema）**——我们用 YAML，要么转 JSON Schema，要么用 pydantic，都是引入新依赖。

3. **它的 5 类图边界很硬**——必须先选 type。我们的 style 13-18 启发式推断（infer_style）反而更灵活，适合"用户描述模糊"的场景。

4. **它的端口扇出假设组件是矩形且侧边是直线**——我们的 style13 有"组里套子卡再套小卡"的三层嵌套结构，端口扇出要适配的边界比 archify 复杂。

5. **它的 `fittedNodeFontSize` 只处理单行不换行**——我们的卡片有多行 items，要扩展成多行适配。

---

## 五、升级路线建议（务实分级）

### 第一阶段：补齐校验闭环（P0，根治"反复反馈的问题"）

**新增 `geometry.py` 共享模块**（放在 `flowchart-generator/scripts/` 或抽到 `shared/`），实现纯函数：

```python
def rects_overlap(a, b, gap=0) -> bool
def segment_intersects_rect(seg, rect, clearance=0) -> bool
def clean_flow_problems(edges, nodes, ...) -> list[Problem]   # 边穿节点（硬失败）
def clean_overlap_problems(nodes, gap=8) -> list[Problem]     # 节点重叠
def clean_label_obstruction(labels, nodes, ...) -> list[Problem]  # 标签遮盖
def text_units(text) -> int                                   # 统一 CJK 测量
def fitted_font_size(text, width, preferred, minimum) -> float  # 渲染时缩字号
def minimum_text_width(text, minimum) -> float                # 下限校验
```

**Problem 数据类**（关键）：
```python
@dataclass
class Problem:
    code: str           # "clean-flow/edge-through-node"
    severity: str       # "error" | "warning"
    message: str        # 含数字阈值 + 修复动词
    subject: dict       # {diagram_type, path, identity}
    evidence: dict      # 具体测量数据
    supported_fixes: list[str]  # 只允许的修复手段
```

**给 flowchart-generator 每个 style 增加 `validate_layout()`**，在 `cmd_generate` 里渲染后自动调用，失败非零退出并打印 problems。

**给 super-diagram 的 `validate` 补齐边穿节点检测**——`_line_blocked` 已经写好，只需在 validate 里对所有 edges 调用一遍。

### 第二阶段：自动端口扇出（P0，解决箭头堆叠）

移植 archify 的 `automaticPortSpread` 算法（约 50 行 Python）：
- 按 `(组件id, 侧)` 分组共享端点的关系
- 按对端中心坐标排序（确定性）
- `spacing = min(14, (边长-2×16gutter)/(n-1))`
- 对称分布 + 16px 角留白

先在 super-diagram 的 `route_edge` 里加（因为它已经有候选机制），再考虑 flowchart-generator。

### 第三阶段：渲染时缩字号（P1，根治"卡片大文字空"）

实现 `fitted_font_size`，在渲染每个 `<text>` 时按盒宽动态算字号：
```python
font_size = max(minimum, min(preferred, (width - 8) / (text_units(text) * 0.6)))
```
替换掉 gen.py 里写死的 `.en=15px / .zh=13px / .item=12.5px`。这一改直接消除"盒子大字号小"和"盒子小字号溢出"两个极端。

### 第四阶段：统一 IR（P1，长期架构重构）

引入 `Node`/`Edge`/`Group` dataclass，让 style 13-18 都映射到统一结构。这是大工程，建议在新加 style 时逐步迁移，不一次性重写。

### 不建议做的

- ❌ 引入 ajv/JSON Schema（我们用 YAML，pydantic 更自然，但短期没必要）
- ❌ 照搬 archify 的 deliver 原子交付（我们的产物是 .py 脚本，不是 HTML，收据价值有限）
- ❌ 照搬 visual-check（CLAUDE.md 硬约束已明确反对截图目检，archify 自己也承认 `visualReview: "pending"`）

---

## 六、结论

**我们的问题是真的，但不是"算法不如人"——是"架构层面欠债"**。具体讲：

1. flowchart-generator 是"借鉴 12 风格"起步的 bottom-up 产物，每个 style 独立孤岛，共享层欠债；
2. super-diagram 是"统一入口"的 top-down 产物，路由已经接近 archify 水平，但校验和文本适配仍欠；
3. archify 的核心可借鉴点是**"校验闭环 + 维修单据"**——不是某个具体算法，而是让 LLM 能自愈的工程哲学。

**务实升级顺序**：先补校验闭环（P0-1）→ 再补端口扇出（P0-2）→ 再做缩字号（P1-3）→ 最后考虑统一 IR（P1-4）。前三项能在现有架构上增量改进，不需要重写。

最大的教训：**质量校验不是"做完功能再加"的锦上添花，而是从一开始就该有的承重墙**。archify 把它放在共享层，所有渲染器共用，一次实现五处受益——这是我们现在最该补的债。
