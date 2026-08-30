# 办公超级 Skill 架构方案 v3（2026-08-30 更新）

> **v1**: 2026-08-08（[2026-08-08-office-super-skill.md](./2026-08-08-office-super-skill.md)）
> **v2**: 2026-08-28（[2026-08-28-office-super-skill-v2.md](./2026-08-28-office-super-skill-v2.md)）
> **v3 日期**: 2026-08-30
> **v3 更新动因**: ① 8/29 决策**废弃 TipTap web-editor**（TexLite/web-editor 清理，改 IDE 内 LaTeX Workshop 预览）——v2 的阶段 3 需要重新定义；② 第三轮增量调研完成（[2026-08-30 开源方案增量调研](../research/2026-08-30-开源方案增量调研-文档MCP与生成转换生态.md)，40+ 新项目核验）
> **目标不变**: 生成标准美观的 Word / LaTeX / PDF 并互相转换，内置流程图生成能力
> **范式不变**: AI 产出结构化数据（MD/JSON）→ 模板引擎渲染，绝不直接生成 OOXML/排版代码；Office 自动化只做渲染后操作

---

## 0. v2 → v3 状态盘点（2026-08-30）

### v2 路线图中已完成（8/28–8/29 期间落地）

| v2 条目 | 状态 | 落地 commit/证据 |
|---|---|---|
| markitdown 三级解析路由 | ✅ | `4fd23c0`，office.py 四级：anydoc → MinerU → markitdown → python-docx |
| Word → PDF 直接导出 | ✅ | `4fd23c0`，render_word 的 `export_pdf`（ExportAsFixedFormat） |
| LaTeX → Word 反向链路 | ✅ | `427727e`，.tex → MD 清洗 → Word/PDF（MD 中间态路线验证成功） |
| 模板注册表 v1 | ✅ | `7777731`，manifest.json + CLI，24 项端到端全绿 |
| TinyTeX 环境自包含 | ✅ | `26b4412` + flushend.sty 项目自包含（TEXINPUTS 前缀） |
| 公式乱码根治 | ✅ | 8/29：latex2mathml + Office MML2OMML.XSL 标准链路 + 行内公式 |
| 图表 skill 内嵌 | ✅ | 8/29：diagram-design（39 类型）+ 文档生成主流程固化进 SKILL.md |
| 阶段 3 M1/M2（TipTap web-editor） | ⚠️ **已完成随即废弃** | `744a3aa`/`9c2e492` 后，8/29 清理（IDE 预览取代） |

### v3 的三个结构调整

1. **阶段 3 重新定义**：从"自建 TipTap Web 编辑器"改为 **"IDE 生态 + 轻量核对 + 修订审阅"** 组合（零自建前端）
2. **修订标记从"计划"升级为 P0**：2026 夏季生态的 Word 工具主战场已转向修订/审阅，弹药充足
3. **解析路由保持四级架构不变**，候补档（marker/kreuzberg）按需插入，不重排

---

## 1. 阶段 3（重定义）：IDE 生态 + 轻量核对 + 修订审阅

### 1.1 预览确认环节（取代 web-editor，零自建前端）

```
MD 中间态确认   →  VS Code 内置 MD 预览 / Markdown Preview Enhanced
                   （预览 CSS 配方正字体，贴近最终版式；内置预览已支持 diff 渲染）
LaTeX 编译预览  →  LaTeX Workshop 10.13.1 + latexmk -xelatex recipe
                   （settings.json 模板化分发，TEXINPUTS 指向项目模板）
docx 渲染后核对 →  docx-preview（docxjs，Apache-2.0）静态 HTML 页
                   随生成产物附带，浏览器零后端核对；分页为近似值
权威核对        →  Word COM 导出 PDF（已实现）即为最终版式的权威预览
```

### 1.2 修订审阅（v3 新增，P0）

| 步骤 | 工具 | 说明 |
|---|---|---|
| ① 生成初稿 | md_to_word.py（已有） | AI 产出 MD → Word 引擎渲染 |
| ② 用户修改/批注 | 用户在 Word 中改 | — |
| ③ diff 出红线稿 | **Python-Redlines**（MIT，126★，v0.3.0） | 两份 docx → 原生 w:ins/w:del 修订稿，**不依赖 MS Word**（内嵌 .NET 引擎），结构感知 docxdiff |
| ④ AI 理解修订 | 解析修订 docx（docx-revisions 类）或 word-mcp-live 读批注 | AI 获得用户修改意图 |
| ⑤ 二稿 + 修订记录 | 自研引擎 OOXML 修订输出（蓝本：docx npm 9.7 / SecurityRonin docx-mcp） | 后续迭代 |

**进阶通道（Trial）**：word-mcp-live（MIT，198★）——COM 驱动"打开中"的 Word 做实时 AI 修订会话（原生修订标记 + 逐步撤销 + 线程批注），封装为可替换适配器，不直接绑死。

### 1.3 公文专项校准（Trial，低成本）

