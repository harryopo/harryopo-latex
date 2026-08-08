# harryopo-latex Skill 扩展方案：Word/MD → LaTeX 表格攻坚

> **方案日期**: 2026-08-05
> **方案类型**: 现有 skill 增强（非新建工作台）
> **决策来源**: 用户四问回答——扩展 Skill + 混合场景 + 表格痛点全选 + LLM 仅填参数
> **关联调研**: [Word-Markdown-to-LaTeX-开源方案深度调研报告.md](./Word-Markdown-to-LaTeX-开源方案深度调研报告.md)
> **关联代码**: [.trae/skills/harryopo-latex/](../.trae/skills/harryopo-latex/)

---

## 1. 为什么不做独立工作台

用户最初提到"工作台或 skill"，经过四问对齐后明确选择 **扩展 Skill**。理由：

| 维度 | 独立工作台 | 扩展现有 Skill（选定） |
|------|-----------|----------------------|
| 复用资产 | 从零起步，重复造轮子 | 直接迭代 convert.py/md2latex.py/模板 |
| AI 集成 | 需自己接 API、写 prompt | 天然在 AI IDE 里跑，零集成 |
| 维护成本 | 前后端+依赖+部署长期负担 | 仅维护脚本和模板 |
| 新手友好 | 需要重 UI 才能实现 | 用 MD 中间态 + PDF 预览替代 |
| 离线可用 | 受限于 LLM API | 脚本本身离线可跑（只填参数时才需 LLM） |

**结论**：把"可视化"和"新手友好"通过 **流程设计** 而非 UI 实现——MD 中间态就是天然的可视化层。

---

## 2. 用户痛点聚焦

用户在表格问题上**四个选项全选**（合并丢失、列宽溢出、跨页断行、嵌套结构），说明这是核心攻坚方向。

| 痛点 | 行业现状 | 本次目标 |
|------|---------|---------|
| 合并单元格丢失 | Pandoc 行业平均水平 70%，垂直合并尤差 | L1 水平合并 100%、L2 垂直合并 90%+ |
| 列宽溢出 | 所有工具通病，靠 tabularx 缓解 | 已有方案，需覆盖到所有表格类型 |
| 跨页表格断行 | 需手动 longtable | 行数阈值自动切换 longtable |
| 复杂嵌套 | 无开源方案能完美处理 | **不强行转换**，输出占位+手工模板 |

---

## 3. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│ 用户上传 .docx / .md / .txt                                  │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM 仅做：意图理解 → CLI 参数填充 → 用户确认话术              │
│ （不做：内容生成、表格修复、文件修改）                          │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 预处理层 preprocess.py 【新增】                                │
│  ├── DOCX：zipfile + XML 解析（绕过 python-docx 结构丢失）     │
│  │   ├── 提取 w:tblGrid（列规格）                              │
│  │   ├── 提取 w:vMerge（垂直合并）                             │
│  │   ├── 提取 w:gridSpan（水平合并）                           │
│  │   └── 检测嵌套 w:tbl                                        │
│  ├── 表格分级：L0 简单 / L1 水平 / L2 垂直 / L3 跨页 / L4 嵌套 │
│  └── 输出：标准化 MD + tables.json（表格元数据）               │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 转换层 【已有，需扩展】                                        │
│  ├── convert.py（现有，扩展表格分支）                          │
│  │   ├── L0 → tabularx + booktabs（现有逻辑）                 │
│  │   ├── L1 → \multicolumn + tabularx                        │
│  │   ├── L2 → \multirow + 固定列宽 tabular                    │
│  │   ├── L3 → longtable + \endhead + \endfoot                │
│  │   └── L4 → 占位符 + 警告 + 手工修复模板                    │
│  └── md2latex.py（现有，新增 pandoc-harryopo 引擎）           │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Pandoc 集成 【新增模板和增强 Lua】                             │
│  ├── harryopo-pandoc-template.latex（替换 KOMA-Script）       │
│  └── harryopo-table.lua（基于 mathnotes-table.lua 扩展）      │
│      ├── 智能列宽（已有）                                      │
│      ├── colspan/rowspan 支持（Pandoc 3+ 原生属性）            │
│      └── 自动判断 simple/longtable                            │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 编译层 build.ps1 【已有】                                      │
│  └── xelatex × 3 → PDF                                        │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 反馈层 【轻量新增】                                            │
│  ├── 编译失败 → log_parser.py 解析 .log → 结构化错误          │
│  ├── PDF 预览 → 自动打开                                      │
│  └── 表格 ASCII 预览 → 让用户确认结构                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 表格分级处理详细策略

