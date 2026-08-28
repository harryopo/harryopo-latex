# 阶段 3：Web 可视化编辑器方案书（2026-08-28）

> **依据**: [2026-08-28-office-super-skill-v2.md](./2026-08-28-office-super-skill-v2.md) 阶段 3（React + TipTap 编辑器 + ProseMirror Doc 中间表示 + Yjs + inline diff）
> **调研来源**: Oleafly wysiwyg 源码深析（opensource-reference/Oleafly）· tiptap-markdown-react 源码（opensource-reference/tiptap-markdown-react，已 clone）· TipTap 官方文档 · 2026 编辑器竞品对比
> **铁律不变**: AI 只产出结构化数据（MD/JSON）→ 模板引擎渲染；编辑器只是"用户可视化编辑 MD 中间态"的入口

---

## 0. 结论摘要（TL;DR）

| 决策项 | 结论 |
|---|---|
| **编辑器内核** | **TipTap 3**（ProseMirror）—— Yjs 原生、`@tiptap/markdown` 开源双向、自定义序列化 API、`@tiptap/extension-mathematics` 官方公式 |
| **MD 双向** | `@tiptap/markdown`（MarkdownManager）+ 自研自定义节点序列化（参照 tiptap-markdown-react CitationRef 范式） |
| **LaTeX/复杂结构兜底** | **RawBlock/RawInline**（借鉴 Oleafly：语义节点只覆盖已知结构，其余原样 `source` 属性保存） |
| **公式** | `@tiptap/extension-mathematics` + KaTeX 渲染（预览近似，最终以引擎渲染为准） |
| **协同/审阅（v2）** | Yjs + y-websocket；diff 用 `@codemirror/merge`（unified/MergeView） |
| **不采用** | `@tiptap-pro` import/export（商业 Start plan）；Milkdown（备选，插件门槛高、文档少） |
| **定位** | 办公文档（Word/MD）可视化编辑面，**与 TexLite（LaTeX 源码编辑）并存**，共享 MD 约定与模板注册表 |

**MVP 范围**（M1）：单用户本地 harryopo-web（Vite + React，localhost:8080），MD 加载/保存、公式/表格/图片可视化、预览、导出复用 office.py。

---

## 1. 背景与目标

### 1.1 痛点
- 当前链路 `AI 产 MD → office.py 渲染` 全程无图形界面，用户无法可视化编辑中间态文档
- Word 模板填充（docxtpl）只能改 data.json，不直观

### 1.2 目标
- 浏览器里**可视化编辑 MD 中间态文档**（符合 harryopo MD 约定）
- 实时预览 + 一键导出 Word / PDF / LaTeX（复用现有渲染引擎）
- v2 加 AI 流式插入 + inline diff 审阅 + 多用户协同

### 1.3 范围边界
- **不做** LaTeX 源码级可视化（那是 TexLite + CodeMirror 的职责）
- **不做** 引擎重写（铁律：编辑器只编辑 MD，渲染永远走 office.py/convert.py/md_to_word）

---

## 2. 调研结论（技术选型）

### 2.1 编辑器内核对比（2026 实测数据）

| 方案 | 内核 | 风格 | 许可证 | bundle | 评价 |
|---|---|---|---|---|---|
| **TipTap 3** ⭐ | ProseMirror | WYSIWYG | MIT（核心） | ~250KB | Yjs 原生、markdown 扩展、公式官方扩展、自定义序列化；**与 Yjs 协同路线天然契合** |
| Milkdown | ProseMirror | WYSIWYG MD | MIT | ~200KB | 插件驱动、中文公式支持好；但单人维护、文档少、改造深 |
| MDXEditor | — | WYSIWYG | MIT | ~250KB | MDX 强，中文/公式生态弱 |
| @uiw/react-md-editor | — | 分栏预览 | MIT | ~180KB | 非 WYSIWYG |
| ByteMD | Svelte | 分栏 | MIT | ~150KB | 非 WYSIWYG，转 React 有隔阂 |

