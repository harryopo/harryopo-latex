# harryopo-latex Skill 扩展方案 v2：MinerU + LLM + 可选 Web 三层架构

> **方案日期**: 2026-08-05（v2 修订）
> **修订原因**: 用户反馈 v1 方案过于保守——排除 MinerU 是错的（已开源 Apache 2.0）、LLM 只填参数太弱、未考虑 Web 可视化价值
> **核心转变**: 从"纯脚本极简方案"改为"MinerU 解析 + LLM 智能修复 + 可选 Web 可视化"的真正折中方案
> **关联调研**: [Word-Markdown-to-LaTeX-开源方案深度调研报告.md](./Word-Markdown-to-LaTeX-开源方案深度调研报告.md)
> **v1 方案**: [2026-08-05-harryopo-latex-skill-extension.md](./2026-08-05-harryopo-latex-skill-extension.md)（已归档，被本文件取代）

---

## 1. v1 → v2 的关键修正

| 维度 | v1 方案（错误） | v2 方案（修正） |
|------|---------------|---------------|
| **文档解析** | 自写 XML 解析（重复造轮子） | **MinerU**（业界 SOTA，开源 Apache 2.0） |
| **LLM 角色** | 仅填参数（太弱） | **填参数 + 表格修复 + 内容确认 + 编译纠错** |
| **可视化** | 只靠 MD 中间态 | **MD 中间态 + 可选轻量 Web 预览器** |
| **表格处理** | 自写 L0-L4 分级 | **MinerU 输出 HTML 表格 + LLM 修复 + LaTeX 渲染** |
| **公式处理** | 假设 MD 已含 LaTeX | **MinerU 自动识别公式转 LaTeX（SOTA 精度）** |
| **加粗映射** | `\textbf{}`（中文加粗会糊） | **`\fzht{}` 黑体**（中国学术排版规范，已修复 convert.py） |

---

## 1.5 补充调研：docx2tex (transpect)

> 用户反馈的另一开源方案，经核实后定位为**备选方案**。

