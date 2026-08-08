# 办公超级 Skill 架构方案

> **日期**: 2026-08-08
> **目标**: 解决"AI 做的 Word/PDF/PPT 丑死了、不按模板来"的根本痛点，构建模板驱动、可视化可编辑的办公文档生成体系。
> **调研依据**: [AI 文档生成调研](../research/2026-08-08-ai-office-generation.md) · [模板引擎调研](../research/2026-08-08-template-engines.md) · [可视化编辑调研](../research/2026-08-08-visual-editing.md)

---

## 0. 一句话总结

**核心范式转变：把 AI 从"直接产出文档"改为"产出结构化数据（JSON/Markdown），再由模板引擎渲染成文档"。**

这才是解决"AI 输出丑"的根本方案。当前所有"丑"的根源，都是让 LLM 直接操作 OOXML/排版代码——而 LLM 运行在文本语义层，文档是排版结构层，两者抽象层级不匹配。

---

## 1. 四大核心需求 → 技术对策

| # | 你的需求 | 技术对策 | 对应调研结论 |
|---|---------|---------|------------|
| 1 | AI 输出按模板来，不再丑 | **模板引擎驱动**：用户提供 .docx/.tex/.html 模板 → AI 只产出符合模板 schema 的结构化数据 → 引擎渲染保真 | 模板引擎调研 §0、§7 |
| 2 | Word ↔ Markdown ↔ LaTeX 互转 | **Pandoc 为中枢** + harryopo LaTeX 模板体系 + 结构化中间表示 | AI 生成调研 §5 |
| 3 | 办公文件可视化、途中可编辑 | **TipTap + Yjs + diff 审阅** 的前端编辑器，结构化中间表示作为编辑内核 | 可视化调研 §1、§6 |
| 4 | 提供几个喜欢的模板，以后按模板输出 | **模板注册表 + 自动 schema 提取**：模板入库时自动分析占位符，生成 schema 约束 AI 输出 | 模板引擎调研 §8 |

---

## 2. 目标架构总览（三层闭环）

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户层                                   │
│   自然语言需求  +  用户提供的模板（Word/LaTeX/HTML）              │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ① 生成层（AI）                              │
│   LLM 产出结构化数据（JSON/YAML/Markdown）                       │
│   受模板 schema 约束（function calling / structured output）     │
│   绝不直接生成 OOXML / 排版代码                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ② 编辑层（可视化）                          │
│   浏览器前端：TipTap/ProseMirror 编辑器 + Yjs 协作                │
│   AI 修改以 inline diff 呈现 → 用户接受/拒绝                     │
│   结构化中间表示（ProseMirror Doc）作为编辑内核                   │
│   实时预览：docx-preview / pdf.js / LaTeX WASM                   │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ③ 输出层（渲染）                            │
│   Word:  docxtpl / docxtemplater / Pandoc reference-doc          │
│   PDF:   XeLaTeX + harryopo 模板 / WeasyPrint / Typst            │
│   PPT:   Marp / Slidev / Presenton                               │
│   全部从模板渲染，保证"不丑"                                      │
└─────────────────────────────────────────────────────────────────┘
```

**核心原则**：三层职责严格分离。AI 只管内容，模板只管设计，引擎只管渲染。

---

## 3. 按格式推荐的技术路线

### 3.1 Word / docx（你最关心的）

| 方案 | 模板形态 | AI 职责 | 推荐场景 |
|------|---------|--------|---------|
| **docxtpl (Python)** ⭐首选 | .docx 文件本身（Jinja2 标签 `{{}}`） | 产出符合 schema 的 JSON | Python 生态、与现有 harryopo 契合 |
| **docxtemplater (JS)** | .docx 文件（`{tag}` 占位符） | 产出 JSON | JS/Node 全栈 |
| **Pandoc --reference-doc** | 一个样式参考 .docx | 产出 Markdown | 从 Markdown 一键转品牌化 Word |
| **poi-tl (Java)** | .docx 文件（`{{tag}}`） | 产出 JSON | Java 企业环境 |

**最佳路线（Python 生态）**：
```
用户提供 品牌模板.docx（含 {{title}}、{% for item in items %} 等占位符）
    ↓
