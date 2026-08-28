# TexLite / Oleafly 轻量本地实时编辑方案调研报告

> **日期**: 2026-08-28
> **调研目标**: 找到"轻量、本地、可预览、实时编辑"的开源方案，可改造进 harryopo 办公平台（阶段 2 本地预览服务器 + 阶段 3 Web 编辑器）
> **调研方式**: skill_agent_deep-research-ultra 深度调研 + README 实证 + 双项目源码全量分析（已 clone 至 `opensource-reference/`）
> **源码版本**: TexLite v0.8.1（AGPL-3.0）· Oleafly v0.3.12（AGPL-3.0-or-later）

---

## 0. 结论摘要（TL;DR）

| 项目 | 形态 | 技术栈 | 与本项目契合度 | 推荐 |
|---|---|---|---|---|
| **TexLite** | Web 工作区（localhost:3000） | Node24 + Fastify + SQLite + React + CodeMirror6 + Yjs + pdfjs | **极高**：默认引擎就是 xelatex；方正字体零改核心；模板/MD 中间态可改造 | ⭐⭐⭐ 主改造对象 |
| **Oleafly** | Tauri 桌面应用 | Rust + React + CodeMirror6 + TipTap3 + pdfjs | 中高：引擎 descriptor 模式/模板体系/MCP 思路可借鉴；桌面形态不宜嵌入 Web 链路 | ⭐⭐ 参考蓝本 |

**核心结论**：**TexLite 就是方案书阶段 2/3 的现成蓝本**（编译队列 + 快照隔离 + 增量缓存 + Yjs 协同 + PDF 预览 + SyncTeX 全都有，37 个测试），远超"自研 ~500 行核心"的 ROI；Oleafly 的**引擎能力描述符（EngineDescriptor）、模板 gallery 契约、MCP 驱动**设计可借鉴。两者均为 AGPL，内部平台自用无碍。

---

## 1. 项目实证画像

### 1.1 TexLite（西南财经大学数据库组）

- **定位**：轻量 local-first LaTeX Web 工作区，写/编译/预览/讨论，面向单服务器小群信任用户，**复用宿主机 LaTeX 安装**（不打包容器）
- **技术栈**：Node.js 24+ · Fastify 5 · better-sqlite3（WAL）· React 19 + Vite · **CodeMirror 6** · **Yjs 13 协同**（+ y-indexeddb 离线缓冲）· pdfjs-dist 6（Range 字节流）· tex-fmt WASM 格式化 · bibtex-tidy · PM2 进程管理
- **编译链路**（`compiler.ts` + `routes/compile.ts`）：
  - latexmk 命令：`-xelatex|-pdf|-lualatex -norc -interaction=nonstopmode -file-line-error -halt-on-error -synctex=1 -no-shell-escape -outdir=<增量缓存>`（默认 `-norc`，项目 latexmkrc 需显式 `-r` 加载——安全设计）
  - **双层调度**：全局并发池（maxCompileJobs:10）+ 按 project+root 键的编译协调器（同目标 1 active + 1 pending，generation 指纹合并/覆盖请求）
  - **快照隔离**：编译前复制不可变源快照（SHA-256 revision），编辑继续不受影响；增量缓存复用 latexmk 依赖数据库（同 root 不同引擎自动清理）
  - **跳过优化**：revision 相同 + 缓存存在 → `skipped` 不重编
- **实时编辑**：**Yjs 协同编辑是实时多用户**（WebSocket 状态广播 + awareness 光标 + Undo 跨会话）；编译为**手动触发**（Ctrl+S 或按钮），非输入防抖自动编译
- **预览**：编译状态写入 Yjs meta（queued/running/succeeded/failed 广播给所有协作者），完成推送版本化 pdfUrl（`?run=<runId>` + ETag + 206 Range），**旧 PDF 保留到新版就绪**；SyncTeX 双向跳转
- **配置**：`texlite.config.json`（defaultEngine=`xelatex`、allowedEngines、maxCompileJobs、PDF loadingStrategy 等全量校验）
- **部署**：`npm i -g texlite && texlite init && texlite start`，默认绑定 127.0.0.1:3000，单进程（无 cluster）

### 1.2 Oleafly

