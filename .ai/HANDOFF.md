# HANDOFF — 会话交接记录

> 规范：每次会话结束更新本文件。**代码是唯一真值源**，本文件是导航与线索。
> 置信度标记：✅ 已验证（有命令/文件为证）· ⚠️ 进行中 · ❓ 待确认

---

## 当前状态速览

| 项 | 值 | 置信度 |
|---|---|---|
| 项目 | harryopo 办公文档 AI 生产力平台 | ✅ |
| 阶段 | **维护期**（P0 3/3 · P1 6/6 · P2 5/5 收官；P3 四项未启动） | ✅ |
| 交付形态 | 自包含 Agent Skill，13 个子命令 / 5 条输出链路（word·paper·notes·slides·book）+ 规则包合规检查/盲审隐匿 | ✅ |
| 健康检查基线 | `office.py doctor` 的 OK 项数**随检查类增减，别抄本表**——跑一次看汇总行（2026-11-01 实测 69 OK / 0 WARN / 0 FAIL，其中含「文档口径」一类） | ✅ |
| chinese-book | 缺字形 691→0；错误 7→**3** 且**三个丢失的边栏 caption 已全部恢复渲染**（floatrow 报错降为处理期告警，恢复后输出正确） | ✅ |
| 远程同步 | `origin/main` = 本地 HEAD（2026-10-11 接手轮发现 6 commit 漏推已补推；2026-10-31 复核 `origin/main..HEAD` = 0） | ✅ |
| CI | `.github/workflows/ci.yml`（skill-ci）：lint + latex-render 两 job，**latex-render 末尾跑 `office.py doctor`**（2026-11-01 起，闸已接进 CI） | ✅ 2026-11-01 分支试跑 success |

---

## 权威文档导航（先查这里，别读记忆文件当真值）

| 文件 | 角色 | 入库 |
|---|---|---|
| `docs/REPO_WIKI.md` | **架构地图 + 能力清单 + API + 技术债**（接手先读 §4 能力清单防重复造轮子、§9 复用指引） | ✅ |
| `.trae/skills/harryopo-office/SKILL.md` | AI 行为契约：触发词、主流程、全部排版约定 | ✅ |
| `CLAUDE.md` | 项目铁律 + 37 条踩坑警示（**本地未入库**） | ❌ |
| `memory/MEMORY.md` | 会话流水（**本地未入库**，只作参考；行数会涨，别当真值） | ❌ |

> ⚠️ **已知反模式**：`CLAUDE.md` / `MEMORY.md` 在 `.gitignore` 内，克隆仓库的人看不到。涉及项目铁律时，优先读已入库的 `SKILL.md` + `REPO_WIKI.md`。

---

## 2026-11-01 会话：doctor 接进 CI + 顺带抓到取数面的 CJK 盲区

### 本次完成

| # | 工作 | 验证 |
|---|---|---|
| 1 | `ci.yml` 的 `latex-render` job 末尾加 `office.py doctor` 步（闸长在提交落地的地方）；放这个 job 而非 lint job，因为 `check_toolchain` 对 xelatex 缺失判 FAIL 而 lint job 不装 TeX | ✅ 分支试跑（`workflow_dispatch --ref`）两 job success；**不动 main 先量风险** |
| 2 | **CI 首跑就照出一个本机照不出来的盲区**：doctor 的画像/隐私断言从 `git ls-files` 取数，ubuntu 默认 `core.quotePath=true` 把 CJK 路径转义成 `"\345\217\202..."` 一整项，`endswith('.md')`、`startswith('蒸馏区/')` 全体漏匹配 → Linux 上少算 2 个 .py + 4 个 .md + 616 行，且**隐私闸会在个人材料真被跟踪时报"全 OK"** | ✅ 本机对照实验：`quotePath=true` 下旧取数面看不见 canary、`-z` 看见 |
| 3 | 两处改 `ls-files -z`（NUL 分隔永不转义） | ✅ 强制 `quotePath=true` 与默认配置下 `--stats` 输出逐字一致（607/29+16/~17314/94）；**canary**：伪造跟踪 `蒸馏区/__privacy_canary__.md` → `[FAIL] 蒸馏区/ 被 git 跟踪（1 个文件）`、exit 1，随后 `git rm --cached` + 删文件复原，`git ls-files 蒸馏区` 回 0 |
| 4 | 拆掉两处会漂的手写基线数字：REPO_WIKI 用法段的「当前基线 68 OK…」、HANDOFF 速览行的固定读数，改为"跑一次看汇总行" | ✅ doctor 复跑 69 OK / 0 WARN / 0 FAIL（Linux 端为 6 WARN 0 FAIL，都是 CI 不装的可选依赖） |