Skill 自动分析模板 → 提取 schema（哪些占位符、什么类型）
    ↓
AI 按 schema 产出 JSON 数据
    ↓
docxtpl 渲染 → 品牌化.docx（完美保留模板样式）
```

### 3.2 PDF（学术/排版型）

| 方案 | 模板形态 | 适用 |
|------|---------|------|
| **LaTeX + Jinja2** ⭐ | .tex 模板 + Jinja2 占位符 | 论文、报告、书籍（harryopo 已就绪） |
| **Pandoc + LaTeX template** | Pandoc template + reference-doc | Markdown 一键转高质量 PDF |
| **Typst** | .typ 模板 | 编译极快，未来备选 |
| **WeasyPrint + CSS** | HTML/CSS 模板 | 设计型 PDF、报表、发票 |

**最佳路线（本项目）**：
```
用户提供 harryopo LaTeX 模板（.cls/.sty 已完成）
    ↓
AI 产出结构化内容（Markdown 或 JSON）
    ↓
Pandoc / Jinja2 填充 → XeLaTeX 编译 → 高质量 PDF
```

### 3.3 PPT / 演示文稿

| 方案 | 模板形态 | 亮点 |
|------|---------|------|
| **Presenton** ⭐ | HTML + Tailwind 主题 | Gamma 最佳开源替代，API 可调用 |
| **Marp** | Markdown + CSS 主题 | 最简洁，已有成熟 Skill 生态 |
| **Slidev** | Markdown + Vue 组件 | 最灵活，开发者友好 |
| **PPTAgent** | 参考真实 PPT 结构 | 中科院方案，分析参考 PPT 再生成 |

**最佳路线**：Marp（技术内容）或 Presenton（设计型演示）。

---

## 4. 可视化 + 可编辑架构（你的最大想法）

### 4.1 推荐技术栈

| 层 | 组件 | 作用 |
|----|------|------|
| 前端框架 | React 19 / Next.js 15 | 生态最大，编辑器组件支持最好 |
| **编辑器内核** | **TipTap (ProseMirror)** | 50+ 扩展、docx 导入导出、协作成熟 |
| 协作/AI 同步 | **Yjs + Hocuspocus** | CRDT 黄金标准，AI 流式插入 |
| **AI 编辑 UX** | **inline diff（Cursor 风格）+ 接受/拒绝** | 颗粒度可控，人保留最终决定权 |
| docx 预览 | docx-preview（高保真）| 展示"将导出的样子" |
| LaTeX 实时预览 | WasmTex（嵌入式）/ Overleaf CE（完整）| 边写边看 |
| PDF 标注 | pdf.js + react-pdf-highlighter-plus | 开源、React 友好 |
| 最终输出 | docxtpl / XeLaTeX / Pandoc | 模板化渲染 |

### 4.2 关键设计原则

1. **结构化中间表示作为编辑内核** —— 编辑器操作的是 ProseMirror Doc（结构化），不是扁平文本。这是可靠编辑的基石，防止"AI 失控重写整篇"。
2. **AI 生成完整文档 + 系统自己 diff** —— 让 LLM 输出完整的目标内容，编辑器自己算 diff，呈现给用户接受/拒绝。比让 AI 输出"操作序列"可靠得多。
3. **inline diff + 建议模式混合** —— 大段重写用 diff，局部润色用建议模式，避免全文重生成丢失已认可部分。
4. **版本审计（差异化机会）** —— 没有现有工具在内容接受后保留 AI 来源标记。带"手动/AI/快捷编辑"徽章的版本历史是蓝海。

### 4.3 三种产品形态（按投入从低到高）

| 形态 | 描述 | 适合阶段 |
|------|------|---------|
| **A. 本地 Skill + 预览** | Skill 生成文件 → 本地服务器渲染预览 → 用户在编辑器（VS Code/Web）改源文件 → 重新生成 | MVP，最快验证 |
| **B. Web 编辑器** | 独立 Web 应用：TipTap 编辑器 + 实时预览 + diff 审阅 + 一键导出 | 完整产品 |
| **C. 嵌入式 ONLYOFFICE** | 用 ONLYOFFICE CE 做 docx 的 OOXML 原生编辑，Skill 负责生成和填充 | 最高保真，最重 |

---

## 5. 模板注册表机制（解决"给模板→按模板输出"）

这是整个方案的关键创新点，让"用户给几个喜欢的模板，以后自动按模板输出"成为可能。

### 5.1 工作流

```
1. 用户入库模板
   ├── Word: 用户提供 .docx → 自动扫描 Jinja2/{tag} 占位符
   ├── LaTeX: 用户提供 .tex → 自动扫描 \command{} 和 Jinja2 占位符
   └── HTML:  用户提供 .html → 自动扫描 {{}} 占位符
        ↓