**决策**：TipTap 3。理由：ProseMirror Doc 即"结构化中间表示"（与方案书阶段 3 一致）；`@tiptap/markdown` 开源提供 MD↔JSONContent 双向；自定义扩展 `renderMarkdown/markdownTokenizer` 可完整定制 harryopo 约定；Yjs 协同是 TipTap 一等公民。

### 2.2 关键机制来源（源码实证）

**Oleafly `packages/wysiwyg`（opensource-reference/Oleafly）**—— 最完整参考：
1. **RawBlock/RawInline**（`raw-block.ts`/`raw-inline.ts`）：atom 节点，唯一语义载荷 `attrs.source`；HTML 契约 `div[data-type=raw-block]`/`span[data-type=raw-inline]`；可编辑 textarea（Ctrl+Enter 保存/Escape 取消/IME 防护）—— **"未识别结构原样保真"的正解**，直接呼应项目铁律
2. **math token 占位保护**（`preserve-inline.ts`）：`scanMathExpressions` 扫描 `$...$`/`$$...$$` 区间 → `protectInlineSources` 替换为 token → 解析 → `restoreInlineSources` 还原 —— 防解析器破坏定界符
3. **preamble/body 分离**（`latex/document.ts` `splitLatexDocument`）：preamble 收进可折叠 textarea，正文才可视化 —— harryopo 模板大量 usepackage 场景非常实用
4. **round-trip 幂等测试**（`round-trip.test.ts`）：`serialize(parse(serialize(parse(x)))) === serialize(parse(x))` —— 防二次编辑漂移的护栏
5. **双编辑器共存**：inert + 同挂载（display:none 会破坏 CodeMirror 虚拟化测量）
6. **AI 写操作并发模型**：generation 计数 + 二次校验 + conflict 上报；`isolateHistory` 让 AI 批量编辑不进用户 undo 栈
7. **diff 全套复用 `@codemirror/merge`**（split MergeView / unified unifiedMergeView / 审批卡只读版）

**tiptap-markdown-react（opensource-reference/tiptap-markdown-react）**—— 最小可行参考：
- `@tiptap/markdown` MarkdownManager（双向解析 API）
- `@tiptap/extension-mathematics`（官方公式）+ KaTeX（含 SSR 往返）
- **自定义节点 markdown 往返范式**（`CitationRef.ts`）：`renderMarkdown` + `markdownTokenizer` 把 `[^n]` ↔ 自定义 span —— 正是 harryopo 扩展公式/表格/注释等自定义结构的方法

### 2.3 商业陷阱提示
- `@tiptap-pro/extension-export-markdown`、`@tiptap-pro/extension-import/export`、Conversion REST API 均需 **Start plan + 私有 registry** → **全部不采用**；开源 `@tiptap/markdown` + 自研序列化覆盖同样能力

---

## 3. 架构设计

```
harryopo-web（独立 Vite + React 19 应用，localhost:8080）
│
├── ① 编辑器层（TipTap 3）
│   ├── StarterKit + Markdown（@tiptap/markdown）
│   ├── Mathematics（@tiptap/extension-mathematics + KaTeX）
│   ├── TableKit（GFM 表格）/ Image / 自定义 harryopo 节点
│   └── RawBlock / RawInline（未识别结构兜底，借鉴 Oleafly）
│
├── ② 文档模型（ProseMirror Doc —— 唯一编辑内核）
│   ├── MD 加载：MD → @tiptap/markdown parse → JSONContent（含公式 token 保护）
│   ├── 保存：JSONContent → renderMarkdown → MD（harryopo 约定）
│   └── round-trip 幂等（核心护栏）
│
├── ③ 服务层（调用现有引擎）
│   ├── 渲染导出：office.py render（word / paper / notes / --pdf）
│   ├── 预览：MD → HTML 渲染（markdown-it/KaTeX）或直接调引擎
│   └── 模板注册表：schema → 编辑表单（docx 模板字段引导）
│
└── ④ 协同与审阅（v2）
    ├── Yjs + y-websocket（多用户）
    └── @codemirror/merge（inline diff 审阅 + AI 流式插入审批）
```

