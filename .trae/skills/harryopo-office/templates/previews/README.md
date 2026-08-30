# harryopo-office 示例文档

本目录是 **harryopo-office skill 的官方示例文档**（Markdown 中间态），可直接用最新 skill 渲染为 Word (.docx) 与 LaTeX (PDF) 双格式。

## 示例清单

| 示例文件 | 模板类型 | 展示特性 |
|----------|----------|----------|
| `paper-single-column.md` | 论文单栏 (`harryopo-paper`) | 基础论文：摘要/关键词/多级标题/公式/表格/参考文献 |
| `paper-twocolumn.md` | 论文双栏 (`harryopo-paper[twocolumn]`) | 双栏排版 + 摘要跨栏 + 末页栏平衡 (flushend) |
| `paper-showcase.md` | 论文全特性 (`harryopo-paper`) | 算法伪代码/多列表格/行内公式/交叉引用/上标引文 |
| `report.md` | 报告 (`harryopo-report`) | 章节式（chapter）+ 自动目录 + 六章完整报告 |
| `report-showcase.md` | 报告全特性 (`harryopo-report`) | RAG 多 Agent 设计报告 + Mermaid 流程图 + 大量表格 |

## 元信息约定（文档头部 blockquote）

渲染前由引擎提取，`convert.py`（LaTeX）与 `md_to_word.py`（Word）双链路同步支持：

```markdown
# 主标题

> 副标题：xxx                 # 可选，与主标题同字体同字号（方正大标宋 22pt），仅换行区分
> 作者：张三、李四            # 多作者用顿号分隔
> 单位：示例大学   # 或 `> 学校：`，渲染为作者行下方仿宋小字
> 日期：2026年8月29日
```

## 生成命令（统一入口 office.py）

```bash
# 单栏论文：Word + PDF
python office.py render paper-single-column.md --format word,paper --type paper

# 双栏论文
python office.py render paper-twocolumn.md --format paper --type paper --twocolumn

# 报告（章节式 + 自动目录）
python office.py render report.md --format word,paper --type report

# 论文全特性 / 报告全特性
python office.py render paper-showcase.md --format word,paper --type paper
python office.py render report-showcase.md --format word,paper --type report

# 自定义输出目录（建议统一 output/<项目名>/）
python office.py render paper-single-column.md --format word,paper --output-dir ../../output/examples
```

产物命名规则（同目录）：

- `{文件名}-word.docx`（Word）
- `{文件名}-paper.pdf` / `{文件名}-report.pdf`（PDF）
- `{文件名}-paper.tex` / `{文件名}-report.tex`（LaTeX 源码，可在 IDE 中编辑预览）
- `figures/`（mermaid / super-diagram / diagram-design 渲染的图片）

## 预览方式

- **VS Code**：安装 Markdown Preview Enhanced，配合 `harryopo-preview.css`（见 [harryopo-preview.css](harryopo-preview.css)）
- **PDF 效果**：以渲染出的 PDF 为准（字体/分栏/页码）
- **LaTeX 二次编辑**：生成 `*.tex` 后用 VS Code + LaTeX Workshop 打开，改完点 ▶ 编译预览

## 常见修复点（2026-08-29 已修复）

1. 摘要/关键词统一 `**摘要：**` / `**关键词：**` 普通段落格式（废弃旧 `> **摘 要**` blockquote）
2. 章节标题统一 `# 第X章` Markdown 格式（废弃旧 `<h1 class="chapter">` HTML 格式）
3. 顶部 HTML 注释 `<!-- ... -->` 由 convert.py 自动剥离
4. 百分比 `%`、`&`、`_` 等特殊字符由 parse_inline 自动转义（曾导致摘要静默截断）
5. 元信息 blockquote（作者/单位/日期/副标题）由双链路跳过正文渲染
6. report 类型自动生成目录，手工目录已移除
7. 双栏依赖 flushend.sty（templates/cls/ 自包含副本，规避 TinyTeX 缺包）