- **定位**：本地优先（local-first）完整研究工具链**桌面应用**——写/编译/校对/文献/引用/图/PDF 审阅/Git/AI；**无实时多人浏览器编辑**（Git 为协作路径）
- **技术栈**：Tauri 2 + Rust（4 crates）+ pnpm monorepo（13 包）+ React 19 + CodeMirror 6 + **TipTap 3（WYSIWYG）** + pdfjs 6.2 + KaTeX + React Flow + hunspell/harper
- **引擎管理**（`document_engine.rs`）：**EngineDescriptor 契约**（produces_pdf/supports_synctex/allow_shell_escape 等能力矩阵），前端以 descriptor 为唯一事实源；Tectonic 默认（XeTeX 内核）+ latexmk 多引擎 + Typst；`detect_latexmk_flavor` 自动识别 fontspec/unicode-math → XeLaTeX（**缺 ctex 检测，加一行即补**）；`% !TeX program=` magic comment 优先；TinyTeX 按需安装（SHA-256 + member 清单验证）
- **预览**：pdfjs 6 完整查看器（虚拟化滚动/双页/反色/搜索）+ **revision 匹配才接受**、失败不清除旧 PDF、二进制 IPC 传 PDF；自研 `.synctex.gz` 解析器（不依赖 synctex 二进制，patience diff 处理编辑偏移）
- **编辑器**：CodeMirror 6 代码视图（LaTeX mask + 项目级索引/引用检查/内联 KaTeX 预览）+ TipTap 3 WYSIWYG（unified-latex 双向解析，RawBlock 保留复杂片段）+ `@codemirror/merge` AI 变更 diff
- **AI**：内置 Copilot（20+ 工具，diff 先行审批）+ **MCP server**（axum 绑定 127.0.0.1:5323，Claude/Codex/Cursor 可驱动打开的项目）
- **模板体系**：`resources/templates/` 24+ 模板（目录 + main.tex + template.json + preview.png），画廊/引擎过滤自动生效——**新增 harryopo 中文模板只需加一个目录**

---

## 2. 与 harryopo 需求匹配度评估

| 需求 | TexLite | Oleafly | 说明 |
|---|---|---|---|
| **轻量** | ✅ npm 单包 + SQLite，无 Docker | ⚠️ Tauri 桌面 + Rust 构建重 | TexLite 明显更轻 |
| **本地** | ✅ localhost:3000，数据在 XDG 目录 | ✅ 项目=普通文件夹 | 都满足 |
| **可预览** | ✅ pdfjs + SyncTeX + 旧 PDF 保留 | ✅ pdfjs 完整查看器 + 分离窗口 | 都满足 |
| **实时编辑** | ✅ Yjs 多用户实时协同 | ❌ 无多人实时，仅本地 | **TexLite 独占优势** |
| **XeLaTeX** | ✅ 默认引擎 xelatex | ✅ latexmk 自动/`!TeX program` | 都满足 |
| **方正字体** | ✅ latexmkrc 注入 TEXINPUTS（零改核心） | ⚠️ Tectonic bundle 无中文字体；latexmk+TinyTeX 路径可行 | TexLite 更顺 |
| **MD 中间态** | ⚠️ 纯 LaTeX 工作区，需加转换步骤 | ⚠️ 同样需改造 | 都要改造 |
| **可改造性** | ✅ 37 个 vitest 测试兜底，模块清晰 | ✅ 但 Rust 改造门槛高 | TexLite 胜 |
| **许可** | AGPL-3.0 | AGPL-3.0-or-later | 内部自用均可 |

**判据**：用户要"轻量 + 本地 + 可预览 + 实时编辑 + 可改造" → **TexLite 五项全中，是唯一同时满足"实时编辑"的方案**。

---

## 3. 可改造点详析

### 3.1 TexLite 改造（推荐路径）

| 改造项 | 工作量 | 方案 |
|---|---|---|
| **方正字体 + 中文模板接入** | 零核心改动 | 项目 latexmkrc 写 `$ENV{'TEXINPUTS'} = 'd:/ai/latex/templates/fonts;d:/ai/latex/templates/cls;...'`，编译自动继承 → 复用 `\newCJKfontfamily` + fontspec |
| **MD 中间态入口**（方案 B，推荐） | 1-2 天 | 改 `compiler.ts`：spawn latexmk 前插入"MD→LaTeX 转换"（复用 `scripts/convert.py`/`office.py`）；扩展产物发布支持多产物（PDF+DOCX） |
| **MD→Word 直出** | 复用 | 产物端点读服务端文件，DOCX 直接调 `word_template_engine.save(export_pdf=True)` 双格式 |
| **harryopo 模板注册表对接** | 小 | 内置模板 seed 成 TexLite 项目模板；`template_registry.py schema` 供编辑器字段提示 |
| **模板 gallery** | 借鉴 Oleafly | 目录 + template.json + preview.png 契约（TexLite 需补此层） |
| **编译诊断 → harryopo-build-mcp** | 小 | `compileDiagnostics.ts` 结构化诊断（文件/行号/错误分组）直接包装成 MCP 工具 |
| **Windows 注意** | 验证 | `spawn(latexmk)` 对 .bat/.cmd 的路径处理、synctex 二进制需实测 |