### 关键收获

- **"本地绿、CI 才有读数"的取数面问题**：本机 git 配了 `core.quotePath=false`，所以 CJK 路径在两种实现下表现相同，盲区完全隐形。**按路径前缀/后缀做断言的门，取数必须用 `-z`**，不然非 ASCII 目录（本项目就叫 `蒸馏区`、`参考资料`、`测试区`）会静默漏出闸外。对应既有教训「闸与夹具的取数面」「量具必须能被证伪」。
- CI 里那 5 个 WARN（pandoc/mmdc/系统浏览器/pymupdf/playwright/win32com）是**诚实读数**：CI 环境确实没装，且只降不阻断。别为了"CI 全绿好看"去豁免它们。

### 本次完成（续）：按出口枚举补第 8 类闸「凭据形态」

隐私护栏原先只查"个人材料目录有没有被跟踪"，但**已跟踪文件内容里混进 token** 是另一条独立出口
（改环境脚本、示例配置、复制粘贴的链接）。新增 `check_credentials`：逐个入库**文本**文件扫 8 类形状
→ AWS AKIA / GitHub token(ghp_/gho_/ghs_/github_pat_) / OpenAI sk- / PEM 私钥块 / JWT /
带密码的 URL(`://u:p@host`) / IM webhook(Slack·钉钉·Discord) / `key = "≥16 位且含数字或符号的字面量"`。
命中即 FAIL；二进制按 NUL 嗅探跳过、单文件上限 3MB（**已知边界**：docx/pdf 里塞凭据照不到，只能靠 review）。

| 验证 | 结果 |
|---|---|
| 存量扫描 | 607 个入库文件 **0 命中**（收紧前的宽松版会假报 `token = text.split(...)` 两处，收紧右值形状后清零） |
| canary | 造 `__cred_canary__.md` 注入 7 类形状 → 7 条 FAIL 全中、exit 1；同时良性行（`api_key = "text"` 短值、`token = text.split(...)`）正确放过 |
| 清理 | `git reset -- 路径` 取消暂存 + 删文件（canary 从未进 HEAD）；`git ls-files` 回 0 |
| 口径同步 | 5 处 doctor 能力清单同改（SKILL.md frontmatter + 路由表、office.py help/docstring、README 中英），Python 脚本断言每处命中恰好 1 次 |

本机基线：**70 OK / 0 WARN / 0 FAIL**（+1 类）。

### 顺手关掉一项待确认

`fork` 检查不用劳用户了：`gh api repos/harryopo/harryopo-latex/forks` = **0**，`forks_count=0`。
所以 9-27 历史重写没有被 fork 带走旧历史；**唯一残余风险只剩 GitHub 服务端按 SHA 缓存的不可达对象**（需 Support 工单）。

### 本次完成（续2）：全链路编译体检 + 模板 8 项缺陷清零（同日晚些）

给 `office.py` 加了 `check_tex_log`（每条 LaTeX 链路收口前解析 xelatex 日志），因为它一上就发现
**五类链路每次编译都在吞错误**（paper 61 条）。逐条定位并修 8 项，A/B 对照（同一份 e2e 用改前/改后模板各编一遍）
**61 → 0**；详细成因表见 `docs/REPO_WIKI.md` §8「2026-11-01 编译日志断言抓出的模板缺陷」。

| 验证 | 读数 |
|---|---|
| 九用例复测（产物全写仓库外 `Temp/hrp-audit`） | paper 单栏/双栏、report、gov、word 学术/gov、notes **七项 rc=0 且日志零错误**；slides 6 条、book 10 条待清 |
| govcheck | 10/10 通过 |
| PDF 公式字体 | 7 份产物 CM 回退**全部为无**、XITS 在位 |
| 双源同步 | typography/book/mathnotes 三份改动都 cp 到 skill 副本，`doctor` sha256 断言通过（期间真报过一次 30 行差异，同步后回绿） |
| 新闸 | doctor 加「宏名合法性」（宏名含数字即 FAIL，横扫即抓出 `book.cls` 的 `\harryopo@a5paper`）与 `check_tex_log` WARN |

