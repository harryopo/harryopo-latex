# HANDOFF — 项目现状（新人第一天接手）

> 本文件是**唯一的现状面**：现在在哪、怎么验证、还欠什么。
> 规则看 `CLAUDE.md`（项目铁律 + 踩坑警示），架构与能力清单看 `docs/REPO_WIKI.md`，动手规范看 `.ai/AI-HANDOFF-SPEC.md`。
> 历史会话流水不写在这里（去 `memory/MEMORY.md` 与 `git log`），本文只保留「还在影响今天」的三件事。

---

## 0. 三十秒速览

| 项 | 值 | 怎么确认 |
|---|---|---|
| 项目 | harryopo 办公文档 AI 生产力平台（LaTeX 模板体系 + 自包含 Agent Skill） | `README.md` |
| 阶段 | **维护期**：P0 3/3 · P1 6/6 · P2 5/5 收官；P3 四项未启动 | `CLAUDE.md`「当前状态」 |
| 交付形态 | 自包含 Skill，**13 个子命令 / 5 条输出链路**（word · paper · notes · slides · book） | `office.py --help` |
| 远程 | `origin/main` == 本地 `HEAD` == `65d4c10`，ahead/behind = 0 | `git rev-parse --short HEAD origin/main` |
| 工作区 | 只剩 `?? 2026-11-03/`（本轮审计脚本与报告，约定不入库） | `git status --short` |
| 健康基线 | 项目根 **81 OK / 0 WARN / 0 FAIL**；分发包 **52 OK / 2 WARN / 0 FAIL**（共 54 项） | 两处跑法见 §2.1 |

> 读数会随检查项增减，**别抄表**：判断"正常"的标准是两处都 `0 FAIL`，具体条数以汇总行为准。

---

## 1. 最近 5 个 commit 各自解决了什么

| commit | 标题 | 解决了什么 | 验证 |
|---|---|---|---|
| `8cbb0c8` | feat(skill): 示例资源入包 + processed MD 图片解析基准修复 + xelatex 缺失提示 | ①分发包首次带 `examples/`（6 个 MD 源 + figures），"整个目录拷走即用"才真有 demo 可跑；②`office.py` +38/-2：processed MD 写进 `output_dir` 后相对图片基准丢失，notes 会静默落 800×400 灰块，改为回填源图；③xelatex 不在 PATH 时给明确提示（`_ensure_tex_on_path`），不再只报一句"失败" | 11 files +1463/-2；`output/examples/report-showcase.processed.md` 真图 118539B，不再是 1888B 灰块 |
| `1d52a17` | docs: 三步上手 + examples 目录树同步 + 画像数字更新 | 门面（README 中英 + SKILL.md + REPO_WIKI）与内核能力对齐：三步上手、examples 目录树、画像数字 | 4 files +64/-5 |
| `f99cf65` | docs(assets): 架构图入仓 `docs/assets/skill-demo` | 架构图从"本地看图"变成仓库内可追溯（HTML 源 + PNG），画廊图不再依赖个人机器 | 2 files +131（`office-layers.html` 131 行 + `office-layers.png` 84549B） |
| `2a25f77` | docs: 画像同步 633 文件 / 101 文档 | examples 与 assets 入库后，doctor 的画像行与之对齐 | 1 file ±1 |
| `65d4c10` | fix(doctor): 消融包内自比自 sha 与凭据扫描空转 | 分发包模式 `PROJECT_ROOT == SKILL_DIR`，cls 双源 sha 比对退化成"自比自"（恒等 OK）；无 `.git` 时 `git ls-files` 为空，隐私/凭据检查静默 OK。改为**显式 WARN 声明跳过**（"无双源可比，跳过 sha 比对；必含段 21 项仍生效" / "git ls-files 执行失败，跳过检查"） | 2 files +79/-38；包内读数由 61 OK 收敛为 **52 OK / 2 WARN** |

---

## 2. 怎么验证一切正常

### 2.1 doctor：两处读数，别混用

项目根（在仓库里跑，有 `.git`，检查项最全）：

```powershell
python .trae/skills/harryopo-office/scripts/office.py doctor
# === 汇总: 81 OK / 0 WARN / 0 FAIL ===
```

分发包（把 skill 目录拷到**项目外**，模拟用户拿到的 zip）：

```powershell
$tmp = Join-Path $env:TEMP 'hrp-pkg-check'
robocopy .trae\skills\harryopo-office "$tmp\harryopo-office" /E
python "$tmp\harryopo-office\scripts\office.py doctor"
# === 汇总: 52 OK / 2 WARN / 0 FAIL ===   （共 54 项）
# [WARN] 分发包模式：无双源可比，跳过 sha 比对；必含段 21 项仍生效
# [WARN] git ls-files 执行失败，跳过检查
```

