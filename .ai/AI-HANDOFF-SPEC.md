# AI-HANDOFF-SPEC — 接手规范（照着走）

> 适用对象：第一次接手本仓库的 AI Agent。
> 本文只写**能落地执行**的规则，每条对应到命令或文件。现状面看 `.ai/HANDOFF.md`，铁律看 `CLAUDE.md`。

---

## 1. 开工前的阅读顺序

按这个顺序读，**读到能回答"这件事该在哪改"就停**，不要通读。

| 顺序 | 文件 | 读它为了解决什么问题 | 入库 |
|---|---|---|---|
| 1 | `.ai/HANDOFF.md` | 现在在哪：最近 5 commit、工作区残留、doctor 两处读数、4 条遗留债、哪些目录不入库 | ✅ |
| 2 | `CLAUDE.md` | 项目铁律 + 踩坑 1–43。**不读会重复踩已知坑**（字体族命名、`!` 错误、双源同步、闸门假绿…） | ❌ 本地 |
| 3 | `docs/REPO_WIKI.md` | 架构地图：§4 能力清单（防重复造轮子）、§8 技术债、§9 复用指引 | ✅ |
| 4 | `.trae/skills/harryopo-office/SKILL.md` | AI 行为契约：触发词、文档生成主流程、全部排版约定 | ✅ |
| 5 | `README.md` / `README.en.md` | 对外门面；改动要**双语同轮**同步 | ✅ |
| 6 | `.learnings/LEARNINGS.md`、`memory/MEMORY.md` | 历史教训与流水。**只作参考，不当真值** | ❌ 本地 |
| 7 | `docs/plans/*`、`docs/research/*` | 方案书与调研：解释"为什么这么设计"，优先级最低 | ❌ 本地 |

**唯一事实来源 = 代码**（`office.py` 的 subparser、`templates/cls/*.cls|sty`、`scripts/*.py`）。
`docs/REPO_WIKI.md` 是已入库的知识库，`CLAUDE.md` 是本地规则，二者都**服从**代码读数。

反例：`memory/MEMORY.md` 有 1500+ 行，里面的数字都是当时读数；拿它当基线必然错位。

---

## 2. 冲突时以谁为准

优先级：**可执行验证 > 代码 > 入库文档 > 本地文档 / 历史报告**

| 冲突类型 | 以谁为准 | 怎么做 |
|---|---|---|
| 数量（检查项/子命令/文件数/文档数） | 命令实时输出 | `office.py doctor`、`doctor --stats`、`office.py --help` |
| 行为（某参数有没有生效、某块渲不渲染） | 源码 | 读 `office.py` 的 `add_parser` 与该链路函数；再实测产物 |
| 页数 / 体积 | **重渲染**的产物 | `output/examples/*.pdf` 是历史快照（paper 已知 6 页，当前模板 7 页） |
| 历史报告（`2026-11-03/*.md`） | 当时读数，不是当下事实 | 要用就重跑命令 |
| 文档 vs 文档 | 已入库者优先 | `REPO_WIKI.md` / `SKILL.md` > `HANDOFF.md` 的叙述 > `MEMORY.md` |

**判据**：任何数字写进文档时，必须同时能写出取数命令；写不出就别写，改成"以 X 命令为准"。

---

## 3. 动工前的环境校验

```powershell
python .trae/skills/harryopo-office/scripts/office.py doctor
```

- **0 FAIL 才开工**；有 FAIL 先修环境或修断言的根因，**不要绕**。
- `[FAIL]` 行会直接给出路径与期望值；`[WARN]` 允许存在（可选依赖缺失/分发包降级），但**要知道为什么**。

工具链缺失的装法（doctor 会报具体路径）：