**顺带查出的两件事**（都归到下面待办，不是猜测，有实测）：
- `--a5paper` 是**假开关**：A4/A5 两次渲染页面同为 595×842pt，生成的 tex 恒为 `\documentclass{harryopo-book}`
- 架构图 `output/skill-demo/office-layers.html|png`（09-20）**已过期**：图上写"11 subcommands · 4 chains"，
  实际 13 子命令 / 5 链路，且交付物层还写着没做的 `pptx`；REPO_WIKI §3.2 的 mermaid 数据流图同样缺
  slides/book/盲审/日志断言（本轮已把 mermaid 补齐，**架构图重绘待用户审核**）

---

## 2026-10-31 会话：状态复盘 + 文档漂移横扫（无功能改动）

### 实测现状（本轮取数）

| 项 | 读数 | 取数方式 |
|---|---|---|
| doctor | **68 OK / 0 WARN / 0 FAIL** | `office.py doctor`（修画像前 67 OK / 1 WARN） |
| 子命令 | **13** | `office.py --help` 实读 |
| govcheck | **10/10 通过** | `office.py govcheck output/examples/gov-notice-paper.tex` |
| 远程同步 | `origin/main..HEAD` = **0** | `git log --oneline origin/main..HEAD \| wc -l` |
| CI | 最近一次 run **success**（skill-ci / main） | `gh run list` |
| 最近提交 | 2026-10-11（本轮为空窗 20 天后的第一次改动） | `git log -1` |

### 本轮完成

| # | 工作 | 验证 |
|---|---|---|
| 1 | REPO_WIKI 头部画像漂移回正（603/28/16799/93 → 607/29/17226/94，取 `doctor --stats` 实时值整行替换） | ✅ doctor 文档时效项转 OK |
| 2 | **同类横扫**：顺着"手写数字必漂"这条线全仓查同类，另清 4 处——REPO_WIKI 的「52 项断言」×2、「28 个脚本」、SKILL.md 目录树「render/diagram/template 三子命令」、HANDOFF 导航表「MEMORY.md 1180 行」 | ✅ `grep` 断言零命中 |
| 3 | **改法不是改数字，是拆掉会漂的写法**：断言项数/脚本数改为「以 doctor 实时计数为准」，子命令列全 13 个名字（`--help` 可读回） | ✅ 无新增手写数字 |
| 4 | README 中英同步：12→13 子命令 + 补 `blindcheck` 特性条与快速开始 3.5 步（上轮 Adopt 的 blindcheck/规则包在门面完全没露出） | ✅ 双语同改；`blindcheck --help` 核实接受文件/目录 |
| 5 | **闸门化（不是修完就完）**：doctor 新增第 6 类检查 `check_doc_command_claims`——现状面四份文档（README 中英/REPO_WIKI/SKILL.md）里"N 子命令"声明与列举清单必须等于 `office.py` 实际注册集（从源码 `sub.add_parser` 直取，不跑 `--help` 避免自嵌套）。`.ai/HANDOFF.md` 与 memory 流水按"历史读数不改写"排除在外 | ✅ **canary 双注双验**：README 改 12 → `[FAIL] README.md:100 声明 12 子命令，实际 13 个`；SKILL.md 清单删 `doctor` → `[FAIL] SKILL.md:28 子命令清单漏列 doctor`；两处从 /tmp 副本还原后 **69 OK / 0 WARN / 0 FAIL**，退出码回 0 |
| 6 | 闸门首跑就抓到本轮自己漏掉的两处：REPO_WIKI:38 目录树仍写 12、REPO_WIKI:82 §3.1 清单漏 `doctor`（"grep 到却漏改"的典型） | ✅ 已修，且由闸门兜底 |

**阈值教训**：清单完整性一开始按"行内出现 ≥3 个命令名"触发，误报 4 处散文（特性条"redline + revise + live 三态闭环"根本没有穷举承诺）。改为"窗口内出现 ≥6 成命令名才算在列举全部"后假阳性清零、真缺陷仍全中——**闸门的判据要挑"它在不在做承诺"，不是"它在不在提这些词"**。

### 方法论留档

- **一个漂移数字背后是一族**：REPO_WIKI 头部只是被 doctor 咬着报出来的那一个；同类手写数字（断言项数、脚本数、子命令数、行数）doctor **不检查**，靠"报一个修一个"必然漏。修完后这类数字要么删掉、要么改成"以 X 命令实时输出为准"。
- **门面落后于内核**：10-11 落地的 `blindcheck` + 规则包架构进了 SKILL.md/REPO_WIKI/HANDOFF，但 README 中英两份完全没提——**外部可见面必须和内部能力同轮同步**，否则用户永远发现不了新功能（对应"功能可达性也算缺陷"）。
- HANDOFF 当日核验记录里的"12 个子命令"是**历史读数**，不改写，只加当日 Adopt 后的括注。