### 4.1 分级检测规则

| 等级 | 名称 | 检测条件 | 自动化程度 |
|------|------|---------|-----------|
| **L0** | 简单表 | 无合并、行数 ≤ 10 | 全自动 |
| **L1** | 水平合并表 | 有 gridSpan、无 vMerge | 全自动 |
| **L2** | 垂直合并表 | 有 vMerge | 自动（90%），余下提示手工 |
| **L3** | 跨页表 | 行数 > 20 或单行高度 > 0.3\textheight | 全自动（切 longtable） |
| **L4** | 嵌套/复杂表 | 表中表、单元格含图、合并+嵌套同时存在 | **不自动**，输出模板 |

### 4.2 各等级 LaTeX 输出模板

**L0 简单表**（现有逻辑保留）
```latex
\begin{table}[htbp]
  \centering\small
  \begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X ... }
    \toprule
    \textbf{Col A} & \textbf{Col B} \\
    \midrule
    data & data \\
    \bottomrule
  \end{tabularx}
  \caption{...}
\end{table}
```

**L1 水平合并**
```latex
\begin{table}[htbp]
  \centering\small
  \begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X ... }
    \toprule
    \multicolumn{2}{c}{\textbf{合并表头}} & \textbf{Col C} \\
    \cmidrule(lr){1-2}
    A & B & C \\
    \midrule
    ...
    \bottomrule
  \end{tabularx}
\end{table}
```

**L2 垂直合并**（关键：tabularx 与 multirow 冲突，需固定列宽）
```latex
\begin{table}[htbp]
  \centering\small
  \begin{tabular}{l l l}  % 固定列宽，放弃 tabularx
    \toprule
    \textbf{A} & \textbf{B} & \textbf{C} \\
    \midrule
    \multirow{3}{*}{合并值} & b1 & c1 \\
     & b2 & c2 \\
     & b3 & c3 \\
    \bottomrule
  \end{tabular}
\end{table}
```

**L3 跨页**
```latex
\begin{longtable}{>{\raggedright\arraybackslash}p{0.3\textwidth} ... }
  \toprule
  \textbf{A} & \textbf{B} \\
  \midrule
  \endfirsthead
  \multicolumn{2}{l}{\small\itshape 续上表} \\
  \toprule
  \textbf{A} & \textbf{B} \\
  \midrule
  \endhead
  \midrule
  \multicolumn{2}{r}{\small\itshape 下页续} \\
  \endfoot
  \bottomrule
  \caption{跨页表格标题} \\
  \endlastfoot
  data & data \\
  ...
\end{longtable}
```

**L4 嵌套/复杂**（不自动转，输出占位）
```latex
% [WARN] 表格 #N 为嵌套结构（单元格内含表格/图片），自动转换不可靠
% 已生成占位符。建议手工重建，参考模板：
%   \begin{table}[htbp]
%     \centering
%     \begin{tabular}{|c|c|}
%       \hline
%       \begin{tabular}{@{}c@{}} ... \end{tabular} & ... \\  % 内嵌表
%       ...
%     \end{tabular}
%   \end{table}
\textbf{【表格 #N 待手工处理】原始 Word 表格请见附件}
```

### 4.3 表格元数据 JSON Schema

`preprocess.py` 输出的 `tables.json` 示例：
```json
{
  "tables": [
    {
      "id": 1,
      "level": "L2",
      "rows": 5,
      "cols": 3,
      "has_vmerge": true,
      "has_gridspan": false,
      "has_nested": false,
      "estimated_height_tex": "0.25\\textheight",
      "raw_md": "| A | B | C |\n|---|---|---|\n...",
      "suggestion": "use_multirow",
      "warning": null
    },
    {
      "id": 2,
      "level": "L4",
      "rows": 8,
      "cols": 4,
      "has_vmerge": true,
      "has_gridspan": true,
      "has_nested": true,
      "warning": "嵌套表格+合并，自动转换不可靠",
      "suggestion": "manual_rebuild"
    }
  ]
}
```

---