| 工具 | 现状路径 | 缺失怎么装 |
|---|---|---|
| xelatex | `D:\Tools\TinyTeX\TinyTeX\bin\windows\xelatex.EXE` | 装 TinyTeX/TeX Live；缺宏包用同目录 `tlmgr install <pkg>`；`office.py` 有 `_ensure_tex_on_path()` 补 PATH |
| pandoc | `%LOCALAPPDATA%\Pandoc\pandoc.EXE` | 官方安装器（doctor 认这个路径） |
| mmdc | `%APPDATA%\npm\mmdc.CMD` | `npm i -g @mermaid-js/mermaid-cli` |
| Python 依赖 | — | `python -m pip install python-docx latex2mathml pywin32 pymupdf playwright`（playwright 还需 `playwright install chromium`） |

编译硬约束（违反即白干）：

- **只用 XeLaTeX**（禁 pdfLaTeX / LuaLaTeX）；
- 必须 `-interaction=nonstopmode`；
- **编 3 遍**（交叉引用/目录稳定）；slides 实测 2 遍即可；
- 产物**一律写仓库外**（`$env:TEMP\...` 或任意临时目录）；`output/` 里只有官方示例入库。

---

## 4. 改动的护栏（做完必跑，不是可选）

| 你改了什么 | 必须做什么 | 验收 |
|---|---|---|
| `templates/cls/*.cls|*.sty`、`templates/slides/*` | **单向同步**到 `.trae/skills/harryopo-office/templates/`（根 → skill，不回写） | `diff -q` 两份一致；`office.py doctor` 的 cls 双源 sha 断言转 OK |
| 模板 / Markdown 管线 | 五链回归（§6 的命令全集） | `check_tex_log` 五链全 0 FAIL |
| `scripts/doctor.py` 的检查逻辑 | **注入真 bug 验证**：故意改坏，确认 `[FAIL]` + `exit 1`，再还原 | 只跑一遍"全绿"不算验证（踩坑 35） |
| 子命令集合 / 链路清单 | README 中英 + `SKILL.md` + `REPO_WIKI.md` 同轮同步 | `check_doc_command_claims` 不报 FAIL |
| 分发件（打包） | ①内容以 `git ls-files` 为基准；②解压到**项目外**跑 doctor；③确认新行为出现 | `52 OK / 2 WARN / 0 FAIL`（54 项）+ 两条"跳过"WARN；包内**不带 `.git`** |
| 任何提交前 | 跑一次 doctor + `git status` 复核 | 0 FAIL；工作区只有已知的未跟踪目录 |

**改模板后不要忘了产物侧的连带**：模板行为变了，`output/examples/` 里的快照就过期（页数会变），要么同轮重生成，要么在 HANDOFF 里注明"快照落后"。

---

## 5. 绝不能做

| 禁止 | 原因 / 替代做法 |
|---|---|
| 编造验证读数 | 没跑就是没验证，写"应该能过"等于撒谎。写不出命令的数字不许进文档 |
| 跳步降级 | 把 `check_tex_log` 的 FAIL 改回 WARN、把五链砍成一条、把断言删掉换取"全绿"——闸门降级比缺陷更贵 |
| `git add -A` / `git add .` | 会把 `2026-11-03/`、隐私目录一起带进去。**逐路径 add** |
| `git push --force` 到 main | 历史已被 filter-repo 重写过一次；force push 只在用户明确授权时执行 |
| 把隐私目录入库 | `蒸馏区/ 测试区/ test-e2e*/ 简历/ memory/ .learnings/ CLAUDE.md`。用 `git check-ignore -v <path>` 实证，不读 `.gitignore` 猜 |
| 分发包里带 `.git` | 会让人误判"仓库还在"；包内 `git ls-files` 也失效（见踩坑 41） |
| 直接生成 `.docx`/`.pdf` 二进制 | AI 只产结构化数据（MD/JSON），模板引擎渲染（项目铁律） |
| 用 pdfLaTeX / LuaLaTeX | 中文字体链会断，报错形态完全不同 |
| 按扩展名批量删文件 | 会误删入库交付物（踩坑 38）。先 `git ls-files <pattern>` 求交集，非空即停 |
| 在仓库根留编译副产物 | 产物写仓库外；`*-e2e.*`、`texput.log` 已在 `.gitignore`，但最好根本别产生 |