---

## 2026-10-11 会话：接手轮——intake 核验 + 漂移修复（交接补全）

### 本次完成

| # | 工作 | 验证 |
|---|---|---|
| 1 | super-memory intake 全量核验：本文件 + `docs/REPO_WIKI.md` + `memory/MEMORY.md` 尾部交叉印证 | ✅ 核验记录见 memory/MEMORY.md「2026-10-11」节（本地文件） |
| 2 | **漂移修复**：远程同步声明过期——6 个 commit（10-03~10-05 全部成果）未推送，origin/main 停在 10-02 | ✅ 补推后 `git log origin/main..main \| wc -l` = 0 |
| 3 | **漂移修复**：REPO_WIKI 头部画像漂移（582→592 文件、92→93 文档，doctor 报 WARN）→ 按 `doctor --stats` 实时值替换 | ✅ doctor 回到 **68 OK / 0 WARN / 0 FAIL** |
| 4 | 10-05 会话补录进 memory/MEMORY.md（此前只记在本文件，本地流水断档） | ✅ 已追加（本地文件，不入库） |
| 5 | 工作区残留登记：根目录 `probe2.tex`（chinese-book 排错探针）+ `templates/{book,math-notes,slides}/figures/` 未跟踪图表 PNG（五链路回归管线副本；`templates/paper/figures` 有入库先例）——**未清理**，是否入库待用户决定 | ⚠️ 仅登记 |

### 核验结论（接手者重点）

- 12 个子命令实测存在：render / template / diagram / redline / revise / live / trace / style / govcheck / ide / info / doctor
  （注：这是当日 intake 时刻的读数；同日 Adopt 落地 `blindcheck` 后为 **13**，以 `office.py --help` 为准）
- `CLAUDE.md` 与 `memory/` 确在 `.gitignore`（97/99 行）——**仓库里没有会话流水是设计而非事故**；入库知识三件套 = `SKILL.md` + `docs/REPO_WIKI.md` + 本文件
- doctor 基线 68 OK 是回归红线：改模板/换机器/提交前必跑（见「可复现验证命令」§1）

### 本次完成（续）：chinese-book 691 条缺字形清零（当日第二项）

**根因**（最小对照实验实锤，见 commit 5cc19ec）：`kaoWinCJKsc.sty` 13 处声明把 fontspec
特性写在命令名之前——`\newCJKfontfamily[Path=...]\fzA{FZSSJW}`。xeCJK 语法是
`\newCJKfontfamily[族名]\命令[特性]{字体}`，**特性整串被解析成"族名"**：13 个声明共用
垃圾族名互相 Redefining（日志可见），`\fzsong` 等命令注册的字体**不带 AutoFakeBold/Slant
也不带 Path**。凡对该族内容加粗/斜体（字体演示块 `\textbf`、kaobook 边注斜体），
b/it/bi 形状解析失败 → 族回退主字体 XITS（纯拉丁）→ 中文 Missing character。

修复：13 处改为标准语法并显式注册族名（fzsong/fzhei/fzkt/fzfs/…，使既有
`\CJKfamily{fzfs}` 引用按原意生效）。验证：missing **691→0**、errors 10→7
（3 处 "FZFSJW cannot be found" 同根因一并消失=原"低"待办边注 \url 解决）、
pages 58 不变、capacity 0、doctor 68 OK、zimubiao 页渲染目检四组字体样张全真实输出。

**教训**：上轮 10-05 会话修的"AutoFakeBold 补齐"实际没生效（特性被吃了），但当时
验证指标（\x00 文本层计数）恰好归零，造成"已修好"的假象——**修完要验"机制生效"
而不只是"指标变化"**；另 10-05 会话把 3 处 FZFSJW 错误归因于"\url 延迟展开"，
实为同一语法问题，归因时两个现象同根因的情况要主动并案。

### 本次完成（续2）：chinese-book 错误 7→3（当日第三项）

| 项 | 结果 |
|---|---|
| lstlisting 孤儿环境连锁（4 错） | ✅ **已清**：paiban.tex:245 示例行含字面 `\end{lstlisting}` → 扫描器提前闭合 → 真 \end 孤儿。修法=内容行不出现完整序列。**无效法留档**：行内加空格（listings 比较忽略空白）、序列前后加普通文字 |
| floatrow Caption lost ×2 | ⚠️ 未清，已精确定位：wide-fig（全书唯一 figure*，floatrow 未管理该类型；floatsetup/改 figure 均无效，widefigure 环境未定义）+ yinyong 表（\centering 前置假设已证伪）。**边栏标题真丢**，需自建 widefigure 或细读 kaocaption toggle |
| endcsname ×1 | ⚠️ 记档：markdown 包 glossaries 主题第三方交互（preamble 期非致命），按"不动第三方包"原则不修 |
| 工作区残留 | ✅ 已清：probe2.tex 删除；三个 figures 副本目录入库 |