差的 27 项是**只在仓库内成立**的检查（cls 双源 sha、隐私护栏、gitignore 有效性、文档时效等）。
包内那 2 条 WARN 是"如实降级"，不是缺陷；**只要出现 FAIL 就是真问题**。

### 2.2 五条输出链路：一条命令全覆盖

```powershell
python .trae/skills/harryopo-office/scripts/office.py render output/examples/paper-showcase.md `
  --format word,paper,notes,slides,book -o (Join-Path $env:TEMP 'hrp-handoff-verify')
```

2026-11-07 实测（同一源、默认 `fangzheng` 字体方案）：

| 链路 | 产物 | 预期读数 |
|---|---|---|
| word | `paper-showcase-word.docx` | 141KB |
| paper | `paper-showcase-paper.pdf` | **7 页** / 302KB |
| notes | `paper-showcase-notes.pdf` | 7 页 / 267KB |
| slides | `paper-showcase-slides.pdf` | 11 页 / 232KB |
| book | `paper-showcase-book.pdf` | 11 页 / 298KB |

> 体积按 KiB 四舍五入（`文件字节 / 1024` 取整），对照命令：`Get-ChildItem <dir> | Select-Object Name,Length`。

> ⚠️ **入库快照已落后**：`output/examples/paper-showcase-paper.pdf` 还是 2026-09-20 的版本，**6 页**；当前模板重渲染是 **7 页**。
> 其余四份页数一致（notes 7 / slides 11 / book 11）。产物页数一律**以重渲染为准**，快照只作展示。

book 的纸张开关（A4/A5，实测尺寸差）：

```powershell
... render output/examples/paper-showcase.md --format book --a5paper -o <dir>
# A4: 11 页 595×842pt      A5: 16 页 420×595pt
```

`render` 内置 `check_tex_log`：任一条链日志出现 `! ...` 直接判 **FAIL**——**"出了 PDF"不等于"编对了"**（nonstopmode 会吞错照出文件）。

### 2.3 其他常跑

```powershell
python .trae/skills/harryopo-office/scripts/office.py govcheck output/examples/gov-notice-paper.tex   # 10/10
python .trae/skills/harryopo-office/scripts/office.py doctor --stats                                  # 画像行
python .trae/skills/harryopo-office/scripts/office.py --help                                          # 13 个子命令
```

当前画像：**633 个入库文件 / 101 篇文档 / ~17728 行 / 29 个 skill 自研脚本 + 16 个辅助脚本**。

### 2.4 分发包"打对了没"

打包后必须走三步，缺一步都可能是假绿：

1. 解压/拷到**项目外**（不能在仓库里，否则 `_find_project_root()` 会指回项目根）；
2. 跑一次 `office.py doctor`；
3. **确认新行为出现**：能看到上面那两条 WARN、以及「文档口径 13 个」。
   如果看到 61 OK 或 10 条 `cls 双源 sha256 一致` 的 OK，说明打进去的是**旧 `doctor.py`**。

---

## 3. 已知未修项（4 条：为什么留着 / 动它的前置条件）

### 3.1 双生渲染函数

- **现象**：`.trae/skills/harryopo-office/scripts/mermaid_render.py` 与 `diagram_render.py` 的 `find_blocks` / `code_hash` / `extract_and_render` 近乎逐行重复。
- **为什么留着**：两条引擎各自稳定，且服务不同后端——mermaid 走 `mmdc` 出 PNG，diagram-design 走 HTML→playwright 出 PNG；调用方分散在 `office.py diagram` 与 render 主流程。重复不是错误，**合并才会引入回归面**。
- **动它的前置条件**：先补齐一份能同时覆盖三类块的回归用例（mermaid 块 / diagram-design 块 / `super-diagram` 块被**拦截报错**），且 mmdc + playwright 都可用；否则不动。背景记在 `docs/REPO_WIKI.md` §8-3。

### 3.2 notes 的 12 条 `Font shape ... undefined` Info

- **现象**：notes 链路 xelatex 日志里 12 条 shape Info（系统字体族的 Bold/Italic 回退分支），**不是 `!` 错误**，产物完全正常。
- **为什么留着**：notes 是独立体系（`templates/math-notes/harryopo-mathnotes.cls` 不加载 base.sty，见 CLAUDE.md 踩坑 1），这 12 条来自回退分支；动它等于改正文观感，风险大于收益。
- **动它的前置条件**：备一份同源「改前/改后」PDF 肉眼对照（字形无退化）+ 用户认可观感变化。
- **证据**：`2026-11-03/skill-final/outputs/skill-ready-report.md`（notes resolve=12 shape Info 那一条）。

### 3.3 `scripts/yaml2ir.py` 死引用

- **现象**：文件已入库，但**全仓零代码调用**；只有它自己的 docstring 与 `docs/REPO_WIKI.md:68` 还把它写成流程一环（super-diagram 时代残留）。
- **为什么留着**：无副作用、不参与任何链路；删之前要先排除外部脚本 import。
- **动它的前置条件**：`grep -rn yaml2ir --include=*.py .` 结果只剩它自己；用户点头删除；**同轮**把 `docs/REPO_WIKI.md:68` 那行摘掉。

### 3.4 notes 链路的 emoji 缺字形（`📦` 等）

- **现象**：编译日志 `Missing character: There is no 📦`；源在 `output/examples/report-showcase.md:440`（**内容里的 emoji**）。
- **为什么留着**：这是输入内容，不是模板缺陷；CJK 字体本就没有 emoji 字形，硬修只能换符号，或引入 emoji 字体（体积 + 授权面）。
- **动它的前置条件**：用户同意把示例内容里的 emoji 换成文字/ASCII 标记，或明确接受引入 emoji 字体。

---

## 4. 哪些目录/文件不入库，为什么

| 路径 | 状态 | 原因 |
|---|---|---|
| `/docs/plans/`、`/docs/research/`、`/docs/*.md` | 忽略 | 方案书与调研报告属过程材料；例外 `!/docs/REPO_WIKI.md`（知识库必须入库）、`docs/assets/`（画廊图） |
| `/memory/`、`/.learnings/`、`/CLAUDE.md` | 忽略 | 个人流水 / 学习日志 / 本地规则。**克隆仓库的人看不到 CLAUDE.md**，所以铁律必须同步进已入库的 `SKILL.md` + `REPO_WIKI.md` |
| `output/*`（`!output/examples/**` 例外） | 忽略 | 生成产物默认不入库；只有官方六示例（md/docx/tex/pdf 三格式）入库展示 |
| `/蒸馏区/`、`/测试区/`、`/test-e2e*/`、`/简历/` | 忽略 | 隐私与测试残留 |
| `opensource-reference/` | 忽略 | 第三方源码自带 git |
| `*.aux` `*.log` `*.toc` `texput.log` 等 | 忽略 | 编译残留 |
| `templates/**/*-e2e.tex|pdf` | 忽略 | `office.py` 渲染副产物 |
| `2026-11-03/` | **未跟踪、也未被忽略** | 本轮审计脚本/报告/临时产物，按约定只留本地，**不要 `git add`** |

核对命令：

```powershell
git check-ignore -v docs/plans memory .learnings CLAUDE.md 蒸馏区 测试区
git ls-files output | Measure-Object -Line    # 40（仅 output/examples）
git status --short                            # 只应看到 ?? 2026-11-03/
```

---

## 5. 还在影响今天的三件历史

- **2026-11-01**：doctor 接进 CI，首跑就抓到 `git ls-files` 在 Linux 上把 CJK 路径转义成 `"\345\217\202..."` → 取数面一律改 `ls-files -z`；同轮清掉 paper 链路 61 条编译错误（缺陷表见 REPO_WIKI §8）。
- **2026-11-02**：五条 LaTeX 链路存量 `!` 错误清零（slides 帧内 `verbatim` 缺 `[fragile]`、book 计数器/页眉、`--a5paper` 断线等）；`check_tex_log` 由 WARN 升级为 **FAIL**。
- **2026-09-27**：PII 历史清算（filter-repo 两轮 + force push），此后隐私护栏进 doctor；**fork 数为 0**，旧历史没有被 fork 带走。

---

## 6. 下一步

- **P3 储备**（方案书 v3 §6）：Typst 第三输出通道 · 模板市场 + 多人协作 + 版本审计 · pdfcpu 后处理 · HermesOffice 字节保真往返。
- **可编辑 `.pptx`**：2026-09-18 定调 beamer/PDF 路线后降级，暂不动。
- **§3 四条遗留债**：都写了前置条件，条件不满足就别动。
- **官方示例产物重生成**：`output/examples/paper-showcase-paper.pdf`（6 页）落后于当前模板（7 页），是否重生成待定。
- **`2026-11-03/` 去留**：确认无用即删；无论如何不入库。
