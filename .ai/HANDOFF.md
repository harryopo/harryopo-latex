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
| chinese-book | 编译中断已解除（58 页完整输出），余 691 条缺字形待查 | ⚠️ |
| 远程同步 | `origin/main` = 本地 HEAD | ✅ |

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
| **中** | chinese-book 691 条缺字形 | 2026-10-05 遗留。集中在 `zimubiao`/`fulu` 两章表格内 `\lstinline` 混排；最小样例复现不出，需在完整类下 `\errorcontextlines` 二分。只影响 PDF 文本层，不影响编译与页数 |
| 低 | chinese-book 边注 `\url` 不显示 | 3 处 fontspec FZFSJW 查找失败；边注文字正常，仅 URL 丢失。延迟展开 + 内嵌字体无系统名导致 |
| 低 | 恢复 `sibling=theorem` 共享编号 | 现在 proposition/lemma/corollary 各自独立编号。需升级 thmtools（本机 tlmgr 不在 PATH） |
| P3 | Typst 0.15 第三输出通道 | 方案书 §6 长期储备 |
| P3 | 可编辑 .pptx 输出链路 | 2026-09-18 降级项；python-pptx 1.0.3 + PowerPoint COM 本机可用 |
| P3 | 模板市场 / 多人协作 / pdfcpu / HermesOffice | 长期储备 |
| 低 | `code_hash` 单点收敛 | `mermaid_render` / `diagram_render` 各一份（2 行），已判定不值得动 |

---

## ❓ 待确认

- **GitHub 端缓存对象**：8-30 与 9-27 两轮 filter-repo 已清空历史中的 PII，但 GitHub 服务端的对象缓存需联系 Support 才能彻底清除。是否需要处理？
- **历史备份 bundle**：`D:\ai\latex-history-backup-20260927.bundle` 已确认不存在（上一轮清理时已删）
