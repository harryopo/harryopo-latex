# harryopo — 办公文档 AI 生产力平台

> 生成**标准美观**的 Word / LaTeX / PDF，三者互相转换，内置流程图/架构图生成能力。
> 核心范式：**AI 只产出结构化数据（Markdown/JSON）→ 模板引擎保真渲染**——绝不让 AI 直接生成 .docx/.pdf 二进制。

---

## 核心能力

| 能力 | 说明 | 入口 |
|------|------|------|
| **MD → Word** | 公文/学术 .docx：方正/开源字体一键切换、原生自动目录、OMML 数学公式、三线表、图注表注在下方 | `office.py render x.md --format word` |
| **MD → LaTeX → PDF** | 论文（单/双栏）/ 报告 / 数理笔记 / 公文风格，XeLaTeX + 方正字体 + XITS 数学 | `office.py render x.md --format paper [--type report]` |
| **文档 → MD 解析** | 四级解析路由：anydoc（Rust 毫秒级快检）→ MinerU（扫描件/公式深解析）→ markitdown（微软官方 20+ 格式兜底）→ python-docx 回填 | `office.py render 任意文档` |
| **反向转换** | Word → MD（清洗）；LaTeX → Word/PDF（.tex → MD 清洗 → 双渲染器）；Word → PDF 直接导出（COM） | 同上 |
| **内置图表** | super-diagram 契约（架构图/时序图，AI 算坐标代码渲染）+ Mermaid + diagram-design（39 类型编辑级图表）+ TikZ | MD 中写 ` ```super-diagram ` / ` ```mermaid ` 块 |
| **模板注册表** | 用户 Word 模板入库 → 自动提取 schema → AI 产 data.json → docxtpl 保真填充 | `office.py template ...` |

## 快速开始

```bash
# 0) 依赖（Windows + Python 3.10+）
pip install python-docx latex2mathml pywin32 markitdown anydoc playwright
python -m playwright install chromium   # 图表 PNG 导出
# LaTeX：TinyTeX 或 TeX Live（需 xelatex + ctex + booktabs + flushend）

# 1) 一键渲染：一份 Markdown 同时产出 Word + PDF（含图表自动渲染）
python .trae/skills/harryopo-office/scripts/office.py render 我的文档.md --format all

# 2) 报告类型（章节式封面+目录）
python .trae/skills/harryopo-office/scripts/office.py render 报告.md --format all --type report

# 3) 在 MD 里写架构图（AI/人写 JSON 契约，渲染管线自动出图）
#    ```super-diagram
#    {"type":"architecture","canvas":{"width":960,"height":560,"theme":"light"},
#     "title":"图1：系统架构","nodes":[...],"edges":[...]}
#    ```
```

**Markdown 写作约定**：`#` 主标题 / `##` 一、级 / `> 作者：`元信息 blockquote / `> **表1：**`表标题（渲染在表格下方）/ `> 注：`注释（表格/图片下方）/ `$$...$$` 公式（Word 转 OMML 原生公式）/ `![图1：xxx](figures/x.png)` 图片。

完整工作流（含"内容 → 预览确认 → 配图建议 → 生成 → 插入 → 渲染"主流程）见 **[SKILL.md](.trae/skills/harryopo-office/SKILL.md)**。

## 示例产物

见 **[output/examples/](output/examples/README.md)**：论文单栏/双栏/全特性、报告/报告全特性，五份示例 Word + PDF + LaTeX 三格式齐全，全特性示例含 super-diagram 架构图与 Mermaid 流程图。

| 示例 | 亮点 |
|------|------|
| paper-showcase | 论文全特性：多列表格、算法伪代码、公式、参考文献 + **super-diagram 系统架构图** |
| report-showcase | 章节式报告：封面/目录/三线表 + **四层架构图 + Mermaid 流程图** + 表注规范 |

## 目录结构

```
├── .trae/skills/harryopo-office/   # 核心 Skill（SKILL.md + scripts + 内嵌模板）
│   ├── scripts/                    #   office.py 主入口 / convert.py / diagram_render.py ...
│   │   └── word/                   #   Word 模板引擎（md_to_word + docxtpl 子 skill）
│   ├── skills/diagram-design/      #   编辑级图表规范（39 类型）
│   └── templates/                  #   自包含 LaTeX 模板（cls + fonts + build.ps1）
├── templates/                      # 项目根 LaTeX 模板体系（base.sty + paper/report.cls）
├── templates/math-notes/           # 数理笔记独立体系
├── shared/diagram_geometry.py      # 图表质量校验共享库（边穿节点/重叠/端口扇出）
├── output/examples/                # 官方示例产物（Word/PDF/LaTeX 三格式）
├── docs/plans/                     # 实施方案（最新：2026-08-30-office-super-skill-v3.md）
├── docs/research/                  # 调研报告（开源方案/差距诊断/图表研究）
├── 蒸馏区/                          # 参赛作品说明书模板蒸馏子项目
└── memory/CLAUDE.md                # Agent 协作规则与踩坑警示（30+ 条）
```

## 技术栈

XeLaTeX（ctex + xeCJK + 方正字体 + XITS Math）｜python-docx + docxtpl（Word 引擎）｜anydoc / MinerU / markitdown（解析三级路由）｜super-diagram / Mermaid / diagram-design（图表）｜MS Office COM（目录刷新、PDF 导出）｜playwright（图表 PNG）

## 文档

- **开发方案书 v3**：[docs/plans/2026-08-30-office-super-skill-v3.md](docs/plans/2026-08-30-office-super-skill-v3.md)（阶段路线图 + 集成决策）
- **增量调研**：[docs/research/2026-08-30-开源方案增量调研-文档MCP与生成转换生态.md](docs/research/2026-08-30-开源方案增量调研-文档MCP与生成转换生态.md)
- **Agent 规则与踩坑**：[CLAUDE.md](CLAUDE.md)、[memory/MEMORY.md](memory/MEMORY.md)

## 说明

- 方正字体为商用授权字体，仅限已获授权的环境使用；开源场景切换 `--config opensource`（系统字体方案）
- `简历/`、`opensource-reference/`、`output/`（examples 除外）不入库
- 平台目标平台：Windows（Word 链路依赖本机 MS Office COM）；LaTeX/PDF 链路跨平台
