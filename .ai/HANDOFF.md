# HANDOFF — 会话交接记录

> 规范：每次会话结束更新本文件。**代码是唯一真值源**，本文件是导航与线索。
> 置信度标记：✅ 已验证（有命令/文件为证）· ⚠️ 进行中 · ❓ 待确认

---

## 当前状态速览

| 项 | 值 | 置信度 |
|---|---|---|
| 项目 | harryopo 办公文档 AI 生产力平台 | ✅ |
| 阶段 | **维护期**（P0 3/3 · P1 6/6 · P2 5/5 收官；P3 四项未启动） | ✅ |
| 交付形态 | 自包含 Agent Skill，12 个子命令 / 5 条输出链路（word·paper·notes·slides·book） | ✅ |
| 健康检查基线 | `office.py doctor` → **68 OK / 0 WARN / 0 FAIL** | ✅ |
| chinese-book | 缺字形已清零（2026-10-11，691→0）；错误 7→**3**（lstlisting 孤儿环境连锁已清，余 2 floatrow + 1 endcsname，见待办表） | ✅ |
| 远程同步 | `origin/main` = 本地 HEAD（2026-10-11 接手轮发现 6 commit 漏推，已补推核验） | ✅ |

---

## 权威文档导航（先查这里，别读记忆文件当真值）

| 文件 | 角色 | 入库 |
|---|---|---|
| `docs/REPO_WIKI.md` | **架构地图 + 能力清单 + API + 技术债**（接手先读 §4 能力清单防重复造轮子、§9 复用指引） | ✅ |
| `.trae/skills/harryopo-office/SKILL.md` | AI 行为契约：触发词、主流程、全部排版约定 | ✅ |
| `CLAUDE.md` | 项目铁律 + 37 条踩坑警示（**本地未入库**） | ❌ |
| `memory/MEMORY.md` | 会话流水（1180 行，**本地未入库**，只作参考） | ❌ |

> ⚠️ **已知反模式**：`CLAUDE.md` / `MEMORY.md` 在 `.gitignore` 内，克隆仓库的人看不到。涉及项目铁律时，优先读已入库的 `SKILL.md` + `REPO_WIKI.md`。

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
（无效法清单防止后人重走），本次 4 个无效修法已写进待办表。

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
| 低 | chinese-book 余 3 个错误 | ①floatrow "Caption(s) lost" ×2（wide-fig 的 figure* 未被 floatrow 管理 + yinyong 表，**边栏标题真丢**）：已试 4 法均无效（figure*→figure 连坐新错 / floatsetup[figure*]（未注册类型）/ \centering 前置（无关））；类里 widefigure 环境未定义（floatsetup 条目是死配置），可行方向=自建 widefigure（floatrow DeclareNewFloatType）或细读 kaocaption toggle（kaoCJKsc.sty:664）②endcsname ×1=markdown 包 glossaries 主题第三方交互（preamble 期，非致命，按"不动第三方包"原则记档） |
| 低 | ~~lstlisting 孤儿环境连锁~~ | ✅ 2026-10-11 已清（7→3）：paiban.tex 示例行含**字面 \end{lstlisting}**，扫描器按 token 匹配提前闭合环境。唯一可靠修法=内容行不出现完整序列（加空格/前后加字均无效——listings 比较忽略空白）；陷阱已写进源码注释 |
| 低 | 工作区残留 | ✅ 2026-10-11 已清：probe2.tex 删除（字体排错探针，任务完结）；templates/{book,math-notes,slides}/figures/ 图表副本入库（与 paper/figures 先例一致） |
| P3 | Typst 0.15 第三输出通道 | 方案书 §6 长期储备 |
| P3 | 可编辑 .pptx 输出链路 | 2026-09-18 降级项；python-pptx 1.0.3 + PowerPoint COM 本机可用 |
| P3 | 模板市场 / 多人协作 / pdfcpu / HermesOffice | 长期储备 |
| 低 | `code_hash` 单点收敛 | `mermaid_render` / `diagram_render` 各一份（2 行），已判定不值得动 |

---

## ❓ 待确认

- **GitHub 端缓存对象**：8-30 与 9-27 两轮 filter-repo 已清空历史中的 PII，但 GitHub 服务端的对象缓存需联系 Support 才能彻底清除。是否需要处理？
- **历史备份 bundle**：`D:\ai\latex-history-backup-20260927.bundle` 已确认不存在（上一轮清理时已删）