---

## 6. 交付标准：一条链算"可用"的四个判据

四条**同时**成立才算可用，缺一条就是"出 PDF 了但没编对"：

1. **日志 `! ...` = 0** —— `render` 内置 `check_tex_log` 判 FAIL 即不合格；
2. **页数合理** —— 与上一次读数同级（塌页=提前 `Emergency stop`；暴涨=循环/重复插入）；
3. **关键内容在文本层可检索** —— 标题/关键句能在 PDF 文本里 grep 到（不是被当图片印上去）；
4. **图片不是灰块占位** —— 体积判据：真图 100KB 级，占位块 1888B。

验证命令：

```powershell
# 五链一次性回归（源固定，读数见 HANDOFF §2.2）
python .trae/skills/harryopo-office/scripts/office.py render output/examples/paper-showcase.md `
  --format word,paper,notes,slides,book -o (Join-Path $env:TEMP 'hrp-verify')

# 页数 + 文本层抽检
python -c "import pymupdf; d=pymupdf.open(r'<pdf>'); print(d.page_count); print(d[2].get_text()[:200])"

# 公文规范
python .trae/skills/harryopo-office/scripts/office.py govcheck output/examples/gov-notice-paper.tex
```

Word 链路额外判据：`.docx` 存在且体积在同级（当前 141KB 量级）；需要 PDF 时走 `render --pdf`（COM 导出，属权威核对）。

---

## 7. 出问题时怎么定位

| 症状 | 先查什么 | 命令 / 位置 |
|---|---|---|
| 日志有 `!` | 逐条 `!` 及其后 3 行上下文 | `Select-String -Path <log> -Pattern '^!' -Context 0,3` |
| `Missing character: There is no X` | 字体 cmap 里有没有该字形：`\setCJKmainfont`/`\setmonofont` 指向 vs `templates/fonts/` 实际文件 | emoji（如 `📦`）属**内容**问题，不是模板缺陷 |
| 页数塌（如 11 → 2） | `Emergency stop` **前**最后一个 `!`：常见缺 `\end{...}`、帧内 `verbatim` 缺 `[fragile]`、`$` 被拆成 `$`+`$X$` | 同一条日志尾部 30 行 |
| 图片是灰块 | `ensure_placeholder_figures` 没找到源图：processed MD 与源 MD 目录关系（踩坑 43） | 真图 vs 1888B 占位 |
| doctor 报 cls 双源分叉 | 根与 skill 副本不同步 | `diff -q templates/cls/x.cls .trae/skills/harryopo-office/templates/cls/x.cls`，同步方向**根 → skill** |
| 参数"没生效"（如 `--a5paper`） | 追三层：CLI 透传 → 生成 tex 的 `\documentclass` 选项 → cls 是否读该选项 | 终判用**页面 pt 尺寸**实测（A4 595×842 / A5 420×595） |
| 门"全绿但没抓过 bug" | 闸门可能空转/自比自 | 注入真 bug 试跑（踩坑 35、39、40） |

---

## 8. 收尾清单

1. `office.py doctor` → 项目根 0 FAIL；
2. 更新 `.ai/HANDOFF.md` 的现状面（新 commit、工作区、读数是否变了）；
3. 新踩的坑写 `.learnings/LEARNINGS.md`（**现象 / 根因 / 修法 / 验证** 四段齐全）；
4. 够格进规则的追加到 `CLAUDE.md`「踩坑警示」，**接着编号往下排**；
5. 会话流水追加 `memory/MEMORY.md`（保持原结构，不重排）；
6. 仓库根不留副产物；`git status --short` 只剩已知未跟踪目录。