**方法论教训（本轮实测）**：①对比"正常 vs 失败"样本前先确认样本真实性——把
lstlisting 里的代码示例当成了真浮动体，对比结论全部作废；②修法失败要留档
（无效法清单防止后人重走），本次 4 个无效修法已写进待办表；③**错误数是代理指标，
产出物才是目标**——floatrow 报错在但 caption 渲染正确 = 可接受状态，别为追零
错误进入 floatrow 内部深水区。

### 本次完成（续3）：floatrow caption 全部恢复渲染（当日第四项）

读 kaocaption toggle 机制（kaoCJKsc.sty:664-707）后定位两处真缺陷并修复：
1. **开关泄漏**：AtEndEnvironment 只精确匹配环境名，figure* 结束不触发 figure 的
   钩子 → kaocaption 泄漏。补 figure* 钩子（只复位开关；钩子里放 \RawFloats 会
   全局泄漏让下一个 table 报错——实测教训）。
2. **figure* 无 caption 管线**：floatrow 不管理 figure*，修法=浮动体内容首行
   `\RawFloats` 切标准 caption（图下方居中，恰与演示文案一致）。
验证：三 caption（wide-fig/student-scores/yinyong）PyMuPDF 文本层 + yinyong 页目检
（边栏 Table 5.1 样式、lstinline 等宽、边注全在位）；missing 0 / 58 页 / doctor 68 OK。
余 2 floatrow 报错为处理期告警（nonstopmode 恢复后输出正确），不追零。

---

## 2026-10-05 会话：chinese-book 从"编译中断"修到"完整输出"

### 起因
上一轮提交（c1e99d8）在 message 里写"chinese-book 1127 个 null 空字符 → 0"。
复检发现**该结论不成立**：重新编译后 `main.log` 有 1258 条 Missing character、
且 `tuxiangyubiaoge.tex:40` 处 `TeX capacity exceeded` **直接中断编译**，
PDF 只出 18 页（后 2 页内容丢失）。原判据数的是 PDF 文本层的 `\x00`，
而根因是内容在**排版阶段被丢弃**，两个指标测的不是同一件事。

### 修复清单（全部有 file:line 与对照实验）

| # | 问题 | 根因 | 修法 |
|---|---|---|---|
| 1 | 编译中断（18 页截断） | `kaoCJKsc.sty` 的 `\AtBeginEnvironment{figure}` + `\let\oldcaption\caption` + `\RenewDocumentCommand{\caption}` 自我递归：钩子对每个 figure 都跑，第二次 `\oldcaption` 指向包装版 → parameter stack 溢出 | 一次性 `\let\kao@realcaption\caption` 存真身，所有包装只引用它 |
| 2 | 142 处度量错误 | `\RaggedRightParIndent` **大写 I 拼错**（ragged2e 定义的是 `Parindent`），`\setlength` 参数解析失败 | 改正拼写 |
| 3 | 49 处 titlesec "No format" | titlesec 与 KOMA-Script 章节命令冲突，加载后无人 `\titleformat` | 移除（上游 kaobook 本就不用它，是适配层多加的） |
| 4 | 边注中文全部丢失 | `\newCJKfontfamily` 只声明 CJK 族，marginnote 盒子整体切到该族 latin 分支 → 中文落到 XITS | `\marginfont` / `\@margin@par` 的 `\fzfs` 后补 `\rmfamily` |
| 5 | 15 处 fontspec "cannot be found" | Libertinus Serif/Sans、Mono、Math 本机未安装 | `\IfFontExistsTF` 探测 + 回退内嵌字体 |
| 6 | FZ 族注册失败 | FZ*JW 是单一字重静态字体（fontTools 实测无 fvar），缺 b/i 形状 | 全部补 `AutoFakeBold`/`AutoFakeSlant` |
| 7 | 定理环境全部消失 | kaotheoremsCJKsc 有**两套完全重复**的定理定义（mdframed 真/假两个分支）；`framed` 无默认值且缺 `\ProcessOptions` | 删重复分支 + `framed` 默认 true + 补 `\ProcessOptions` |
| 8 | `\c@proposition already defined` | thmtools 0.76 的 `\@counteralias` 与 amsthm 2.20 在 LaTeX 2026-06 内核下冲突 | 去掉 `sibling=theorem` |
| 9 | 若干 Undefined | iftex 新版不再定义 `\XeLaTeX`；listings 1.11b 移除 `\lst@setcatcodes`；`\abstractname`/`\partpagemarkname`/`\labcor` 无人定义；`\Env` 应为 `\Environment` | 逐个 `\providecommand` 兜底 + 改正错宏 |
| 10 | 章首图缺失 | `images/` 空目录，7 处 `\setchapterimage` 指向不存在的 seaside | 补占位图并修正扩展名 |