### 3.2 Oleafly 借鉴（参考蓝本）

| 借鉴点 | 价值 |
|---|---|
| **EngineDescriptor 能力矩阵** | 引擎选型/能力声明与前端解耦，可移植到 TexLite 改造版 |
| **模板 gallery 契约**（template.json + preview.png） | 直接指导 harryopo 模板注册表 v1 的 preview/字段元数据扩展（M3） |
| **MCP server（127.0.0.1:5323）** | 与 harryopo-build-mcp 同构，可直接参照其审批模型（diff 先行/删除确认/项目范围限定） |
| **revision 匹配才接受 PDF** | 预览可靠性规则（TexLite 也有类似，双保险） |
| **自研 synctex 解析器** | 若 TexLite 的 synctex 二进制在 Windows 有问题，此为替代 |
| **中文拼写/语法** | 均缺（hunspell 西文 only），自研或降级 |

---

## 4. 融合架构建议（阶段 2/3 落地）

```
harryopo-office 基于 TexLite 改造（阶段 2 MVP，localhost:3000）
├── 后端：TexLite Fastify + SQLite（原样）
│   ├── 编译：latexmk（TEXINPUTS 注入 templates/fonts + cls）→ xelatex
│   ├── [改造] compile.ts 插入 MD→LaTeX 转换（复用 convert.py）
│   ├── [改造] 产物发布支持 PDF + DOCX（word_template_engine）
│   └── [包装] compileDiagnostics → harryopo-build-mcp 工具
├── 前端：TexLite CodeMirror6 + Yjs（原样）
│   ├── LaTeX 编辑 + PDF 预览 + SyncTeX + 协同
│   └── [改造] 新增 harryopo 模板 gallery（借鉴 Oleafly template.json）
├── 注册表对接：seed_builtins → TexLite 项目模板；schema 供补全/字段提示
└── 与既有体系：office.py render --serve 子命令启动；--template 路由不变

阶段 3 衔接：TipTap WYSIWYG（借鉴 Oleafly wysiwyg 包）与 CodeMirror 并存，
  共享 localhost 服务与模板注册表（办公文档可视化 + 学术排版双编辑面）。
```

**不采用"自研 ~500 行核心"**：TexLite 已实现编译队列/快照/增量缓存/SyncTeX/协同/预览全套且带 37 个测试，自研等于重复造轮子（违反项目铁律）。改造增量远小于从零实现。

---

## 5. 风险与合规

1. **AGPL-3.0**：TexLite 派生作品若对外提供服务须开源；harryopo 作为个人/内部办公平台自用**无碍**；若未来商业化分发需评估或换许可
2. **单进程限制**：TexLite 无 cluster（SQLite/编译队列进程内共享），单用户/小团队足够
3. **默认 `-no-shell-escape`**：minted 等需 shell escape 场景通过项目 latexmkrc 显式授权（安全默认，符合直觉）
4. **中文路径/编码**：xelatex 日志中文路径 UTF-8 规范化解析需验证
5. **Tectonic bundle 中文字体**（仅 Oleafly 场景）：fandol/ctex 是否在 bundle 内需实测；harryopo 走 latexmk + 方正字体路径不受影响
6. **Node 24 要求**：TexLite 需 Node ≥24，需确认环境（当前用户有 node/npm）

---

## 6. 验证清单（供实施前确认）

- [ ] 本机 Node 版本 ≥ 24（`node --version`）
- [ ] 本机 xelatex / latexmk 可用（`where latexmk`）——**当前环境缺失，需先补齐 TeX Live 或 MiKTeX**
- [ ] TexLite `npm ci && npm run init && npm start` 本地跑通（含 Windows latexmk spawn 实测）
- [ ] 方正字体 TEXINPUTS 注入后 showcase-report.tex 编译通过（中文渲染正确）
- [ ] MD 中间态改造：`office.py` 产物与 TexLite 产物端点对接

---

## 7. 调研源索引

- 源码（已 clone）: `opensource-reference/TexLite/`（DESIGN.md / src/server/compiler.ts / src/client/LatexEditor.tsx / PdfPreview.tsx）
- 源码（已 clone）: `opensource-reference/Oleafly/`（docs/architecture.md / src-tauri/src/document_engine.rs / tex_distro.rs / synctex.rs / packages/wysiwyg/）
- 官方文档: https://oleafly.com/zh-cn/docs/overview/ · TexLite README.zh-CN.md

---

> **方案状态**: 调研完成。建议下一步——基于 TexLite 实施阶段 2 MVP（先补齐 xelatex/latexmk 环境，再跑通本地预览，最后接入方正字体 + MD 中间态改造）。