用公开国标参数对照校准公文模板（无版权风险，规则自实现）：
- **参数源**：markdown2word 的 `@gov_notice` 模板（MIT）+ markdown-gongwen 导出规则表 + docformat-gui 的体检清单（仅参考规则，**其代码 PolyForm 非商业不可引入**）
- **校准点**：三号仿宋 16pt 正文、28 磅行距、页边距 37/35/28/26mm、方正小标宋/黑体/楷体/仿宋分级、发文字号"〔〕"格式、"—1—"页码
- **生成后自动校对**：把 docformat-gui 的体检项（标点规范/序号风格/禁则换行）做成自实现 lint

---

## 2. 解析端：四级路由 + 候补档（架构不变，弹药入库）

```
输入文件
  → ① anydoc 快检（Rust，毫秒级，14 格式）        【已集成】
  → ② MinerU 深解析（0.2s/页，扫描件/公式/表格）   【已集成，升级 3.4.5】
  → ③ markitdown 兜底（微软官方，20+ 格式）        【已集成，升级 ≥0.1.7：omml 公式修复直接受益】
  → ④ python-docx 回填                            【已集成】
  ── 候补档（按需插入，不改变路由结构）──
     marker 2.0.0（Apache-2.0）   MinerU 速度/许可互补档，输出 MD/JSON/chunks，值得 A/B
     kreuzberg v4（MIT，Rust 核）  .doc/.xls/.ppt 老格式补档（①-④ 均不覆盖 .doc）
     Citra（MIT，905★）           解析验证层：提取结果回溯原始页码坐标（证据回溯/质检）
     docling v2.123（MIT）        复杂文档互为兜底（v2 P1 遗留，~1GB 模型按需）
```

**升级动作（P0，半小时级）**：`pip install -U markitdown[docx,pptx,xlsx]` 到 ≥0.1.7（2026-07-29 修复公式 LaTeX 宏/SVG/omml 模板 bug）+ MinerU 升 3.4.5（Unicode 修复）。

---

## 3. LaTeX 链路增强（小步快跑）

| 项 | 来源 | 动作 |
|---|---|---|
| .tex 预检 lint | overleaf-mcp 的 7 项静态检查 | 移植规则为 XeLaTeX 编译前 lint（数学括号/表格列数/悬空引用），并入 harryopo-build-mcp |
| harryopo-build-mcp（v2 遗留） | — | 维持 v2 决策：MCP 包装 build.ps1（编译→日志解析→错误定位→修复建议闭环），预检 lint 一并纳入 |
| IDE 配置模板化 | LaTeX Workshop 实践（8/29 已跑通） | settings.json（latexmk xelatex recipe + TEXINPUTS）+ 方正预览 CSS 打包进模板注册表分发 |

---

## 4. PPT / Excel 输出（v3 正式立项，此前为空白）

生态成熟度已够（多个同栈 Python+COM 参考实现），**范式仍然守铁律**：AI 产 JSON/MD 结构化数据 → 引擎/MCP 渲染。

| 路线 | 参考项目 | 说明 |
|---|---|---|
| COM 路线（Windows 本机） | ykuwai/ppt-mcp（156 工具）、trsdn/mcp-server-ppt、dosev-ai wordmcp/pptmcp/excelmcp | 与我们 Word 引擎同环境；Output Contract（机器可验证输出规格）范式优先移植 |
| 模板引擎路线 | Carbone（JSON→pptx/xlsx，~10ms/份；**CCL 许可**仅参考 API 设计） | 跨平台备选 |
| 优先级建议 | 先 PPT 后 Excel | PPT 与现有 diagram/chart 能力协同更强 |

---

## 5. 目标架构总览（v3）