| 维度 | 实际数据 |
|------|---------|
| GitHub | [transpect/docx2tex](https://github.com/transpect/docx2tex)，**584 stars** |
| 最近提交 | 2025-07-24（活跃维护） |
| Commits | 1,279（成熟项目） |
| 架构 | DOCX → Hub XML → LaTeX（三层 XSLT 管线） |
| 依赖 | **Java 13+**（重要限制） |
| 表格 | 三种模型：tabularx / tabular / htmltabs，支持跨页 |
| 公式 | MathType OLE + Word OMML，准确率号称 99.5% |
| 配置 | CSV（新手）+ XML（高级） |
| 中文 | 需额外配置 xeCJK/ctex |

**客观评价**：
- ✅ 直接输出 LaTeX（MinerU 输出 MD 需二次转换）
- ✅ 专业出版社级精度，CSV/XML 双配置灵活
- ❌ **需要 Java 13+**（新手门槛过高）
- ❌ **584 stars vs MinerU 69.7k**——生态差距悬殊
- ❌ 中文非原生，需要手写 XML 配置
- ❌ 学习曲线陡（要懂 XSLT/XProc）

**最终定位**：**备选方案**，仅当用户有 Java 环境 + 需要出版社级精细控制时推荐。主线走 MinerU。

**工具选型对比**：
| 场景 | 推荐 | 理由 |
|------|------|------|
| 主线（90% 用户） | **MinerU** | 一键装、本地跑、DOCX 原生、公式 SOTA、Apache 2.0 |
| Pandoc 兜底 | Pandoc | 已集成，math-notes 路径继续用 |
| 出版社专业场景 | docx2tex | 备选，需 Java + XSLT 知识 |

---

## 1.6 加粗映射规则（2026-08-05 修正）

**背景**：用户指出"MD 经常出现加粗，但 PDF 没必要，直接用黑体即可"——这是中国学术排版的正确惯例。

**原因**：
- 中文字体加粗后笔画会糊（方正书宋加粗后尤其难看）
- 中文学术规范里强调用**黑体**而不是 bold
- MD 里的 `**加粗**` 只是因为纯文本没别的突出手段，到了 LaTeX 应回归黑体

**已修改的代码**（[convert.py](file:///d:/ai/latex/.trae/skills/harryopo-latex/scripts/convert.py)）：
- 行 227-228：`**xxx**` → `\fzht{xxx}`（原 `\textbf{xxx}`）
- 行 226：`***xxx***` → `\fzht{xxx}`（粗斜体统一走黑体，中文无斜体概念）
- 行 467：表头 `\textbf{}` → `\fzht{}`（表头也用黑体）
- 行 688：DOCX 粗斜体简化为加粗分支

**保留 `\textit{}`**：斜体在英文场景仍有意义（书名、变量名），所以 `*xxx*` 保留转 `\textit{}`。

---

## 2. MinerU 能力确认（2026-08-05 核实）

| 维度 | 数据 |
|------|------|
| 许可证 | MinerU 开源许可证（Apache 2.0 基础），中小企业商用免授权 |
| GitHub | 69.7k stars，5712 commits，最近提交 2026-07-10 |
| 最新版 | 3.4.0（2026-06-18），PP-OCRv6，OCR 速度翻倍 |
| 输入 | PDF / 图片 / **DOCX 原生** / PPTX / XLSX |
| 输出 | Markdown + JSON + 图片 + LaTeX 公式 + HTML 表格 |
| 公式精度 | OmniDocBench v1.6 评分 95.69（SOTA，超 Gemini 3 Pro） |
| 表格能力 | HTML 输出，跨页表格合并，合并单元格还原 |
| 部署 | `pip install mineru`，pipeline 后端纯 CPU 可跑（16GB 内存） |
| MCP | 官方 MCP Server，已集成 Cursor/Claude Desktop |
| 首次下载 | 模型约 2-3GB（自动缓存） |

**关键**：MinerU 已原生支持 DOCX，无需先转 PDF，速度快 10 倍，无幻觉。

---

## 3. 三层架构（v2 核心）

```
┌────────────────────────────────────────────────────────────────┐
│ 用户上传 .docx / .pdf / .md / 图片                               │
└──────────────────────┬─────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 【第一层】MinerU 智能解析                                        │
│  ├── DOCX/PDF/图片 → Markdown + LaTeX 公式 + HTML 表格           │
│  ├── pipeline 后端（CPU 可跑）/ vlm 后端（GPU 高精度）            │
│  ├── 公式：SOTA 精度，直接输出 LaTeX                            │
│  ├── 表格：HTML 格式，保留合并/跨页结构                          │
│  └── 通过 MCP Server 或 CLI 调用                                │
└──────────────────────┬─────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 【第二层】LLM 智能转换引擎                                       │
│  ├── 角色A：意图理解 → 选模板（paper/report/notes）+ 填参数      │
│  ├── 角色B：表格修复 → HTML 表格 → LaTeX tabular/multirow        │
│  │   └── LLM 看 MinerU 输出的 HTML 表格，生成对应 LaTeX 代码     │
│  ├── 角色C：内容确认 → 展示 MD 中间态，提问用户确认              │
│  ├── 角色D：编译纠错 → 读 .log → 修复 LaTeX 错误                │
│  └── 由 harryopo-latex skill 编排（已有）                       │
└──────────────────────┬─────────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ 【第三层】LaTeX 渲染 + 可视化反馈                                │
│  ├── 编译：build.ps1（xelatex × 3）→ PDF                        │
│  ├── 【可选】Web 预览器：单页 HTML 或本地 Next.js                │
│  │   ├── 双栏：MD 源码 | PDF 预览                                │
│  │   ├── 表格结构可视化（高亮合并单元格）                        │
│  │   └── 编译错误标注（红波浪线）                                │
│  └── 【默认】直接在 AI IDE 对话里展示结果                        │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. LLM 的四个实质角色

### 角色A：意图理解 + 参数填充（轻量）
- 理解用户需求："我要把这份 Word 转成双栏论文"
- 选择模板：paper / report / math-notes
- 填充 CLI 参数：`--type paper --twocolumn --author "张三"`
- **不需要看文档内容**，只看用户的话

### 角色B：表格修复（核心新增）
MinerU 输出 HTML 表格，但 HTML → LaTeX 不是 1:1 映射：
```html
<!-- MinerU 输出 -->
<table>
  <tr><td rowspan="2">合并</td><td>A</td></tr>
  <tr><td>B</td></tr>
</table>
```
LLM 任务：看 HTML → 生成正确的 LaTeX：
```latex
\begin{tabular}{l l}
  \multirow{2}{*}{合并} & A \\
   & B \\
\end{tabular}
```
**为什么需要 LLM**：规则引擎处理 rowspan + colspan 组合容易出错，LLM 能理解语义。已有 convert.py 的表格分级作为兜底。

### 角色C：内容确认（新手友好的关键）
- MinerU 输出 MD 后，LLM 不是直接转换，而是：
  - "我解析到 3 个表格、2 个公式、5 张图片，标题是《XXX》，对吗？"
  - "表格 2 有合并单元格，我建议用 multirow 处理，可以吗？"
  - "图 3 的 caption 是'实验结果'，要保留吗？"
- **让用户在 MD 中间态确认，而不是转换完才发现问题**

### 角色D：编译纠错（闭环）
- xelatex 失败时，读 .log
- LLM 解析错误 → 建议修复 → 自动应用或提问用户
- 例："Overfull \hbox 23pt at line 142 → 表格列宽超了，建议把 p{5cm} 改成 p{4cm}"

---

## 5. 表格处理：MinerU + LLM + 脚本三层兜底

```
MinerU HTML 表格
      ▼
┌─────────────────────────────────────┐
│ table_classify.py 【新增脚本】       │
│  ├── 简单表 → convert.py 直转       │
│  ├── 合并表 → 打包给 LLM 修复       │
│  └── 嵌套表 → 占位符 + 手工模板     │
└──────────────────────┬──────────────┘
                       ▼
┌─────────────────────────────────────┐
│ LLM 修复（仅对合并表）               │
│  ├── 输入：HTML + 上下文            │
│  ├── 输出：LaTeX tabular 代码       │
│  └── 校验：括号匹配、列数一致       │
└──────────────────────┬──────────────┘
                       ▼
┌─────────────────────────────────────┐
│ convert.py 渲染 【扩展】             │
│  ├── 插入 \\multirow/\\multicolumn  │
│  ├── 加 booktabs 三线表             │
│  └── caption 下置                   │
└─────────────────────────────────────┘
```

---

## 6. 可选 Web 预览器（新手友好的可视化）

### 6.1 何时做 Web 层

**默认形态**：不做 Web，全在 AI IDE 里跑（Skill 形态）。

**触发做 Web 的条件**（满足任一就做）：
- 用户明确说"我要可视化界面"
- 表格修复需要用户交互式编辑（拖拽合并单元格）
- 要分享给不会用 AI IDE 的人

### 6.2 Web 预览器设计（轻量）

**方案A：单页 HTML（零依赖，最轻）**
- 一个 `preview.html`，浏览器直接打开
- 左栏：Markdown 源码（contenteditable）
- 右栏：PDF 预览（iframe 或 embed）
- 用 LaTeX.js 做实时渲染
- 通过 `file://` 协议加载，无需服务器

**方案B：本地 Next.js（中等成本）**
- Next.js + react-pdf 或 iframe
- 表格编辑器：可视化合并/拆分单元格
- 编译错误红波浪线（Monaco Editor）
- 仅本地运行，`npm run dev` 启动

**方案C：完整工作台（重，不推荐除非必要）**
- 类似迷你 Overleaf
- 文件管理、多标签、协作
- 开发维护成本最高

**推荐**：先做方案A（单页 HTML），不够再升级方案B。

### 6.3 单页 HTML 预览器骨架

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>harryopo LaTeX 预览</title>
  <script src="https://cdn.jsdelivr.net/npm/latex.js/dist/latex.js"></script>
  <style>
    body { display: flex; height: 100vh; margin: 0; font-family: sans-serif; }
    #editor { width: 50%; padding: 1rem; border-right: 1px solid #ddd; overflow: auto; }
    #preview { width: 50%; padding: 1rem; overflow: auto; }
    table { border-collapse: collapse; margin: 1rem 0; }
    td, th { border: 1px solid #999; padding: 0.5rem; }
  </style>
</head>
<body>
  <div id="editor" contenteditable="true">
    <!-- 用户 MD 或 LaTeX 源码粘贴这里 -->
  </div>
  <div id="preview">
    <!-- LaTeX.js 渲染结果 -->
  </div>
  <script>
    // 简单实时渲染
    const editor = document.getElementById('editor');
    const preview = document.getElementById('preview');
    editor.addEventListener('input', () => {
      // 把 LaTeX 源码交给 LaTeX.js 渲染
      // 实际实现需要更多胶水代码
    });
  </script>
</body>
</html>
```

---

## 7. 实施路线（v2）

### 阶段 1：MinerU 集成（最高价值）
**交付**：
- `mineru_cli.py`：封装 MinerU 调用（DOCX/PDF → MD + JSON + 图片）
- 环境检查：`pip install mineru`，首次下载模型
- 测试 5 种 DOCX：简单、公式、表格、合并表、扫描件

**验收**：
- MinerU 能解析用户提供的真实 DOCX
- 输出 MD 含正确的 LaTeX 公式和 HTML 表格
- 模型缓存到本地，二次调用无需重下

### 阶段 2：LLM 表格修复 + convert.py 扩展
**交付**：
- `table_classify.py`：表格分级（简单/合并/嵌套）
- SKILL.md 新增 LLM 表格修复 prompt 模板
- convert.py 新增 multirow/longtable 分支

**验收**：
- MinerU HTML 表格 → LLM → 正确 LaTeX（合并表 90%+ 准确）
- 简单表走脚本直转（不耗 LLM）
- 嵌套表输出占位符

### 阶段 3：LLM 内容确认 + 编译纠错
**交付**：
- SKILL.md 新增"内容确认对话"流程
- `log_parser.py`：解析 xelatex .log
- SKILL.md 新增编译纠错 prompt

**验收**：
- 转换前 LLM 会和用户确认表格/公式/图片
- 编译失败时 LLM 能读 .log 给修复建议

### 阶段 4：【可选】Web 预览器
**交付**：
- 单页 HTML 预览器
- LaTeX.js 实时渲染

**验收**：
- 浏览器打开即用，双栏显示
- 用户可直接编辑 MD/LaTeX

### 阶段 5：文档与沉淀
**交付**：
- SKILL.md 完整更新
- MEMORY.md 更新
- 表格处理 FAQ

---

## 8. 与现有资产的关系（v2）

| 现有资产 | v2 处理 |
|---------|---------|
| `convert.py`（870行） | **保留并扩展**，新增表格分级分支 |
| `md2latex.py` | **保留**，MinerU 输出 MD 后走这个 |
| `mathnotes-table.lua` | **保留**，math-notes 路径继续用 |
| `harryopo-base.sty/paper.cls/report.cls` | **不动**（CLAUDE.md 硬规则） |
| `build.ps1` | **不动** |
| `math-notes` 独立体系 | **不碰** |
| `SKILL.md` | **大更新**，加入 MinerU + LLM 四角色 |

**新增**：
- `mineru_cli.py`：MinerU 封装
- `table_classify.py`：表格分级
- `log_parser.py`：编译日志解析
- `preview.html`（可选）：Web 预览器

---

## 9. 不做的事（v2 边界）

- ❌ **不自己写 DOCX XML 解析**（MinerU 已做得最好，不自造轮子）
- ❌ **不让 LLM 生成完整 LaTeX 文档**（只做表格修复和纠错，文档骨架走脚本）
- ❌ **不强求自动转嵌套表 L4**（行业无解，输出占位）
- ❌ **不碰 math-notes 独立体系**（CLAUDE.md 硬规则）
- ❌ **默认不做完整 Web 工作台**（除非用户明确要可视化交互）

---

## 10. 环境要求（v2）

### 必需
- Python 3.10-3.13
- xelatex（TeX Live 2024+）
- Pandoc 3.x（可选，math-notes 路径用）
- **MinerU**：`pip install mineru`（首次下载模型 2-3GB）
- 磁盘：模型缓存 ~5GB

### 可选
- GPU（vlm 后端高精度，4GB VRAM 起步）
- Node.js（仅做 Web 预览器时）

### 字体
- 已内嵌 `templates/fonts/`，无需额外安装

---

## 11. 风险与缓解（v2）

| 风险 | 缓解 |
|------|------|
| MinerU 模型下载慢/失败 | 用 ModelScope 镜像（`HF_ENDPOINT=https://hf-mirror.com`） |
| MinerU CPU 模式慢 | 接受 5-10 秒/页；或用户有 GPU 走 vlm 后端 |
| LLM 表格修复偶尔出错 | convert.py 的分级脚本做兜底校验 |
| LLM API 成本 | 仅对合并表调 LLM，简单表走脚本；默认用便宜模型 |
| MinerU 版本更新 breaking | 锁定版本，升级走测试流程 |

---

## 12. 成本估算

| 项目 | 一次性 | 持续 |
|------|--------|------|
| MinerU 模型下载 | 2-3GB 流量 | 0（缓存） |
| LLM 表格修复 | 0 | ~$0.001/表（便宜模型） |
| 磁盘占用 | ~5GB（模型+字体+模板） | 0 |
| GPU（可选） | 0（用 CPU 也行） | 0 |

**结论**：成本极低，MinerU 本地跑不花钱，LLM 只在表格修复时少量调用。

---

> **下一步**: 用户确认 v2 方向后，从阶段 1（MinerU 集成）开始实施。