**与 TexLite 的关系**（并存不冲突）：

| 维度 | TexLite（已有） | harryopo-web（阶段 3） |
|---|---|---|
| 编辑对象 | LaTeX 源码（CodeMirror） | MD 中间态（TipTap 可视化） |
| 编译预览 | latexmk → PDF | 调 office.py 渲染 Word/PDF |
| 目标用户 | 学术排版 | 办公文档 |
| 共享 | 模板注册表 · MD 约定 · TinyTeX 环境 | 同左 |

---

## 4. 核心机制设计

### 4.1 MD ↔ ProseMirror 双向（harryopo 约定映射）

| MD 约定 | ProseMirror 节点 | 序列化 |
|---|---|---|
| `#` 主标题 | heading level 1（主标题专用） | `# ` |
| `## 一、` | heading level 2 | `## ` |
| `###/####` | heading 3/4 | `###/#### ` |
| `**加粗**` | bold mark | `**` |
| `$$...$$` | mathematics block（extension-mathematics） | `$$...$$` |
| `$...$` | mathematics inline | `$...$` |
| `> 注：` | blockquote | `> ` |
| `> **表N：**` | 自定义 caption 节点 + TableKit | `> **表N：**` |
| `![图N：](path)` | image | `![...](...)` |
| 表格 | TableKit | GFM `\| \|` |
| 未识别结构 | RawBlock/RawInline（source 原样） | 原样回写 |

**加载流程**（借鉴 Oleafly）：
1. 扫描 MD 中 `$...$`/`$$...$$` 区间 → token 占位（防 @tiptap/markdown 破坏）
2. `editor.commands.setContent(protectedMd)`（@tiptap/markdown 解析）
3. 恢复 token → mathematics 节点

**保存流程**：
1. `editor.storage.markdown.getMarkdown()`（MarkdownManager 序列化）
2. 自定义节点 renderMarkdown 注入（公式/表格/注释/图片）
3. 写回 MD 文件 → 触发渲染

### 4.2 RawBlock / RawInline 兜底（核心保真机制）

- 复制 Oleafly `raw-block.ts`/`raw-inline.ts` 模式：`atom: true` + `attrs.source` + 可编辑 textarea
- 场景：用户粘贴 LaTeX 片段、未支持语法 → 原样保存，不丢内容
- 展示：source 推断友好标签（公式→KaTeX 预览、表格→caption 预览等）

### 4.3 公式

- `@tiptap/extension-mathematics`（官方，`$$...$$`/`$...$` 双向）+ KaTeX 渲染
- **预览近似原则**：浏览器 KaTeX 渲染 ≠ Word OMML / LaTeX 最终效果，UI 提示"以导出为准"

### 4.4 导出链路（铁律不变）

```
编辑器 MD → 保存 .md → 调用 office.py render（word/paper/notes）→ Word/PDF/LaTeX
                    ↑ 与现有 CLI/流程完全一致
```

### 4.5 round-trip 幂等测试（核心验证）

```
MD → parse → JSONContent → renderMarkdown → MD'
断言：MD' 与原 MD 语义等价（结构/公式/表格/图片零丢失）
二次编辑漂移检测：serialize(parse(serialize(parse(x)))) === serialize(parse(x))
```

---

## 5. 与现有体系集成

| 集成点 | 方式 |
|---|---|
| **MD 约定** | 复用 SKILL.md 定义的约定（`#`/`##`/`$$`/表格/图片/注释/表标题），编辑器即约定校验器 |
| **渲染导出** | office.py render / md_to_word / convert.py（同 CLI，加 --serve 提供 HTTP 封装） |
| **模板注册表** | docx 模板 schema → 编辑表单（字段提示/枚举/必填校验）；latex 模板 → main.tex 骨架载入 |
| **TexLite** | 并存；MD 项目可一键"在 TexLite 打开"（复用已有 zip import） |
| **图表** | MD 中 super-diagram/mermaid 代码块 → 调 diagram_render 渲染 PNG（复用 office.py 图表预处理） |

