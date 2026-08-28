# 办公超级 Skill 架构方案 v2（2026-08-28 更新）

> **v1 日期**: 2026-08-08（[2026-08-08-office-super-skill.md](./2026-08-08-office-super-skill.md)）
> **v2 日期**: 2026-08-28
> **v2 更新动因**: 用户指示"当前又出来了很多开源的办公方案（tex64 mcp、markitdown、docling 等），深入调研后集成优化，更新开发方案书"
> **v2 调研依据**: [2026-08-28 开源方案深度调研](../research/2026-08-28-开源方案深度调研-tex64-mcp-markitdown-docling.md)
> **目标不变**: 生成标准美观的 Word / LaTeX / PDF 并互相转换，内置流程图生成能力

---

## 0. 一句话总结

**v1 确立的范式依然成立且已被市场验证：AI 产出结构化数据（MD/JSON）→ 模板引擎渲染，绝不直接生成 OOXML/排版代码**。v2 的增量是把"互相转换"的地基（解析端）从单点补成体系，并明确三条低本高收益链路：

1. **解析端三级路由**：`anydoc 快检 → MinerU 深解析 → markitdown 兜底`（markitdown 为微软官方 12.6 万 star 项目，补齐 20+ 格式输入，docx→md 提速约 100 倍）
2. **Word → PDF 直接导出**：word_template_engine.py 已有 COM 基础设施，加一次 `doc.ExportAsFixedFormat(...)` 即打通，Word 链路不再绕 LaTeX
3. **LaTeX → Word 统一走 MD 中间态**：Pandoc tex→docx 试验预期 CJK/自定义宏还原度差，务实决策是 `.tex → MD 清洗 → Word 引擎渲染`——MD 中间态本就是本项目核心范式

---

## 1. 四大核心需求 → 技术对策（v2 修订）

| # | 需求 | 技术对策 | v2 增量 |
|---|------|---------|---------|
| 1 | AI 输出按模板来，不再丑 | 模板引擎驱动（docxtpl / harryopo LaTeX）+ 自动 schema 提取 | 维持 v1；渲染端不新增（docxtemplater v3+ 商业许可陷阱，仅 JS 栈评估） |
| 2 | Word ↔ Markdown ↔ LaTeX 互转 | **Pandoc 为中枢** + 解析三件套 + LibreOffice headless 兜底 | **v2 重点**：解析端升级为四级体系（§2），Word→PDF 直接导出（§3），LaTeX→Word 定 MD 中间态（§4） |
| 3 | 办公文件可视化、途中可编辑 | TipTap + Yjs + inline diff | 参考 MagicTeX-mcp"评论锚定→agent 修复 + 编译历史快照"交互范式（阶段 3） |
| 4 | 按用户模板输出 | 模板注册表 + 自动 schema 提取 | 维持 v1；模板反解备选 mammoth |

---

## 2. 解析端：四级分工矩阵（v2 新增核心）

> 调研结论：markitdown（微软官方）/ docling（IBM，LF 治理）都是"文档→Markdown"方向，与本项目范式完全一致。解析器并存必须明确分工，避免四套打架。

| 解析器 | 定位 | 速度 | 强项 | 弱项 | 触发条件 |
|---|---|---|---|---|---|
| **anydoc**（已集成） | 快检 fast path | 毫秒级（纯 Rust） | 14 格式→GFM MD，表格原生 | 复杂版面/扫描件弱 | 常规文档首选 |
| **MinerU**（已集成） | 深解析 | 0.2s/页（纯 CPU） | 扫描件 OCR、colspan/rowspan 表格、LaTeX 公式 | 速度慢于 anydoc | 扫描件/复杂版面 |
| **markitdown**（v2 新增，P0） | 兜底 + 长尾 | 快 | 微软官方 Office 原生格式保真（DOCX/PPTX/XLSX）、音视频转写、20+ 格式 | PDF 无版面分析 | anydoc/MinerU 不支持或质量差时 |
| **docling**（v2 新增，P1） | 互为兜底 | 慢（~1GB 模型） | 布局感知、统一 DoclingDocument、**LaTeX 输入**、官方 MCP | 体积大、首次加载慢、中文 PDF 需实测 | 仅复杂文档与 MinerU 对比验证 |

**集成动作（office.py 预处理分支）**：

```python
def to_markdown(path):
    # 1. anydoc 快检（毫秒级，14 格式）
    md = anydoc_convert(path)          # fast path
    if md and quality_ok(md): return md
    # 2. MinerU 深解析（扫描件/复杂版面/公式）
    md = mineru_convert(path)          # 0.2s/页
    if md and quality_ok(md): return md
    # 3. markitdown 兜底（长尾格式/音视频/官方 Office 原生）
    return markitdown_convert(path)    # pip install markitdown
```

---

