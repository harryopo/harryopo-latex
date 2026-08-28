# anydoc 调研报告 — Firecrawl 多格式文档→Markdown 转换器

> 调研日期：2026-08-11 ｜ 来源：`https://github.com/firecrawl/anydoc`（MIT） ｜ 源码：`opensource-reference/anydoc/`（已 clone 全量分析）

## 一、项目定位

Firecrawl 出品的**纯 Rust 文档转 Markdown 库**：Word/PowerPoint/Excel/OpenDocument/RTF/EPUB/CSV/PDF → 统一 GitHub-Flavored Markdown（GFM）。为 Firecrawl Parse 提供本地转换内核。自带 Python / Node / WASM / Rust 绑定 + Agent Skill。

## 二、架构分析（源码级）

三层设计，所有格式共享一份输出逻辑：

```
document bytes
  → format detection（内容嗅探：PDF 头 / RTF 开组 / OLE 流名 / ZIP mimetype，不依赖扩展名）
  → 格式 parser（doc/docx/ppt/pptx/xls/xlsx/odt/ods/odp/rtf/epub/csv 各一，PDF 走 pdf-inspector）
  → 共享 Document model（blocks/inlines/tables/notes/assets）
  → 单一 GFM serializer → Markdown
```

- `src/model/`：统一文档模型（Block/Inline/Table/List/Asset）
- `src/formats/`：每格式独立 parser（docx 含 styles/numbering/content 三层）
- `src/render/markdown/`：单一 serializer（anchors/escape/inline/table）
- `src/package/`：ZIP/OLE 安全解析（防 zip bomb、深度嵌套、节点数、解压比上限）

**安全设计**：ResourceLimit 硬上限（解压比、嵌套深度、节点数、重复展开、资产字节）→ 恶意文档不拖垮进程（`tests/fixtures/abuse/` 有 deepxml/imagebomb/zipbomb 测试）。

## 三、关键能力

| 能力 | 说明 |
|------|------|
| 14 种格式 | doc/docx/docm、ppt/pps/pot/pptx/pptm/ppsx/ppsm、xls/xlsx/xlsm/xlsb、odt/ods/odp、rtf、epub、csv、pdf |
| 速度 | 纯 Rust 无 ML，中位 **4.4ms/文档**（实测公文模板 13ms） |
| 结构保留 | 标题锚点、加粗/斜体/删除线、行内码/代码块、链接与交叉引用、多级列表（保留源编号）、表格（含合并单元格→GFM 空白占位）、引用块、脚注/尾注、演讲者备注 |
| 内容嗅探 | 从字节识别格式，扩展名错误仍能正确转换 |
| 内嵌资源 | 图片→alt 文本，原始字节存 `document.assets`（media_type + origin_part），外部 URL 图片→普通 MD 图片 |
| 绑定 | Python（释放 GIL）、Node（libuv 线程池）、WASM（浏览器本地转换）、Rust crate |
| Agent Skill | `npx skills add firecrawl/anydoc` → `anydoc <file> [-o out.md]`，CLI 无需安装（npx 拉预编译二进制） |

**官方基准**（LLM 盲评，6 工具 100 文档）：anydoc **81**（全格式最高）＞ mammoth 70（仅 docx）＞ markitdown 65 ＞ unstructured 63 ＞ docling 57 ＞ pandoc 56 ＞ libreoffice 40。

## 四、限制（对当前项目关键）

1. **图片不落盘**：内嵌图片在 MD 中只有 alt 文本，字节在 `document.assets`（Python `to_document()` 可取，需脚本写盘并回填 MD 路径）——当前 Word 链路是 `![图N：](figures/xx.png)`，需补一层
2. **合并单元格丢失 span**：GFM 无 span 语法，colspan/rowspan 输出为空白单元格——当前"HTML 表格→LaTeX \multicolumn/\multirow"链路需从 `to_document` 的 Cell 模型重建
3. **PDF 仅文本型**：走 pdf-inspector，扫描件/公式 PDF 报 Unsupported（与 MinerU 互补）
4. **输出为 GFM**：`direct_answer` 下划线不转义（下游转 LaTeX 时 `_` 仍可能触发数学模式，那是 convert.py 层的事）

## 五、实测（本项目环境）

公文模板 `蒸馏区\harryopo-公文模板.docx`（5 页、3 表格、目录域）：

- 转换 **13ms**，输出 5063 字符
- 标题层级 `# 一、引言` / `## 2.1` 正确；`**摘要：**`/`**关键词：**` 保留
- 3 个表格全部正确（表头加粗识别、`direct_answer` 下划线不丢）
- 目录域→锚点链接保留（当前链路是删 TOC，anydoc 保留可选择性保留/删除）
- 参考文献 `\[1\]` 正确转义

## 六、与当前链路对比

| 维度 | 当前（pandoc + python-docx 回填 + MinerU） | anydoc |
|------|------|------|
| docx 速度 | pandoc 102ms + python-docx 表格回填 | 13ms 全流程 |
| 表格 | pandoc 不可信 → python-docx 按 body 流提取回填 | 原生表格解析（GFM） |
| 格式覆盖 | docx/pdf 为主 | 14 种 |
| 扫描 PDF | MinerU（200ms/页，公式/OCR） | 不支持（需 OCR） |
| 图片 | 回填路径 | alt 文本 + assets（需补落盘） |

## 七、集成建议（三档）

**A. Fast path（推荐先做，低风险）**：`office.py` 的 DOCX/ODT/RTF/PPT/XLSX 预处理分支并行引入 anydoc 作为首选转换器，pandoc/MinerU 降级兜底。改动集中在 `scripts/office.py` + `scripts/docx_clean.py`（适配 GFM 输出差异），AI 读文档内容场景提速 ~100 倍。

**B. 完整集成**：A + `to_document` 模型补两层：①assets 写盘→回填 `![alt](path)`；②Cell 模型→重建 HTML 表格（含 span）→LaTeX \multicolumn/\multirow。工作量中等，替换掉 python-docx 回填 + pandoc 两条依赖。

**C. 维持现状**：仅作为独立工具/Agent Skill 使用（`npx @firecrawl/anydoc` 读任何文档进上下文）。

## 结论

anydoc 是目前文档→MD 转换的最佳开源方案（速度/覆盖/质量三维最优，MIT），与 MinerU（扫描/公式）互补。建议采用 **A 档 fast path** 先行验证，稳定后再评估 B 档。