## 5. 关键脚本设计

### 5.1 preprocess.py（新增）

**职责**：DOCX 结构化解析，输出标准化 MD + tables.json

**核心实现**：
- 不使用 python-docx（它丢失合并信息）
- 用 `zipfile` 解压 .docx，直接解析 `word/document.xml`
- XML 命名空间：`w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'`
- 关键标签：
  - `<w:tbl>` 表格根
  - `<w:tblGrid><w:gridCol w:w="..."/>` 列规格
  - `<w:tr>` 行
  - `<w:tc>` 单元格
  - `<w:tcPr><w:gridSpan w:val="N"/>` 水平合并
  - `<w:tcPr><w:vMerge w:val="restart"/>` 垂直合并开始
  - `<w:tcPr><w:vMerge/>` 垂直合并续接

**CLI**：
```powershell
python preprocess.py input.docx -o output_dir/
# 输出 output_dir/input_clean.md + output_dir/tables.json
```

### 5.2 convert.py 扩展点

现有 `_parse_table_to_latex` 只支持 L0。需改为：

```python
def _parse_table_to_latex(raw: str, table_meta: dict = None) -> List[str]:
    """根据表格分级返回对应 LaTeX 代码"""
    if table_meta is None:
        # 无元数据 → 默认 L0 简单处理（向后兼容）
        return _parse_simple_table(raw)

    level = table_meta.get("level", "L0")
    if level == "L0":
        return _parse_simple_table(raw)
    elif level == "L1":
        return _parse_table_with_colspan(raw, table_meta)
    elif level == "L2":
        return _parse_table_with_rowspan(raw, table_meta)
    elif level == "L3":
        return _parse_longtable(raw, table_meta)
    elif level == "L4":
        return _parse_nested_table_placeholder(raw, table_meta)
```

每个 `_parse_table_with_*` 函数独立实现，可单独测试。

### 5.3 harryopo-pandoc-template.latex（新增）

参考 Eisvogel 但替换为 harryopo 体系：

```latex
% harryopo-pandoc-template.latex
% 用于 Pandoc 直转 harryopo LaTeX
\documentclass{$if(twocolumn)$twocolumn,$endif$$if(dark)$dark,$endif$]{harryopo-paper}

\title{$title$}
\author{$author$}
\date{$date$}

$if(abstract)$
\abstractcontent{$abstract$}
$endif$
$if(keywords)$
\keywordscontent{$keywords$}
$endif$

\begin{document}
\maketitle$if(twocolumn)$withabstract$endif$

$body$

$if(bibliography)$
\bibliography{$bibliography$}
$endif$
\end{document}
```

### 5.4 harryopo-table.lua（增强版 Lua Filter）

基于现有 `mathnotes-table.lua` 扩展：
- 保留：智能列宽、booktabs 三线表、caption 下置
- 新增：检测 `colspan`/`rowspan` 属性生成 `\multicolumn`/`\multirow`
- 新增：行数 > 20 自动切 `longtable`

### 5.5 log_parser.py（新增，可选）

编译失败时解析 .log，输出结构化错误：
```json
{
  "errors": [
    {
      "type": "Overfull \\hbox",
      "line": 142,
      "detail": "段落过宽 23.5pt",
      "suggestion": "检查表格列宽或加 \\sloppy"
    }
  ]
}
```

---

## 6. SKILL.md 更新要点

新增"DOCX 表格分级处理"流程：

```markdown
### DOCX 转换流程（含复杂表格）

1. 上传 .docx 后，调用 `python preprocess.py input.docx -o tmp/`
2. 检查 `tables.json`：
   - 全部 L0-L3 → 自动转换走 convert.py
   - 含 L4 嵌套表 → 暂停，向用户提示：
     "表格 N 为嵌套结构，自动转换不可靠。
      建议方案：(a) 在 Word 里拆分表格 (b) 手工填写 LaTeX 模板（已为你生成占位符）"
3. 展示标准化 MD 中间态，请用户确认内容
4. 用户确认后，convert.py 根据表格分级生成对应 LaTeX 代码
5. build.ps1 编译 → 若失败，log_parser.py 给修复建议
```

---

## 7. 实施路线与验收标准

