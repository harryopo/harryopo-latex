# 源码分析：cathrynlavery/diagram-design

**日期**：2026-08-29
**源码**：`opensource-reference/diagram-design/`（git clone，130 commits，v2.6）
**项目**：https://github.com/cathrynlavery/diagram-design
**定位**：Editorial diagrams your designer won't hate —— 39 种编辑级图表类型，Claude Code / Codex / Factory Droid / Pi 通用 Agent skill

---

## 一、项目本质

**这是"设计规范驱动型 skill"**，与 fireworks-tech-graph（模板驱动）、flowchart-generator（程序渲染）是三种不同范式：

| 范式 | 代表 | 机制 | 颜值来源 |
|---|---|---|---|
| 模板驱动 | fireworks-tech-graph | 手工设计 SVG 模板 + 数据填充 | 模板本身的设计 |
| 程序渲染 | flowchart-generator / D2 | 代码算坐标拼 SVG | 算法 + 色板 |
| **规范驱动** | **diagram-design** | **AI 按设计系统规范手写 HTML/SVG** | **规范约束 LLM** |

diagram-design 靠一份极其完整的 SKILL.md + 53 个 references 文档约束 LLM 产出。39 类型 × 3 变体（minimal light / minimal dark / full editorial）共 117+ 个成品 HTML 示例在 `assets/`。

## 二、设计系统核心（为什么好看）

### 1. 哲学
- **"The highest-quality move is usually deletion"**——删减优先，每节点必须有独立意义
- 强调色（accent）只给 1-2 个焦点；密度 4/10；9 节点以上拆图
- **"No shadows. No Mermaid slop."**——无阴影、不复制 Mermaid 渲染器布局

### 2. 语义 token（style-guide.md，单一起源）
- `paper`/`ink`/`muted`/`soft`/`rule`/`accent`/`accent-tint`/`link`，亮暗双值 + 翻转规则
- 默认皮肤 = 冷编辑色板：白纸 `#f5f5f5` + 墨黑 `#2d3142` + 原子橙焦点 `#eb6c36` + 蓝灰 `#4f5d75`
- 终端皮肤（可选）：纯黑底 `#0a0a0a` + 单焦点色 —— **与用户要的黑白灰完全同构**

### 3. 字体规则（明确反对 JetBrains Mono）
- 标题：Instrument Serif（衬线）；节点名：Geist（无衬线 12px/600）；技术标注：Geist Mono（端口/URL/字段类型）
- **Mono 只用于技术内容**，绝不当全局字体；中文 fallback 微软雅黑

### 4. 4px 网格（强制）
- 所有字号/坐标/尺寸/间距必须被 4 整除（字号 8/12/16/20...，节点宽 80/96/112...，间距 20/24/32/40/48）

### 5. 6 条连接器硬规则（§6，违反即失败）
1. 正交圆角连接器 r=8（禁止斜线）
2. 标签距线 6-10px（遮罩不贴线）
3. 连接器不重叠（交叉用 bridge/hop）
4. 同边多连接 fan out ≥12px
5. 连接器不穿非端点盒子（不可避免时虚线 + 标签在可见端）
6. 标签遮罩不压后续节点

### 6. 复杂预算（§7）
每类型限节点数（架构 ≤9 节点/12 箭头，时序 ≤5 lifeline，泳道 ≤5 lanes...），超出拆图

### 7. 无障碍契约 + 自检
- `<svg role="img" aria-labelledby>`，title 第一个子元素，slug 前缀 ID
- `scripts/self_check.py`（无第三方依赖）验证生成物

## 三、导入能力
- `scripts/mermaid_extract.py`：Mermaid（flowchart/sequence/state/er）→ IR，**extract 不 render**，保留内容丢弃渲染器布局
- `scripts/drawio_extract.py`：draw.io → IR
- 4 个输出旋钮：format（html/svg/png）× size（doc-inline/slide-16x9/social-og...）× detail（faithful≤24/balanced≤12/simplified≤7）× audience

## 四、中文适配验证（实测）
- 按规范手写「多智能体编排平台」中文架构图（`output/diagram-compare/dd-zh-agent.html`）
- 中文标题/节点/图例无乱码（字体栈补 `'Microsoft YaHei'` fallback）
- `self_check.py` 通过

## 五、与现有方案对比结论

| 维度 | diagram-design | 我们（flowchart-generator mono） | 原版 fireworks style5 |
|---|---|---|---|
| 美学范式 | 编辑级极简（白纸黑字+焦点） | 算法生成（黑白灰） | 模板玻璃拟态 |
| 类型覆盖 | **39 种** | 6 种（13-18） | 12 种 |
| 中文 | ✅ 实测通过 | ✅ | ✅ |
| 生成方式 | LLM 手写（规范约束） | 程序渲染 | 模板填充 |
| 接入成本 | 装 skill 即用（AI 生成） | 已有 | 需 yaml2ir 转换 |
| 质量门禁 | self_check + 6 连接器规则 | validate_layout | 4 项质检 |

## 六、落地建议

1. **作为 AI 生成 skill 直接使用**：复制 `skills/diagram-design/` 到 `~/.trae-cn/skills/` 或项目 `.trae/skills/`，AI 生成图时调用（39 类型覆盖 agent 架构图）
2. **与 office.py 集成**：MD 里 `diagram-design` 代码块 → AI 按规范生成 HTML → html2png 转 PNG（复用 playwright）
3. **借鉴规范改进自研**：把 4px 网格、6 连接器规则、焦点色规则、密度预算引入 flowchart-generator（补质检缺口）
4. **中文皮肤**：预置一份中文 fallback 的 style-guide 变体（字体栈加雅黑）

## 七、注意事项
- 依赖 Google Fonts（内网需改本地字体或接受 fallback）
- 生成质量依赖 LLM 遵循规范的程度（规范详尽但长，需完整加载）
- 默认 density 4/10 与用户"复杂架构图"场景需权衡（>9 节点会强制拆图）