**结果**：errors 405 → 10 · 页数 18 → 58 · 空字符 0 · 定理环境全部恢复渲染
（Proposition 5 / Lemma 3 / Corollary 3，此前全为 0）· `doctor` 68 OK 无回归

### ⚠️ 仍未解决（如实记录，不要当成已修）

- **691 条缺字形**（183 个不同字符），全部落在 XITS 三个纯拉丁字重上
  → xeCJK 的 CJK 族选择在这些环境下失效。集中在 `zimubiao.tex`(320) /
  `fulu.tex`(251) 两章的**表格内 `\lstinline|...|` 混排**。
  已排除：等宽字体字重、`\texttt`、`\lstinline` 基础用法（最小样例均 0 缺失），
  但最小样例**复现不出来**，需在 kaobook 完整类下用 `\errorcontextlines` 逐层二分。
  影响：这些字从 PDF 文本层丢失，**不影响编译成功与页面输出**。
- 3 处 fontspec `FZFSJW cannot be found`：边注里 `\url` 被延迟到出页才展开，
  此时 fontspec 按字体名解析不到内嵌字体。边注文字本身正常，**只是 URL 不显示**。

### 关键决策

- **`sibling=theorem` 是妥协**：去掉后 proposition/lemma/corollary 各自独立编号，
  不再与 theorem 共享计数器（原本 1.1 / 1.2 连续）。要恢复共享需升级 thmtools，
  本机 tlmgr 不在 PATH，未走装包路线。
- **没装任何 TeX 包**：全部靠 `\providecommand` / 字体探测兜底，保证换机器也能编译。
- chinese-book 仍是第三方 kaobook 适配，**LaTeX 2026-06 内核比它新两年**，
  类似的版本错配大概率还有。当前自研 `harryopo-book.cls`（11 页 / 0 空字符）
  反而更干净，两条链路都在管线里可用。

### 验证方法（可复现）

```bash
# chinese-book 完整编译 + 客观指标（class 在 styles/ 子目录，必须给 TEXINPUTS）
cd templates/chinese-book && python -c "
import os,subprocess,re
env={**os.environ,'TEXINPUTS':f'{os.getcwd()}/styles//;{os.getcwd()}/../fonts//;'}
subprocess.run(['xelatex','-interaction=nonstopmode','main.tex'],env=env,timeout=1800)
log=open('main.log',encoding='utf-8',errors='replace').read()
from collections import Counter
print('errors:',len(re.findall(r'^! ',log,re.M)),Counter(re.findall(r'^! (.{0,55})',log,re.M)).most_common(6))
print('missing:',log.count('Missing character'),'capacity:',log.count('TeX capacity'))
print('pages:',re.findall(r'Output written on .*?\((\d+)',log))"
```

⚠️ **两个坑**：
1. `TEXINPUTS` 结尾分号不能省（Windows 用 `;` 分隔、结尾 `;` 表示追加默认路径）；
   Git Bash 里 `TEXINPUTS=... xelatex` 不生效，必须用 Python `subprocess` 传 env。
2. `\errorcontextlines=999` + 搜 `TeX capacity exceeded` 后的上下文，是定位
   递归类问题的唯一可靠手段——错误行号 `l.40` 指向的是 expl3 栈里的旧 token，
   **不是真实触发位置**，照着改会改错地方。

---

## 2026-09-30 会话：skill 自包含修复 + 工程护栏

### 本次完成