```
┌─────────────────────────────────────────────────────────────────┐
│ 用户层：自然语言 + 用户模板（Word/LaTeX）+ 任意输入文件             │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ ① 生成层：AI 产 MD/JSON（受模板 schema 约束）                     │
│    解析入口：anydoc → MinerU → markitdown → python-docx          │
│    候补：marker / kreuzberg / docling / Citra（验证层）           │
│    图表：diagram-design(39类) + super-diagram + mermaid + TikZ   │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ ② 编辑/确认层（v3 重定义，零自建前端）                            │
│    MD 确认：VS Code 预览 + 方正 CSS ｜ LaTeX：LaTeX Workshop     │
│    docx 核对：docx-preview 静态 HTML ｜ 权威：Word COM 出 PDF    │
│    修订审阅：Python-Redlines 红线稿 → AI 理解 → 二稿             │
│    （进阶：word-mcp-live COM 实时修订会话）                       │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ ③ 输出层：Word(md_to_word+docxtpl) / PDF(XeLaTeX harryopo+COM)  │
│    PPT/Excel：COM 路线（v3 立项）｜ 互转：Pandoc 中枢+COM 兜底    │
│    后处理：pdfcpu（P2）｜ 编译诊断：harryopo-build-mcp + 预检lint │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 分阶段路线图（v3）

### P0（本周，1-2 天级动作）
- [ ] markitdown 升级 ≥0.1.7 + MinerU 升 3.4.5（解析质量直接受益）
- [ ] **Python-Redlines 接入**：生成版 vs 用户修改版 → 红线稿 diff（修订审阅 MVP）
- [ ] docx-preview 静态核对页：office.py 渲染 Word 后附带 `output.docx.html` 核对页

### P1（2 周内）
- [ ] GB/T 9704 公文参数校准（markdown2word/markdown-gongwen 规则对照）+ 公文格式 lint
- [ ] harryopo-build-mcp + overleaf-mcp 7 项静态检查移植（编译诊断闭环）
- [ ] marker 2.0.0 A/B（对 MinerU，跑自有文档集）；kreuzberg 补 .doc/.xls/.ppt 档
- [ ] docx npm 9.7 修订 OOXML 结构评估 → 自研引擎修订输出（二稿带修订记录）
- [ ] docling 接入决策（v2 遗留：跑复杂文档对比，质量达标才入库）

### P2（1 个月内）
- [ ] PPT 输出链路（Output Contract 范式 + COM 参考实现）
- [ ] word-mcp-live 适配器封装（实时修订会话进阶通道）
- [ ] Citra 证据回溯验证层（MinerU 提取质检 + 页级引用展示）
- [ ] 模板注册表 v2：brand-docs 的 Profile 抽取思路（样式保真校验）
- [ ] IDE 配置模板化分发（LaTeX Workshop recipe + 预览 CSS 进注册表）

### P3（长期储备，维持 v2）
- [ ] Typst 0.15 第三输出通道（MathML/PDF/A 新能力提升其储备价值）
- [ ] 模板市场 + 多人协作 + 版本审计；pdfcpu 后处理工具箱
- [ ] HermesOffice 字节保真往返跟踪（Word 往返编辑的对标方向）

---

## 7. 集成决策速查（v3 增量）

| 决策 | 项目 | 等级 | 动作 |
|---|---|---|---|
| **Adopt** | Python-Redlines | P0 | 修订审阅 MVP 依赖 |
| **Adopt** | markitdown ≥0.1.7 / MinerU 3.4.5 升级 | P0 | 现有依赖升级 |
| **Adopt** | docx-preview（docxjs） | P0 | 渲染后核对静态页 |
| **Trial** | marker 2.0.0 / kreuzberg v4 | P1 | 解析候补档 A/B |
| **Trial** | word-mcp-live | P1 | 实时修订会话（适配器封装） |
| **Trial** | docx npm 9.7 修订结构 | P1 | 自研修订输出的 OOXML 蓝本 |
| **Trial** | GB/T 9704 参数校准集 | P1 | 公文模板对照（规则自实现） |
| **Trial** | overleaf-mcp 静态检查 | P1 | .tex 预检 lint 移植 |
| **Trial** | dosev/ykuwai PPT MCP 族 | P2 | PPT 输出蓝图（Output Contract） |
| **Assess** | Citra / brand-docs / docling / Typst 0.15 | P2-P3 | 按需评估 |
| **Hold** | SuperDoc / pullmd / O2OA | — | AGPL 传染风险 |
| **Hold** | kimi-skills / ComPDFKit / OfficeDoc / docformat-gui(代码) | — | 许可缺失/不透明/非商业 |

**红线不变**：所有集成守住"AI 只产结构化数据 → 模板引擎渲染"；Office MCP/COM 自动化只做渲染后操作与审阅辅助，绝不回到"AI 直接改文档二进制"。

---

## 8. 风险清单（v3 增补）

1. **Python-Redlines 依赖内嵌 .NET 二进制**：跨机器分发需验证 Windows 环境兼容性；作为依赖引入时锁定版本
2. **docx-preview 分页为近似值**：核对页必须标注"以导出 PDF 为准"，避免用户误判版式
3. **word-mcp-live 成熟度**（2026-02 创建，198★）：封装为可替换适配器，不绑死 COM 会话
4. **PPT/Excel COM 自动化的稳定性**：参考项目多为单人维护，Output Contract 先行、COM 调用充分隔离
5. **marker/kreuzberg 引入新依赖体积**：kreuzberg Rust 核需 wheel 可用性验证（Windows）
6. v2 遗留风险全部维持（解析器分工漂移 / docling 体积 / WASM CJK 弱 / 许可合规）

---

## 附：调研报告索引

| 报告 | 日期 | 覆盖 |
|---|---|---|
| v1 调研（ai-office-generation 等 3 篇） | 08-08 | 全景 |
| v2 调研（tex64/markitdown/docling/LaTeX-MCP） | 08-28 | 13+ 项目 |
| **v3 增量调研（文档 MCP 生态 × 生成转换 × 中文公文与预览）** | **08-30** | **40+ 新项目**：[2026-08-30-开源方案增量调研-文档MCP与生成转换生态.md](../research/2026-08-30-开源方案增量调研-文档MCP与生成转换生态.md) |

> **方案状态**: v3 已整合增量调研与阶段 3 重定义；下一步从 P0 三项（升级 markitdown/MinerU、Python-Redlines、docx-preview 核对页）开始。