2. 自动生成 schema（JSON Schema）
   {
     "title": "string",
     "author": "string",
     "sections": [{"heading": "string", "content": "markdown"}],
     "date": "date"
   }
        ↓
3. AI 生成时，schema 作为 structured output 约束
   LLM 只能产出符合 schema 的数据 → 保证与模板匹配
        ↓
4. 引擎渲染 → 输出文档（完美继承模板样式）
```

### 5.2 模板分类

| 类型 | 用途 | 示例 |
|------|------|------|
| **全局模板** | 默认主题/品牌，所有文档继承 | 公司品牌色、字体、页眉页脚 |
| **场景模板** | 按文档类型选择 | 论文模板、周报模板、合同模板 |
| **用户自定义** | 用户上传的"喜欢的模板" | 用户提供的设计稿 |

---

## 6. 与现有项目的整合路线（harryopo LaTeX）

### 6.1 当前状态
- ✅ harryopo LaTeX 模板体系（base.sty + cls）正在开发
- ✅ Word ↔ MD ↔ LaTeX 转换 skill 开发中
- ⬜ 可视化编辑层
- ⬜ 模板注册表

### 6.2 分阶段路线图

#### 阶段 1：模板驱动生成（立即，纯 Skill）
- [ ] 完成 harryopo LaTeX 模板（base.sty + 4 个 cls）
- [ ] Word ↔ Markdown ↔ LaTeX 转换 skill（Pandoc 为中枢）
- [ ] **docxtpl 模板填充子 skill**：用户提供 .docx 模板 → 自动提 schema → AI 填充
- [ ] 模板注册表 v1（本地文件夹 + manifest.json）

**产出**：AI 输出的 Word/PDF 不再丑，严格按模板。

#### 阶段 2：本地可视化预览（短期）
- [ ] Skill 生成后自动启动本地预览服务器
- [ ] LaTeX 用 latexmk + PDF 实时预览
- [ ] Word 用 docx-preview 渲染 HTML 预览
- [ ] 用户改源文件（.md/.tex）→ 自动重新生成

**产出**：用户能"看到"AI 做的东西，在源文件层修改。

#### 阶段 3：Web 可视化编辑器（中期，独立产品）
- [ ] React + TipTap 编辑器
- [ ] ProseMirror Doc 作为结构化中间表示
- [ ] Yjs + AI 流式插入
- [ ] inline diff 审阅 UX
- [ ] 一键导出 Word/PDF/PPT

**产出**：真正的"可视化 + 途中可编辑"。

#### 阶段 4：完整办公平台（长期）
- [ ] 模板市场（上传/分享模板）
- [ ] 多人协作
- [ ] 版本审计（AI/手动标记）
- [ ] ONLYOFFICE 深度集成（OOXML 原生编辑）

---

## 7. 最值得集成/借鉴的开源项目（精选 Top 10）

| # | 项目 | Stars | 用途 | 为什么选它 |
|---|------|-------|------|-----------|
| 1 | **Pandoc** | 45.8K | 格式转换中枢 | Markdown ↔ 全格式，reference-doc 机制实现品牌化输出 |
| 2 | **docxtpl** | 2.1K | Word 模板引擎 | Jinja2 语法，.docx 即模板，Python 生态，免费 |
| 3 | **Typst** | 55.3K | 现代排版引擎 | 编译快 3-100x，LaTeX 的现代替代，未来备选 |
| 4 | **WeasyPrint** | 9.5K | HTML→PDF | CSS 控制排版，设计型 PDF 最佳 |
| 5 | **TipTap** | 29K | 富文本编辑器 | ProseMirror 内核，50+ 扩展，docx 导入导出 |
| 6 | **Yjs** | 18K | 协作/CRDT | AI 流式插入的黄金标准 |
| 7 | **Marp** | 8.8K | Markdown→PPT | 最简洁的演示生成，成熟 Skill 生态 |
| 8 | **Presenton** | 9.4K | AI 演示生成 | Gamma 的开源替代，HTML+Tailwind 渲染 |
| 9 | **docx-preview** | 1.5K | docx 浏览器渲染 | 高保真预览 Word |
| 10 | **Overleaf CE** | 15K | LaTeX 在线编辑 | 生产级 LaTeX 可视化编辑，可私有部署 |

---

## 8. 关键避坑指南（来自调研）

1. **绝不让 AI 直接生成 .docx/.pdf 二进制** —— 这是 ChatGPT/Copilot 文件生成"排版崩坏"的根源。LLM 在语义层，文档在排版层。
2. **模板的最佳形态是用户熟悉的工具本身** —— Word 文件、LaTeX 文件、HTML 文件。让用户在这些工具里设计模板。
3. **AI 的角色限定为"数据生产者"** —— 通过 structured output / JSON schema 产出数据，引擎负责渲染。
4. **让 AI 输出完整文档 + 系统自己 diff** —— 比让 AI 输出"操作序列"可靠得多。
5. **中文支持是硬约束** —— 所有方案必须验证中文字体嵌入、CJK 断行、标点处理。WASM 引擎对中文字体支持需先验证。
6. **inline diff + 建议模式混合** —— 避免全文重生成（丢失用户已认可的部分）。
7. **版本审计是差异化机会** —— 没有现有工具在接受内容后保留 AI 来源标记。

---

## 9. 立即可以做的事

基于你当前的进度（正在开发 Word↔MD↔LaTeX skill），建议：

1. **优先完成 docxtpl 模板填充能力** —— 这是"按模板输出"最快见效的部分。
   - 做一个子 skill：输入 .docx 模板 → 自动分析占位符 → 生成 schema → AI 填充 → 输出品牌化 .docx
2. **把 Pandoc 作为转换中枢** —— Word↔MD↔LaTeX 都走 Pandoc，保证质量和一致性。
3. **建立模板注册表** —— 一个 `templates/` 文件夹 + manifest，记录每个模板的 schema 和适用场景。
4. **可视化先做"本地预览"** —— 不急于做 Web 编辑器，先让 Skill 生成后自动开本地服务器预览 PDF/HTML，验证"不丑"。

---

## 附：调研报告索引

| 报告 | 内容 | 路径 |
|------|------|------|
| AI 文档生成调研 | 30+ 开源项目 + 10+ 商业产品对比 | [docs/research/2026-08-08-ai-office-generation.md](../research/2026-08-08-ai-office-generation.md) |
| 模板引擎调研 | Word/LaTeX/PDF 模板引擎深度对比 | [docs/research/2026-08-08-template-engines.md](../research/2026-08-08-template-engines.md) |
| 可视化编辑调研 | 浏览器编辑、实时预览、AI 编辑 UX | [docs/research/2026-08-08-visual-editing.md](../research/2026-08-08-visual-editing.md) |

---

> **方案状态**: 调研完成，架构已定。下一步进入实施规划。