| # | 工作 | 文件 | 验证 |
|---|---|---|---|
| 1 | docstring 转义告警（`\mathtitle` → SyntaxWarning + GBK 乱码） | `office.py` | ✅ `--help` 无告警 |
| 2 | 路径回退失效（skill 拷走必崩 `FileNotFoundError`） | `office.py` / `template_registry.py` / `seed_builtins.py` | ✅ 五链路脱离仓库独立跑通 |
| 3 | 内嵌 cls 副本陈旧（缺 gov 段/公式字体修复/slides 链路） | skill `templates/` | ✅ 6 份副本 sha256 一致 |
| 4 | 4 份文档口径统一（README/CLAUDE/方案书/REPO_WIKI） | 多处 | ✅ 12 子命令一致、零死链 |
| 5 | 新增 `doctor` 自检（51 项，FAIL→exit 1） | `doctor.py` + `office.py` | ✅ 注入真 bug 验证有效 |
| 6 | **`.gitignore` 两处静默失效**（影响隐私屏蔽） | `.gitignore` | ✅ `check-ignore` 逐条实证 |
| 7 | REPO_WIKI 头部画像数字修正 + 改为实时统计 | `doctor.py` + `REPO_WIKI.md` | ✅ 时效检查 OK |

### 关键决策（勿轻易推翻）

- **不改 `_find_project_root` 的 `.trae`-skip 语义** —— REPO_WIKI §9 要求锚项目根，改了会让本仓库跑到分发副本上
- **cls 副本同步是单向的**（项目根 → skill），根是唯一事实来源
- **PPT 链路定调 beamer/PDF，不做可编辑 .pptx**（2026-09-18 拍板），`.pptx` 降 P3
- **`docs/` 只放回 REPO_WIKI**，方案书/调研报告仍本地保留（隐私考量）

### 踩坑（详见 CLAUDE.md 31-37）
1. `.gitignore` 目录级排除（`/docs/*`）会让 `!` 例外失效
2. 行尾注释会被并入模式，`!path  # 说明` 必须拆成两行
3. "未被跟踪" ≠ "规则在生效"——两者要分别断言
4. 护栏必须**注入真 bug** 验证有效，跑通不算

---

## 可复现验证命令

```bash
# 1) 全量自检（改模板/换机器/提交前必跑，有 FAIL 退出码 1）
python .trae/skills/harryopo-office/scripts/office.py doctor

# 2) 文档画像数字（更新 REPO_WIKI 头部时用这个，不要手写）
python .trae/skills/harryopo-office/scripts/office.py doctor --stats

# 3) 五链路回归（改动渲染相关代码后）
python .trae/skills/harryopo-office/scripts/office.py render output/examples/paper-showcase.md --format word,paper
python .trae/skills/harryopo-office/scripts/office.py render output/examples/gov-notice.md --format paper --gov
python .trae/skills/harryopo-office/scripts/office.py govcheck output/examples/gov-notice-paper.tex
# 预期：paper-showcase 291KB / gov 59KB / govcheck 10-10

# 4) 自包含验证（改 cls 同步逻辑后）
#    把 .trae/skills/harryopo-office/ 整个复制到无 templates/ 的临时目录跑 render

# 5) 提交前隐私自查
git diff --cached | grep -E '^\+' | grep -inE '[0-9]{8,11}|学号|@qq\.|api[_-]?key|secret|password'
```

---

## 下一步待办