### 阶段 1：DOCX 表格预处理（最高价值）
**交付**：`preprocess.py` + 单元测试
**验收**：
- 能正确解析 5 种典型 DOCX 表格（简单、水平合并、垂直合并、跨页、嵌套）
- 输出 tables.json 准确标注 level
- 标准化 MD 保留所有内容（无丢失）

### 阶段 2：convert.py 表格分支扩展
**交付**：convert.py 新增 `_parse_table_with_colspan/rowspan`、`_parse_longtable`、`_parse_nested_table_placeholder`
**验收**：
- L0-L3 全部能输出可编译的 LaTeX
- L4 输出清晰占位符和手工模板
- 现有测试用例不回归

### 阶段 3：Pandoc 直转集成
**交付**：`harryopo-pandoc-template.latex` + `harryopo-table.lua`
**验收**：
- `pandoc input.md --template harryopo-pandoc-template.latex --lua-filter harryopo-table.lua` 能直接产出可编译 .tex
- 与 convert.py 输出风格一致

### 阶段 4：反馈层与文档
**交付**：`log_parser.py` + SKILL.md 更新 + 表格处理 FAQ
**验收**：
- 编译失败时能给出明确修复建议
- SKILL.md 含表格分级流程图
- 新手按流程能独立完成 DOCX → PDF

---

## 8. 不做的事（明确边界）

- ❌ **不做 Web 工作台**（用户已选 Skill 形态）
- ❌ **不集成 MinerU/Marker**（用户选"LLM 仅填参数"，MinerU 需要 GPU+模型，过重）
- ❌ **不追求 L4 嵌套表自动转换**（行业无解，强行做会出 bug）
- ❌ **不让 LLM 修复表格**（用户明确要求 LLM 仅填参数，修复靠脚本+用户手工）
- ❌ **不动 math-notes 独立体系**（CLAUDE.md 明确警告与 base.sty 冲突）

---

## 9. 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| python-docx 思维定式导致漏掉 XML 信息 | 中 | 强制走 zipfile+XML，禁用 python-docx |
| multirow + tabularx 冲突 | 高 | L2 起放弃 tabularx 用固定列宽 |
| 复杂 DOCX 结构导致 XML 解析崩溃 | 中 | L4 兜底，解析失败直接走占位符 |
| Pandoc 版本差异（colspan 支持需 3.x） | 低 | preprocess.py 检测 Pandoc 版本并降级 |
| 用户 DOCX 用了非常规样式 | 中 | 元数据 JSON 暴露原始 XML 片段供调试 |

---

## 10. 与现有资产的关系

| 现有资产 | 本方案处理方式 |
|---------|--------------|
| `convert.py`（870行） | **扩展**，新增表格分级分支 |
| `md2latex.py` | **保留**，新增 `--engine pandoc-harryopo` 选项 |
| `mathnotes-table.lua` | **作为基础**派生出 harryopo-table.lua（不修改原文件） |
| `harryopo-base.sty` / `paper.cls` / `report.cls` | **不动**（CLAUDE.md 硬规则） |
| `build.ps1` | **不动** |
| `templates/fonts/` | **不动** |
| `math-notes` 独立体系 | **不碰**（CLAUDE.md 硬规则） |
| `SKILL.md` | **更新**，加入新流程 |

---

## 11. 命名与放置

新增文件全部放在 `.trae/skills/harryopo-latex/scripts/` 和 `templates/` 下：

```
.trae/skills/harryopo-latex/
├── scripts/
│   ├── convert.py            # 扩展
│   ├── md2latex.py           # 扩展
│   ├── preprocess.py         # 【新】DOCX 预处理
│   ├── table_repair.py       # 【新】表格分级渲染（也可合并到 convert.py）
│   ├── log_parser.py         # 【新】编译错误解析
│   └── tests/                # 【新】单元测试
│       ├── test_preprocess.py
│       ├── test_table_repair.py
│       └── fixtures/         # 测试用 DOCX
│           ├── simple.docx
│           ├── colspan.docx
│           ├── rowspan.docx
│           ├── longtable.docx
│           └── nested.docx
└── templates/
    └── pandoc/
        ├── harryopo-pandoc-template.latex  # 【新】
        └── harryopo-table.lua              # 【新】基于 mathnotes-table.lua 派生
```

---

> **下一步**: 等待用户最终确认后，按阶段 1 → 4 实施。每阶段完成后编译验证 + 更新 MEMORY.md。