## 3. Word → PDF 直接导出（v2 新增，P1，成本最低收益最直接）

**现状**：word_template_engine.py 已有 COM 基础设施（打开 Word、更新 TOC、SaveAs2），Word 出 PDF 目前绕 LaTeX，链路长。

**动作**：在渲染完成后追加一次调用：

```python
# word_template_engine.py 渲染尾部（render 后、close 前）
doc.ExportAsFixedFormat(OutputFileName, ExportFormat=17)  # wdExportFormatPDF=17
```

**收益**：Word 链路直接出 PDF，页数/字体/分页 100% 与 Word 所见一致；不依赖 LaTeX 字体映射，公文/报告类 Word 模板出 PDF 保真。

---

## 4. LaTeX → Word：统一走 MD 中间态（v2 决策）

**背景**：LaTeX → Word 是唯一完全空白的方向。候选两条路：

| 路线 | 预期质量 | 结论 |
|---|---|---|
| Pandoc tex→docx 直转 | CJK 字体映射、自定义宏（harryopo 主题色/字体命令）、浮动体还原度差 | 可做试验验证，但不作为生产链路 |
| **.tex → MD 清洗 → Word 引擎渲染** | 清洗规则可沉淀（标题/表格/公式→OMML 映射），中间态用户可编辑 | **✅ 采用**（符合 MD 中间态核心范式） |

**实施要点**：
- `.tex → MD`：基于现有 `scripts/convert.py` 反向逻辑 + MinerU 两阶段审查（review → convert）复用
- `MD → Word`：走已跑通的 `md_to_word.py`（方正/开源字体、OMML 公式、原生目录）
- 清洗规则：去自定义宏（`{\fzht ...}` 等转义为样式）、tabular → MD 表格、公式 → LaTeX 内联保留（Word 引擎转 OMML）
- **验收线**：标题层级、表格、正文格式还原度达标即算通过；公式、浮动体可降级为文本/图片

---

## 5. 目标架构总览（三层闭环，v1 保留 + v2 标注）

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户层                                   │
│   自然语言需求  +  用户提供的模板（Word/LaTeX/HTML）+ 任意输入文件 │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ① 生成层（AI）                              │
│   LLM 产出结构化数据（JSON/YAML/Markdown）                       │
│   受模板 schema 约束（structured output）                        │
│   解析端入口：anydoc → MinerU → markitdown → docling（v2）       │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ② 编辑层（可视化）                          │
│   TipTap/ProseMirror 编辑器 + Yjs 协作 + inline diff 审阅        │
│   参考 MagicTeX-mcp：评论锚定→agent 修复 + 编译历史快照（v2）     │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ③ 输出层（渲染）                            │
│   Word:  docxtpl / md_to_word（COM 更新 TOC）                    │
│   PDF:   XeLaTeX + harryopo 模板 / Word 直接导出(v2)             │
│   互转:   Pandoc 中枢 + LibreOffice headless 兜底 + pdfcpu(v2)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. LaTeX 编译诊断闭环：harryopo-build-mcp（v2 决策，替代"tex64 mcp"）

**调研澄清**：tex64 是商业 LaTeX 编辑器（非开源、无 MCP），不采纳。但 LaTeX MCP 生态（MagicTeX-mcp 等）验证了"AI 交互式编译诊断闭环"价值。

**动作**：自封装 `harryopo-build-mcp`——用 MCP 包装 build.ps1：

```
build.ps1（3 遍 XeLaTeX + TEXINPUTS + 页数统计）
  → MCP 工具：harryopo_build(tex_file) / harryopo_diagnostics() / harryopo_fix_suggestion(error)
  → AI 获得：编译 → 日志解析 → 错误定位（行号）→ 修复建议 的闭环
  → 保留原生 XeLaTeX + 方正字体全部能力（WASM 引擎 CJK 弱，不用于生产链路）
```

---

## 7. 模板注册表机制（v1 保留）

工作流不变：用户入库模板 → 自动扫描占位符 → 生成 JSON Schema → AI 产出受约束数据 → 引擎渲染。v2 补充：Word 模板反解可评估 mammoth 作轻量备选；模板注册表 manifest.json 列为阶段 1 收尾项。

---

## 8. 分阶段路线图（v2 修订）

### 阶段 0：资产与地基（v2 新增收尾）
- [x] git 工作区资产保护（8/10-8/16 成果已提交，4 commit）
- [ ] 解析端三级路由落地：markitdown 接入 office.py（**P0，1 周内**）

### 阶段 1：模板驱动生成（v1 阶段 1 完成项保留 + 新收尾）
- [x] harryopo LaTeX 模板体系（base.sty + paper/report.cls，46 个 .tex 全通过）
- [x] docxtpl 模板填充子 skill（11 项端到端验证通过）
- [x] Word ↔ Markdown ↔ LaTeX 转换（Pandoc 中枢 + MinerU 两阶段审查）
- [x] 模板注册表 v1（manifest.json）✅（2026-08-28，24 项端到端验证；M2 LaTeX 反解待后续）
- [x] 解析端三级路由落地（markitdown P0）

