# HANDOFF — 会话交接记录

> 规范：每次会话结束更新本文件。**代码是唯一真值源**，本文件是导航与线索。
> 置信度标记：✅ 已验证（有命令/文件为证）· ⚠️ 进行中 · ❓ 待确认

---

## 当前状态速览

| 项 | 值 | 置信度 |
|---|---|---|
| 项目 | harryopo 办公文档 AI 生产力平台 | ✅ |
| 阶段 | **维护期**（P0 3/3 · P1 6/6 · P2 5/5 收官；P3 四项未启动） | ✅ |
| 交付形态 | 自包含 Agent Skill，12 个子命令 | ✅ |
| 健康检查基线 | `office.py doctor` → **51 OK / 0 WARN / 0 FAIL** | ✅ |
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
| P3 | Typst 0.15 第三输出通道 | 方案书 §6 长期储备 |
| P3 | 可编辑 .pptx 输出链路 | 2026-09-18 降级项；python-pptx 1.0.3 + PowerPoint COM 本机可用 |
| P3 | 模板市场 / 多人协作 / pdfcpu / HermesOffice | 长期储备 |
| 低 | `harryopo-book.cls` | 书籍文档类，方案书未列入 P3 |
| 低 | `code_hash` 单点收敛 | `mermaid_render` / `diagram_render` 各一份（2 行），已判定不值得动 |

---

## ❓ 待确认

- **GitHub 端缓存对象**：8-30 与 9-27 两轮 filter-repo 已清空历史中的 PII，但 GitHub 服务端的对象缓存需联系 Support 才能彻底清除。是否需要处理？
- **历史备份 bundle**：`D:\ai\latex-history-backup-20260927.bundle` 已确认不存在（上一轮清理时已删）