---

## 6. 路线图

### M1（MVP，单用户本地）
- [ ] harryopo-web 脚手架（Vite + React 19 + TipTap 3 + @tiptap/markdown + KaTeX）
- [ ] MD 加载/保存双向（harryopo 约定 + 公式 token 保护 + RawBlock/RawInline 兜底）
- [ ] 工具栏（标题/加粗/列表/公式/表格/图片/引用）
- [ ] 预览面板（markdown-it/KaTeX 实时渲染）
- [ ] 导出按钮（调 office.py：Word / PDF / LaTeX）
- [ ] round-trip 幂等测试 + 端到端断言

### M2（集成增强）
- [ ] 模板注册表对接（docx schema → 表单引导）
- [ ] 多文档项目管理（文件树，本地 fs 服务）
- [ ] super-diagram/mermaid 图表渲染集成

### M3（协同 + AI 审阅）
- [ ] Yjs + y-websocket 多用户协同
- [ ] AI 流式插入 + inline diff 审批（@codemirror/merge，借鉴 Oleafly ToolConfirm 交互）
- [ ] 版本历史（git 对接）

---

## 7. 风险与踩坑预案

| 风险 | 预案 |
|---|---|
| **@tiptap/markdown 对 harryopo 约定兼容性** | 自定义节点 renderMarkdown/markdownTokenizer（CitationRef 范式）；round-trip 测试兜底 |
| **中文标点/断行**（浏览器 vs Word 差异） | 预览仅近似；导出以引擎为准；UI 明示 |
| **KaTeX vs OMML/LaTeX 差异** | 公式预览近似原则；不追求像素级一致 |
| **RawBlock 滥用导致编辑碎片化** | 白名单优先结构化；raw 节点仅兜底 |
| **@tiptap/markdown 版本漂移** | 锁定 3.27.x（与 tiptap-markdown-react 对齐） |
| **Yjs 与模板结构冲突** | v2 再评估；先单用户 |
| **商业陷阱** | 禁装 @tiptap-pro；全部用开源扩展 |

---

## 8. 验证方案（低成本确定性检查）

1. **round-trip 幂等**：样例 MD（含公式/表格/图片/注释/表标题）→ parse → serialize → 断言结构保留
2. **端到端**：编辑器产出 MD → office.py render word/paper → 产物断言（沿用既有脚本模式）
3. **约定合规**：编辑器保存的 MD 通过 SKILL.md 约定校验（无残留 `**` 标题等）

---

## 9. 调研源索引

- Oleafly wysiwyg（已 clone）: `opensource-reference/Oleafly/packages/wysiwyg/`（schema.ts / raw-block.ts / raw-inline.ts / preserve-inline.ts / latex/{parse,serialize,document}.ts）+ packages/editor/controller.ts + src/components/editor/{Editor.tsx, wysiwyg/WysiwygEditor.tsx, diff/}
- tiptap-markdown-react（已 clone）: `opensource-reference/tiptap-markdown-react/`（package.json 依赖 3.27.x；src/CitationRef.ts 自定义节点 markdown 往返范式）
- TipTap 文档: tiptap.dev/docs/editor/markdown（@tiptap/markdown + 自定义序列化 renderMarkdown）
- 竞品对比: 2026 React Markdown 编辑器 9 款实测（TipTap/Milkdown/MDXEditor/@uiw/ByteMD）

---

> **方案状态**: 调研完成，技术选型与架构已定。建议下一步——M1 脚手架（Vite + React + TipTap 3 + @tiptap/markdown + KaTeX）跑通 MD 双向 + 公式 + 导出链路。