### 阶段 2：输出链路打通（v2 重点，1 个月内）
- [ ] **Word → PDF 直接导出**（`doc.ExportAsFixedFormat`，COM 复用）
- [ ] **LaTeX → Word MD 中间态链路**（.tex → MD 清洗 → md_to_word）
- [ ] docling 接入作 MinerU 互为兜底（复杂文档路径，~1GB 模型按需）
- [ ] **harryopo-build-mcp**（自封装，编译诊断闭环）
- [ ] 本地预览服务器（v1 阶段 2）

### 阶段 3：Web 可视化编辑器（中期，独立产品）
- [ ] React + TipTap 编辑器 + ProseMirror Doc 中间表示
- [ ] Yjs + AI 流式插入 + inline diff 审阅
- [ ] 参考 MagicTeX-mcp：评论锚定→agent 修复 + 编译历史快照
- [ ] 一键导出 Word/PDF（含 Word 直出 PDF）
- [ ] JS 栈评估：docxtemplater（**警惕 v3+ 商业许可**）/ docxjs / html-to-docx

### 阶段 4：完整办公平台（长期）
- [ ] 模板市场 + 多人协作 + 版本审计（AI/手动标记，参考 azzindani 版本快照+操作收据思想）
- [ ] ONLYOFFICE 深度集成（OOXML 原生编辑）
- [ ] pdfcpu 收进工具箱（PDF 水印/合并/元数据，P2）
- [ ] quarto 评估为学术报告第二渲染入口（GPL-2.0 许可先确认）
- [ ] Typst 第三输出通道储备（P3 长期）、tectonic、LibreOffice headless 互转兜底

---

## 9. 集成决策速查（v2）

| 决策 | 项目 | 等级 | 动作 |
|---|---|---|---|
| **Adopt** | markitdown / markitdown-mcp | P0 | office.py 第三级解析兜底 |
| **Adopt/Trial** | docling | P1 | MinerU 互为兜底 + LaTeX 解析 |
| **Trial** | MagicTeX-mcp | P1 | 阶段 3 Web 编辑器交互范式参考 |
| **Trial** | fukui-yuto/microsoft-office-mcp | P1 | COM 工具划分参考（渲染后操作） |
| **Trial** | pdfcpu | P2 | PDF 后处理工具箱 |
| **Trial** | quarto | P2 | 学术报告第二渲染入口评估 |
| **Hold** | tex64 | — | 商业闭源，不采纳；产品方向已验证 |
| **不引入** | overleaf-mcp / j2docx / unstructured / 公文低星项目 | — | 与现有重复或质量不足 |

**范式红线**：所有集成守住"AI 只产结构化数据 → 模板引擎渲染"铁律；Office MCP/自动化只做**渲染后操作**（目录刷新、修订、导出 PDF），绝不回到"AI 直接改文档二进制"。

---

## 10. 关键风险清单（v2）

1. **解析器分工漂移**：anydoc / MinerU / markitdown / docling 四级并存，须严格按触发条件路由，避免功能重叠互相打架
2. **markitdown PDF 质量**：无版面分析，仅兜底角色，不替代 MinerU 深解析
3. **docling 体积**：~1GB 模型、首次加载慢——仅复杂文档路径启用，中文 PDF 先实测
4. **许可合规**：docxtemplater v3+ 商业许可、quarto GPL-2.0、mupdf AGPL——使用前确认
5. **LaTeX→Word 还原度**：MD 中间态清洗规则需持续沉淀，公式/浮动体可降级
6. **WASM 引擎中文风险**：tex64/MagicTeX 的 WASM TeX 对 CJK/方正字体支持弱——不用于生产编译链路
7. **数据时效**：stars 数据截至 2026-06/07，集成前以 GitHub 实时为准

---

## 附：调研报告索引

| 报告 | 内容 | 路径 |
|------|------|------|
| v2 开源方案深度调研 | tex64 澄清、markitdown、docling、LaTeX MCP 生态、Office MCP 生态、推荐度评分 | [docs/research/2026-08-28-开源方案深度调研-tex64-mcp-markitdown-docling.md](../research/2026-08-28-开源方案深度调研-tex64-mcp-markitdown-docling.md) |
| v1 架构方案 | 三层闭环、模板注册表、可视化编辑、精选 Top 10 | [docs/plans/2026-08-08-office-super-skill.md](./2026-08-08-office-super-skill.md) |

---

> **方案状态**: v2 调研结论已整合，实施进入阶段 1 收尾 + 阶段 2 输出链路打通。