| 优先级 | 事项 | 说明 |
|---|---|---|
| ~~中~~ | ~~chinese-book 691 条缺字形~~ | ✅ 2026-10-11 已解决（\newCJKfontfamily 语法陷阱，见当日会话节） |
| ~~低~~ | ~~chinese-book 边注 `\url` 不显示~~ | ✅ 2026-10-11 已解决（与缺字形同根因，3 处 FZFSJW 错误消失） |
| 低 | 恢复 `sibling=theorem` 共享编号 | 现在 proposition/lemma/corollary 各自独立编号。需升级 thmtools（本机 tlmgr 不在 PATH） |
| 低 | chinese-book 余 2 处 floatrow 处理期告警 | ✅ **输出已修复**（2026-10-11 第三轮）：三个 caption 全部恢复渲染（PyMuPDF 文本层+目检双确认）。修法=①kaocaption 开关泄漏修复（补 AtEndEnvironment{figure*}，钩子内只复位开关——钩子里 \RawFloats 会全局泄漏）②wide-fig 内容首行 \RawFloats（floatrow 不管理 figure*，标准 caption 走图下方）。剩余报错为处理期告警，不追零 |
| 低 | endcsname ×1 | ⚠️ 记档：markdown 包 glossaries 主题第三方交互（preamble 期，非致命，按"不动第三方包"原则记档） |
| 低 | ~~lstlisting 孤儿环境连锁~~ | ✅ 2026-10-11 已清（7→3）：paiban.tex 示例行含**字面 \end{lstlisting}**，扫描器按 token 匹配提前闭合环境。唯一可靠修法=内容行不出现完整序列（加空格/前后加字均无效——listings 比较忽略空白）；陷阱已写进源码注释 |
| 低 | 工作区残留 | ✅ 2026-10-11 已清：probe2.tex 删除（字体排错探针，任务完结）；templates/{book,math-notes,slides}/figures/ 图表副本入库（与 paper/figures 先例一致） |
| ~~中~~ | ~~把 `office.py doctor` 接进 CI~~ | ✅ 2026-11-01 落地在 `latex-render` job（分支试跑→Linux 读数暴露 `ls-files` 的 CJK 转义盲区→改 `-z` 后合并）。遗留：CI 端 5 个 WARN 是可选依赖缺失的诚实读数，不豁免 |
| **高** | slides 链路末遍 **Emergency stop**（6 条错误） | `convert.py` 的 slides 引擎把 MD 显示公式转义成 `\$$\text{sim}...$\$` 落进 verbatim 上下文（`templates/slides/report-showcase-e2e.tex:112`）。当前 slides PDF 是**前一遍**的产物，尾部可能不全——这是产物正确性问题，不是噪音。修完把 `check_tex_log` 从 WARN 升 FAIL 的门槛就近了 |
| 中 | book 链路 10 条错误 | `\newtheorem` 与 base.sty 重复建计数器（`\c@theorem` 等 5 条）、`FangSong/BI` 形状解析失败、一处 `\newcommand` 体内空行截断（`harryopo-book.cls:378`） |
| 中 | `--a5paper` 是假开关 | 实测 A4/A5 同为 595×842pt，生成的 tex 恒为 `\documentclass{harryopo-book}`；`office.py:601 render_book` 收到 `a5paper` 却没透传类选项。要么接通，要么把开关删掉（不许留"看着能用"的控件） |
| 中 | 架构图 `office-layers.html|png` 重绘（**待用户审核**） | 图上"11 subcommands · 4 chains"、交付物层含未实现的 `pptx`；按 diagram-design 流程改：层 03 编排 13 子命令、层 05 质检加 blindcheck/规则包/日志断言、层 06 交付物改为 docx/pdf(五类)/png；渲染出 PNG 先交用户确认再插文档 |
| P3 | Typst 0.15 第三输出通道 | 方案书 §6 长期储备 |
| P3 增补 | ~~规范包架构~~ ✅ 2026-10-11（rulepack_check.py + rules/gbt9704-2012.yaml + 自制指南，gov-notice 对照逐行一致） | 第四轮调研 Adopt |
| P3 增补 | ~~blindcheck 子命令~~ ✅ 2026-10-11（身份暴露点扫描：元信息/学号/邮箱/手机号/致谢基金/导师/路径，gov 示例命中 2/干净源 0 误报） | 第四轮调研 Adopt |
| P3 增补 | ~~SKILL.md frontmatter 四件套~~ ✅ 2026-10-11（when_to_use 正反例 + metadata version/tags；argument-hint 不适用非单命令 skill） | 第四轮调研 Adopt |
| P3 增补 | ~~skill 仓库 CI~~ ✅ 2026-10-11 全绿（.github/workflows/ci.yml：lint + latex-render 两 job。**首跑三坑留档**：①Actions 默认 bash -e——被检工具"有发现退出 1"会当场中断步骤，须 \|\| true 后断言计数 ②ubuntu texlive 分包：algorithm2e 在 texlive-science 不在 latex-extra ③YAML run 续行保留下一行前导空格——路径参数写单行；另 blindcheck 自检对照不能用其源码（规则转义序列被自身规则命中），对照文件用 rules/*.yaml） | 第四轮调研 Adopt |
| P3 | 可编辑 .pptx 输出链路 | 2026-09-18 降级项；python-pptx 1.0.3 + PowerPoint COM 本机可用 |
| P3 | 模板市场 / 多人协作 / pdfcpu / HermesOffice | 长期储备 |
| 低 | `code_hash` 单点收敛 | `mermaid_render` / `diagram_render` 各一份（2 行），已判定不值得动 |

---

## ❓ 待确认

- **GitHub 端缓存对象**：8-30 与 9-27 两轮 filter-repo 已清空历史中的 PII，但 GitHub 服务端的对象缓存需联系 Support 才能彻底清除。**只剩这一项**（fork 已于 2026-11-01 实测为 0，见当日会话节）。
- **历史备份 bundle**：`D:\ai\latex-history-backup-20260927.bundle` 已确认不存在（上一轮清理时已删）
