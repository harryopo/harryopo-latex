---

## 2026-08-08: flowchart-generator style18 踩坑与优化（已移除 style19 流程图）

### 踩坑1: SVG 路径冗余点（时序图 style18 箭头路径）
- **问题**: 时序图消息路径生成 `L{tx-bend},{my} L{tx-bend},{my}` 两个相同点，浪费且不规范
- **根因**: 参考 lhr-fireworks-tech-graph 的紧凑路由算法，误将"贴边拐弯"误解为多次 bend 点
- **修复**: 直接简写为 `M{fx+10},{my} L{tx-12},{my}`（单向直线路径，无需拐点）
- **教训**: 借鉴开源代码时，要理解算法意图而非照抄具体实现

### 踩坑2: PNG 导出空白（playwright data: URL 渲染）
- **问题**: `page.goto("data:text/html;charset=utf-8,...")` 时，SVG 内容渲染为空
- **根因**: Chromium 对 data: URL 的 SVG 渲染存在兼容性问题，内容无法正确解析
- **修复**: 改为写临时 HTML 文件（`<svg>` 嵌入 `<body>`），再通过 `file://` 协议加载
- **方案**:
  ```python
  html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"></head>
  <body style="margin:0;background:#fff;">{content}</body></html>'''
  tmp_html.write_text(html, encoding="utf-8")
  page.goto(tmp_html.as_uri(), wait_until="networkidle")
  page.screenshot(path=str(png_path), full_page=False)
  tmp_html.unlink(missing_ok=True)
  ```
- **教训**: data: URL 不适合复杂内容渲染，临时文件方案更可靠

### 踩坑3: cairosvg Windows DLL 缺失
- **问题**: `cairosvg.svg2png` 报 `no library called "cairo-2" was found`
- **根因**: Windows 上 cairo 是原生 C 库，pip install cairosvg 不会自动安装 libcairo
- **修复**: 安装 Windows 版 cairo：从 [gnome.org/win32](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer) 下载 GTK runtime，或直接用 playwright 方案
- **替代方案**: 优先用 playwright（`pip install playwright && playwright install chromium`）

### 踩坑4: participants 是列表不是字典
- **问题**: `participants.index(participants[msg["from"]])` 报错
- **根因**: YAML 中 participants 是 list of dict，不是 dict
- **修复**: 用 `pid_map = {p.get("id", p.get("en", p.get("label", ""))): i for i, p in enumerate(participants)}` 建立 ID→index 映射
- **教训**: YAML 数据结构的类型（list vs dict）要在代码中防御性处理

### 踩坑5: marker 引用但未定义（color_map 值错误）
- **问题**: SVG 验证报 `marker 引用但未定义: {'error', 'success'}`
- **根因**: `color_map = {"是": ("as", colors["success"]), ...}` 中，`colors["success"]` 是颜色名字符串，但 marker ID 应该是 `("as", "am")`
- **修复**: `color_map = {"是": ("as", colors["success"]), "否": ("ae", colors["error"])}` 返回 (marker_id, color) 元组，marker ID 从 color_map 第一个元素取值
- **教训**: marker 的 `id` 属性和 fill 颜色是两件事，不能混用

### 踩坑6: colors 字典缺少默认键
- **问题**: `KeyError: 'success'` / `KeyError: 'error'`
- **根因**: YAML 中 `colors` 只定义部分键，覆盖了全局默认值
- **修复**: 先定义完整默认值再合并：
  ```python
  colors = {"bg": "#ffffff", ..., "success": "#059669", "error": "#dc2626", **data.get("colors", {})}
  ```
- **教训**: 默认值合并用 `**data.get(...)` 而非直接赋值，保留所有默认键

### 踩坑7: style13 中 `nodes` 变量未定义
- **问题**: `total_h = header_h + 80 + len(nodes) * node_gap_y + 80` 报 NameError
- **根因**: style13 代码中引用了 `nodes` 变量，但该变量从未定义
- **修复**: 改为从 `layers` 计算，或直接硬编码默认值
- **教训**: 重构/新增 style 时，确保所有变量都有定义

---

### 借鉴 lhr-fireworks-tech-graph 的核心优化
| 技巧 | 实现 |
|------|------|
| 紧凑正交路由 | 从起点贴边拐弯（`fx+10` 到 `tx-12` 直线），非走中点 |
| 2.4px 粗箭头 | `stroke-width="2.4" stroke-linejoin="round"` |
| dominant-baseline="middle" | 文字垂直居中，替代手动 y 偏移 |
| SVG shadow filter | `<feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.07"/>` |
| Token 色系 | start(黄)/process(蓝)/decision(灰)/end(橙)/data(绿)/external(紫) |

---

### 最终产物验证
- ✅ `06-agent-sequence.png` (1000×600, 37KB) — 时序图，6 参与者，9 条消息
- ✅ 路径无冗余点，箭头方向正确，文字居中，颜色区分"是/否"

### 额外发现并修复的预先存在 bug
- **style13 `len(nodes)` 未定义**：应改为 `len(layers)`，一行修复
- **infer_style 误推 style16 为 style15**：04-data-flow.yaml 含 `nodes`/`edges` 但没有 `steps`，导致推断错误；在 style15 检查前插入 `if "nodes" in data and "edges" in data: return 16`

---

### 重要决策：移除 style19 流程图

**原因**：
1. 决策菱形节点"是/否"输出边从菱形底部出来，应该从两侧点出来
2. 分组框位置和内部节点不对齐
3. 整体太散，节点间距计算不精细
4. TikZ 更适合做流程图，flowchart-generator 定位是架构/时序/组织类图

**结论**：flowchart-generator 专注于 style13-18（架构、编排、管线、数据流、泳道、时序图），流程图用 TikZ。
- ✅ **已移除 style19**：流程图做不好，箭头路由有结构性问题，skill 擅长架构/时序图，不适合复杂流程图
