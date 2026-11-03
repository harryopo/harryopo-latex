"""自检库：环境体检 + 防回归护栏

存在理由（2026-09-30）：
1. **cls 双源漂移**——`templates/cls/` 与 `.trae/skills/harryopo-office/templates/cls/`
   是两份副本，而 `_find_project_root()` 刻意跳过 `.trae`，所以 skill 内那份在开发期
   永不被运行时读取，坏了不会报错。2026-09-30 实际发生过：内嵌副本缺 gov 公文段与
   base.sty 的 \\ifnum 公式字体修复。本模块的 `check_cls_sync` 就是为防复发。
2. **必含段检测**——`\\ifx` 恒假、gov 段丢失这类 bug 的共同点是"编译仍成功、结果静默错误"，
   靠肉眼看 PDF 很难发现，只能对源码做特征断言。
3. **环境体检**——把散落在 README/CLAUDE.md 里的环境前提收敛成一条可执行命令。

设计原则：纯标准库、无副作用（只读+diff）、退出码可用于 CI。
"""
import difflib
import hashlib
import os
import re
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

# ============================================================
# 结果收集
# ============================================================

OK, WARN, FAIL = 'OK', 'WARN', 'FAIL'
_ICON = {OK: '[ OK ]', WARN: '[WARN]', FAIL: '[FAIL]'}


class Report:
    """收集检查结果；counts 供调用方决定退出码"""

    def __init__(self):
        self.rows = []   # (level, 分类, 说明)

    def add(self, level, section, msg):
        self.rows.append((level, section, msg))

    def count(self, level):
        return sum(1 for r in self.rows if r[0] == level)

    def has(self, level):
        return self.count(level) > 0

    def render(self, title='harryopo-office 自检'):
        lines = [f'=== {title} ===\n']
        last = None
        for level, section, msg in self.rows:
            if section != last:
                lines.append(f'\n[{section}]')
                last = section
            lines.append(f'  {_ICON[level]} {msg}')
        n_ok, n_warn, n_fail = self.count(OK), self.count(WARN), self.count(FAIL)
        lines.append(f'\n=== 汇总: {n_ok} OK / {n_warn} WARN / {n_fail} FAIL ===')
        if n_fail:
            lines.append('有 FAIL 项——先修掉再提交（详见 docs/REPO_WIKI.md §8）')
        elif n_warn:
            lines.append('无 FAIL。WARN 项多为可选依赖缺失，按需安装即可')
        else:
            lines.append('全部通过')
        return '\n'.join(lines)


# ============================================================
# 路径（与 office.py 同源语义：跳 .trae，锚项目根）
# ============================================================

def _find_project_root(skill_dir: Path) -> Path:
    for parent in [skill_dir] + list(skill_dir.parents):
        if '.trae' in parent.parts:
            continue
        if (parent / 'templates' / 'cls').exists():
            return parent
    return skill_dir


# ============================================================
# 1. cls 双源漂移检测（防复发的核心）
# ============================================================

# cls 源码里必须存在的特征串。缺了就说明副本是旧的/被改坏了。
# 每一项都对应一个"编译能过但结果错"的静默 bug。
REQUIRED_SEGMENTS = {
    'harryopo-paper.cls': [
        (r'\\if@govmode',              'GB/T 9704 公文模式段（\\if@govmode 分支）'),
        (r'\\DeclareOption\{gov\}',    '公文模式选项声明'),
        (r'\\hrpapplyall',             '接入统一排版规范'),
        (r'tocloft',                   '目录需 tocloft（此前用 ctexart 默认目录，无层级无色）'),
    ],
    'harryopo-base.sty': [
        (r'\\ifnum\\harryopo@nomath=0', '公式字体判定（\\ifnum 修复；\\ifx 写法恒假会让 XITS Math 永不加载）'),
        (r'\\usetikzlibrary\{positioning\}', 'tikz 相对定位库（缺失报 PGF Math Error）'),
    ],
    'harryopo-slides.cls': [
        (r'\\LoadClass\[.*\]\{ctexbeamer\}', 'beamer 基类（\\LoadClass；.cls 用它而非 \\documentclass）'),
    ],
    # harryopo-typography 是五类共用的排版规范（2026-09-30 新增）。
    # 下列断言守护的是"删掉也不报错、只会让排版悄悄坏掉"的点：
    'harryopo-typography.sty': [
        (r'\\lstdefinestyle\{pystyle\}', 'Python 代码样式（用户明确要求：无行号）'),
        (r'numbers=none',                '代码块禁用行号（numbers=none）'),
        (r'frame=none',                  '代码块无边框（frame=none）'),
        (r'\\cftsecfont\}\{\\zihao\{4\}\\fzdbs',
                                        '目录一级条目用绝对字号（缺层级差即"缩放反了"）'),
        (r'\\cftsecpagefont\}\{\\normalfont\}', '目录页码用正文字号（不随条目放大）'),        (r'\\newcommand\{\\hrpLineSpread\}', '统一行距（mathnotes 此前完全没设，正文偏紧）'),
    ],
    'harryopo-report.cls': [
        (r'\\hrpapplyall',               '接入统一排版规范'),
        (r'\\hrptocsetup',               '目录走统一层级'),
    ],
    # harryopo-book 的三处静默失效点（均为实测踩出，删掉不会报错、
    # 只会让排版悄悄坏掉）：
    'harryopo-book.cls': [
        (r'\\LoadClass\[.*\]\{ctexbook\}',
         'ctexbook 基类（\\LoadClass；写成 \\documentclass 会静默失效）'),
        (r'\\numberwithin\{equation\}\{chapter\}',
         '公式章级编号（base.sty 是 section 级，book 不覆盖会编成"节.式"）'),
        (r'\\newmdenv', '教学盒子底板（mdframed；6 种盒子靠它，缺失则全部退化）'),
        (r'\\fancyhead\[L\]',
         '双面页眉（[L] 单槽 + \\ifodd 分流；用 [LE]/[RO] 会被 ctexbook 重映射）'),
        (r'\\newcommand\{\\bianzhu\}',
         '右侧旁注命令（\\bianzhu/\\bianzhutu，方案书规格要求）'),
    ],
}

# 必含段里住在 templates/ 其它子目录的模板（上面那张表按 templates/cls/ 取路径，
# 照不到 math-notes 独立体系）。2026-11-01 补：notes 链路每份 PDF 都带
# "! Undefined control sequence. \tightlist" 却照样出满页—— pandoc 注入的私有宏
# 无人定义，nonstopmode 把错误咽掉了。定义补进 cls，这里守它别再丢。
TEMPLATE_SEGMENTS = {
    'math-notes/harryopo-mathnotes.cls': [
        (r'\\providecommand\{\\tightlist\}',
         '\\tightlist 定义（pandoc 列表注入的私有宏，缺了列表间距静默丢失且日志报错）'),
    ],
}

# 需保持一致的文件（项目根为准，单向同步到 skill）
SYNC_FILES = [
    'cls/harryopo-base.sty',
    'cls/harryopo-typography.sty',
    'cls/harryopo-paper.cls',
    'cls/harryopo-report.cls',
    'cls/harryopo-slides.cls',
    'cls/harryopo-book.cls',
    'cls/flushend.sty',
    'math-notes/harryopo-mathnotes.cls',
    # notes 手写编译路径（templates/math-notes/md2latex.py）读这两份，
    # 与 scripts/pandoc 版分叉过（缺 $highlighting-macros$ → 60 条错误），纳入守护
    'math-notes/pandoc/mathnotes-template.latex',
    'math-notes/pandoc/mathnotes-table.lua',
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _same_tree(project_root: Path, skill_dir: Path) -> bool:
    """分发包模式判定：PROJECT_ROOT 回退到 SKILL_DIR 时，双源比对无意义。"""
    try:
        return project_root.resolve() == skill_dir.resolve()
    except OSError:
        return False


def check_cls_sync(project_root: Path, skill_dir: Path, rep: Report):
    """比对项目根与 skill 内嵌 templates/ 是否同步，并断言必含段存在"""
    skill_tpl = skill_dir / 'templates'

    if _same_tree(project_root, skill_dir):
        # 分发包模式：project_root 与 skill_dir 是同一目录，SYNC_FILES 的 a/b
        # 指向同一文件，sha 恒等——10 条"一致"是自比自的假绿（2026-11-03 审计）。
        # 改为 1 条带说明的 WARN；必含段断言仍真实执行（读同一份包内模板）。
        n_seg = (sum(len(v) for v in REQUIRED_SEGMENTS.values())
                 + sum(len(v) for v in TEMPLATE_SEGMENTS.values()))
        rep.add(WARN, 'cls 双源同步',
                f'分发包模式：无双源可比，跳过 sha 比对；必含段 {n_seg} 项仍生效')
    else:
        for rel in SYNC_FILES:
            a, b = project_root / 'templates' / rel, skill_tpl / rel
            if not a.exists():
                rep.add(FAIL, 'cls 双源同步', f'{rel}: 项目根缺失（异常）')
                continue
            if not b.exists():
                rep.add(FAIL, 'cls 双源同步', f'{rel}: skill 内嵌缺失 —— 拷走后该能力不可用')
                continue
            if _sha(a) == _sha(b):
                rep.add(OK, 'cls 双源同步', f'{rel}: 一致')
            else:
                diff = list(difflib.unified_diff(
                    a.read_text(encoding='utf-8', errors='replace').splitlines(),
                    b.read_text(encoding='utf-8', errors='replace').splitlines(),
                    lineterm='', n=0))
                changed = sum(1 for d in diff if d.startswith(('+', '-'))
                              and not d.startswith(('+++', '---')))
                rep.add(FAIL, 'cls 双源同步',
                        f'{rel}: 不一致（{changed} 行差异）→ 以项目根为准 cp 覆盖 skill 内嵌副本')

    # 必含段断言（对项目根那份查——它是唯一事实来源）
    for fname, segments in REQUIRED_SEGMENTS.items():
        p = project_root / 'templates' / 'cls' / fname
        if not p.exists():
            rep.add(FAIL, 'cls 必含段', f'{fname}: 文件不存在')
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        for pattern, desc in segments:
            if re.search(pattern, text):
                rep.add(OK, 'cls 必含段', f'{fname}: {desc}')
            else:
                rep.add(FAIL, 'cls 必含段', f'{fname}: 缺 {desc}')

    # templates/ 其它子目录里的模板必含段（路径按 templates/ 解析）
    for rel, segments in TEMPLATE_SEGMENTS.items():
        p = project_root / 'templates' / rel
        if not p.exists():
            rep.add(FAIL, 'cls 必含段', f'{rel}: 文件不存在')
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        for pattern, desc in segments:
            if re.search(pattern, text):
                rep.add(OK, 'cls 必含段', f'{rel}: {desc}')
            else:
                rep.add(FAIL, 'cls 必含段', f'{rel}: 缺 {desc}')


# ============================================================
# 2. 关键文件 / 目录存在性
# ============================================================

def check_paths(project_root: Path, skill_dir: Path, rep: Report):
    # 分发包模式下 PROJECT_ROOT 回退到 SKILL_DIR，这些路径实际都指向包内，
    # 标签仍写"项目根"会误导（检查逻辑本身不变，只改显示文案）
    root_label = '包内' if _same_tree(project_root, skill_dir) else '项目根'
    required = [
        (f'{root_label} templates/cls', project_root / 'templates' / 'cls'),
        (f'{root_label} templates/fonts', project_root / 'templates' / 'fonts'),
        (f'{root_label} templates/paper', project_root / 'templates' / 'paper'),
        (f'{root_label} templates/math-notes', project_root / 'templates' / 'math-notes'),
        (f'{root_label} templates/slides', project_root / 'templates' / 'slides'),
        ('skill SKILL.md', skill_dir / 'SKILL.md'),
        ('skill templates/cls', skill_dir / 'templates' / 'cls'),
        ('skill templates/fonts', skill_dir / 'templates' / 'fonts'),
        ('skill templates/slides', skill_dir / 'templates' / 'slides'),
        ('skill 内嵌 diagram-design', skill_dir / 'skills' / 'diagram-design'),
    ]
    # skill 自包含：seed_builtins 的 5 个内置模板源必须在包内，否则"拷走即用"
    # 模式（项目根不在场）下 template 注册表 4/5 条目静默 [SKIP]（2026-11-03 审计）
    for rel in ('paper/showcase-paper.tex', 'report/showcase-report.tex',
                'math-notes/example-note.tex', 'book/selftest-book.tex',
                'slides/example-defense.tex'):
        p = skill_dir / 'templates' / rel
        rep.add(OK if p.exists() else FAIL, '关键路径',
                f'skill 内置模板源 templates/{rel}: '
                + ('在位' if p.exists() else '缺失 ← 自包含模式 seed 会 SKIP'))
    for label, path in required:
        rep.add(OK if path.exists() else FAIL, '关键路径', f'{label}: {path}'
                + ('' if path.exists() else '  ← 缺失'))

    # 字体数量（24 个是基线，2026-09-30 起）：
    #   方正 6 + XITS 7 + Heros 4 + lmmono 1 + cour 1 = 19
    #   + JetBrains Mono 4（代码块等宽，SIL OFL 1.1）
    #   + LICENSE-JetBrainsMono.txt（字体许可说明，也计文件数）
    FONT_BASELINE = 24
    for label, path in ((f'{root_label} fonts', project_root / 'templates' / 'fonts'),
                        ('skill fonts', skill_dir / 'templates' / 'fonts')):
        if not path.exists():
            continue
        n = len([f for f in path.iterdir() if f.is_file()])
        rep.add(OK if n == FONT_BASELINE else WARN, '关键路径', f'{label}: {n} 个字体'
                + ('' if n == FONT_BASELINE
                   else f'（基线 {FONT_BASELINE}，差 {n - FONT_BASELINE:+d}）'))


# ============================================================
# 3. 工具链探测
# ============================================================

def check_toolchain(rep: Report):
    # 外部命令
    for cmd, level, hint in [
        ('xelatex',  FAIL,  'LaTeX 链路必需（TeX Live / TinyTeX）'),
        ('pandoc',   WARN,  'notes 链路主引擎（缺失回退 md2latex.py 纯 Python 引擎）'),
        ('mmdc',     WARN,  'mermaid 渲染（npm i -g @mermaid-js/mermaid-cli）'),
    ]:
        found = shutil.which(cmd)
        rep.add(OK if found else level, '工具链',
                f'{cmd}: {found or "未安装"}' + ('' if found else f'  ← {hint}'))

    # 浏览器（图表 PNG 渲染靠 playwright chromium 或系统浏览器）
    has_chromium = any(os.path.exists(p) for p in (
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/usr/bin/google-chrome', '/usr/bin/chromium'))
    rep.add(OK if has_chromium else WARN, '工具链',
            '系统浏览器: ' + ('已找到' if has_chromium else '未找到（playwright chromium 可兜底）'))

    # Python 依赖
    for mod, level, why in [
        ('docx',       FAIL, 'Word 链路必需（pip install python-docx）'),
        ('latex2mathml', WARN, '公式转 OMML（pip install latex2mathml）'),
        ('win32com',   WARN, 'Word COM 导出 PDF / 实时修订（pywin32，Windows 限定）'),
        ('pymupdf',    WARN, '证据回溯 trace + 字体护栏（pip install pymupdf）'),
        ('playwright', WARN, 'diagram-design HTML→PNG（pip install playwright）'),
    ]:
        try:
            __import__(mod)
            rep.add(OK, 'Python 依赖', f'{mod}: 已安装')
        except ImportError:
            rep.add(level, 'Python 依赖', f'{mod}: 未安装  ← {why}')


# ============================================================
# 4. 隐私护栏：确认敏感目录确实没被 git 跟踪
# ============================================================

# 这些目录 2026-09-30 决策停止跟踪；doctor 顺带确认没被误 add
SENSITIVE_PATHS = [
    '蒸馏区', 'memory', '.learnings', 'CLAUDE.md',
    '简历', 'test-e2e', 'test-e2e-v2', '测试区', '.qoder',
]


def check_privacy(project_root: Path, rep: Report):
    try:
        # -z 是安全性质不是风格问题：默认 core.quotePath=true 会把非 ASCII 路径
        # 转义成 "\345\217\202\350\200\203/..."（带引号），于是 '蒸馏区/' 这类
        # CJK 敏感目录永远匹配不上 SENSITIVE_PATHS —— 隐私闸会"全 OK"地漏掉
        # 真的被跟踪了的个人材料。本机配了 quotePath=false 所以看不出来，
        # 2026-11-01 CI（默认 true）跑出来才暴露。-z 用 NUL 分隔，永不转义。
        out = subprocess.run(['git', '-C', str(project_root), 'ls-files', '-z'],
                             capture_output=True, text=True,
                             encoding='utf-8', errors='replace', timeout=30)
        if out.returncode != 0:
            rep.add(WARN, '隐私护栏', 'git ls-files 执行失败，跳过检查')
            return
        tracked = {f for f in out.stdout.split('\0') if f}
    except (OSError, subprocess.SubprocessError):
        rep.add(WARN, '隐私护栏', 'git 不可用，跳过检查')
        return

    for rel in SENSITIVE_PATHS:
        leaked = [f for f in tracked if f == rel or f.startswith(rel + '/')]
        if leaked:
            rep.add(FAIL, '隐私护栏',
                    f'{rel}/ 被 git 跟踪（{len(leaked)} 个文件）——含个人开发材料，勿外传')
        else:
            rep.add(OK, '隐私护栏', f'{rel}/ 未被跟踪')

    # gitignore 规则有效性：目录级排除 + 行尾注释是两类经典失效
    # （① `/docs/*` 排除目录本身，git 不下降，后续 `!` 对目录内文件无效；
    #   ② `!pattern  # 说明` 的注释被当成模式的一部分）
    # 若敏感路径"未被跟踪"却是因为规则写坏了，等于根本没在屏蔽——必须单独断言。
    for rel in SENSITIVE_PATHS:
        p = project_root / rel
        if not p.exists():
            continue
        try:
            r = subprocess.run(['git', '-C', str(project_root), 'check-ignore', '-q', rel],
                               capture_output=True, timeout=20)
            if r.returncode == 0:
                rep.add(OK, 'gitignore 有效性', f'{rel}/ 规则生效（已被忽略）')
            else:
                rep.add(WARN, 'gitignore 有效性',
                        f'{rel}/ 未被 gitignore 覆盖——当前无文件被跟踪，但规则缺失，'
                        f'新增文件会被误提交')
        except (OSError, subprocess.SubprocessError):
            rep.add(WARN, 'gitignore 有效性', 'git 不可用，跳过规则检查')


def check_syntax(skill_dir: Path, rep: Report):
    """规范 3.2 第 1-2 步：语法检查 + 类型检查（本项目无 linter/type checker，
    用 ast.parse 在 SyntaxWarning 升级为异常的模式下手写这两项）。

    `-W error::SyntaxWarning` 等价于把非法转义告警当错误——本项目历史上
    多次踩到 `\\h` / `\\mathx` 这类非 raw docstring 与正则的非法转义
    （CLAUDE.md 踩坑 27/31），靠默认告警容易被忽略。
    """
    import ast
    scripts = sorted(p for p in (skill_dir / 'scripts').rglob('*.py')
                     if '__pycache__' not in p.parts)
    bad = []
    for p in scripts:
        try:
            src = p.read_text(encoding='utf-8', errors='replace')
            with warnings.catch_warnings():
                warnings.simplefilter('error', SyntaxWarning)
                ast.parse(src, filename=str(p))
        except SyntaxWarning as e:
            bad.append(f'{p.name}: 非法转义 {e.msg}')
        except SyntaxError as e:
            bad.append(f'{p.name}:{e.lineno}: {e.msg}')
        except OSError as e:
            bad.append(f'{p.name}: 读取失败 {e}')
    if bad:
        for b in bad:
            rep.add(FAIL, '语法检查', b)
    else:
        rep.add(OK, '语法检查', f'{len(scripts)} 个脚本零 SyntaxWarning / SyntaxError')


# ============================================================
# 5. 仓库画像统计（供 REPO_WIKI 头部引用，避免手写数字漂移）
# ============================================================

def collect_stats(project_root: Path) -> dict:
    """实时统计仓库画像。不手写、不缓存——文档引用这些数字时用
    `office.py doctor --stats` 取当前值，杜绝"声明与实际脱节"。

    py_files 拆两个口径，避免把参考仓库/工具脚本算进核心：
    - py_core：harryopo-office skill 自身（自研产品代码）
    - py_other：其余（shared 几何库、tikz converter、参考资料脚本等）
    """
    stats = {'tracked_files': 0, 'py_core': 0, 'py_other': 0,
             'py_lines': 0, 'md_files': 0}
    try:
        out = subprocess.run(['git', '-C', str(project_root), 'ls-files', '-z'],
                             capture_output=True, text=True,
                             encoding='utf-8', errors='replace', timeout=30)
        if out.returncode == 0:
            # -z 而非按行：默认 core.quotePath=true 的机器（CI ubuntu）上 CJK 路径
            # 会被转义成 "\345\217\202..." 带引号一项，行数不变但按 endswith('.md')
            # 与 Path 取数会全体漏掉——本机恰好配了 quotePath=false 所以照不出来。
            files = [f for f in out.stdout.split('\0') if f]
            stats['tracked_files'] = len(files)
            stats['md_files'] = sum(1 for f in files if f.endswith('.md'))
            for f in files:
                if not f.endswith('.py'):
                    continue
                # 只统计入库文件，避免本地产物混入
                if 'harryopo-office/scripts/' in f.replace('\\', '/'):
                    stats['py_core'] += 1
                else:
                    stats['py_other'] += 1
                p = project_root / f
                try:
                    stats['py_lines'] += len(
                        p.read_text(encoding='utf-8', errors='replace').splitlines())
                except OSError:
                    pass
    except (OSError, subprocess.SubprocessError):
        pass
    return stats


def render_stats_line(project_root: Path) -> str:
    """生成 REPO_WIKI 头部那一行画像（可直接粘贴）"""
    s = collect_stats(project_root)
    return (f"> 生成方式：AI 全仓遍历（{s['tracked_files']} 个入库文件，"
            f"核心为 {s['py_core']} 个 Python 脚本（skill 自研）"
            f"+ {s['py_other']} 个辅助脚本，共 ~{s['py_lines']} 行 + "
            f"LaTeX 模板体系 + {s['md_files']} 篇文档）")


def check_stats_freshness(project_root: Path, rep: Report, wiki_rel='docs/REPO_WIKI.md'):
    """时效标记检查（规范 4.4「过期信息自动降级为待核验」）：
    逐个比对 Wiki 头部画像行里的每个数字与实际，不一致即 WARN。

    四个数字全查而非只查文件数——`py_lines` 尤其易漂：改一次 doctor.py
    自身行数就变。只查一个数字等于给假安全感。
    """
    wiki = project_root / wiki_rel
    if not wiki.exists():
        return
    text = wiki.read_text(encoding='utf-8', errors='replace')
    s = collect_stats(project_root)

    # 声明值：（顺序固定）入库文件数 / skill 自研脚本数 / 辅助脚本数 / 行数 / 文档数
    patterns = [
        (r'（(\d+)\s*个入库文件', s['tracked_files'], '入库文件数'),
        (r'核心为\s*(\d+)\s*个 Python 脚本', s['py_core'], 'skill 自研脚本数'),
        (r'\+\s*(\d+)\s*个辅助脚本', s['py_other'], '辅助脚本数'),
        (r'共\s*~(\d+)\s*行', s['py_lines'], 'Python 行数'),
        (r'\+\s*(\d+)\s*篇文档', s['md_files'], '文档篇数'),
    ]
    missing, drift = [], []
    for pat, actual, label in patterns:
        m = re.search(pat, text)
        if not m:
            missing.append(label)
            continue
        claimed = int(m.group(1))
        if claimed != actual:
            drift.append(f'{label} 声明 {claimed} / 实际 {actual}（{actual - claimed:+d}）')

    if missing:
        rep.add(WARN, '文档时效',
                f'{wiki_rel} 头部画像行缺字段：{"、".join(missing)}——'
                f'用 `office.py doctor --stats` 取当前值整行替换')
    if drift:
        rep.add(WARN, '文档时效',
                f'{wiki_rel} 头部画像已漂移：{"；".join(drift)}——'
                f'用 `office.py doctor --stats` 取当前值整行替换')
    if not missing and not drift:
        rep.add(OK, '文档时效',
                f'{wiki_rel} 头部画像 5 项全部与实际一致'
                f'（{s["tracked_files"]} 文件 / {s["py_core"]}+{s["py_other"]} 脚本 / '
                f'~{s["py_lines"]} 行 / {s["md_files"]} 文档）')


# ============================================================
# 6. 文档口径一致性（子命令数量与清单）
# ============================================================

def canonical_subcommands(skill_dir: Path) -> list:
    """从 office.py 源码直取 `sub.add_parser('name', ...)` 的注册名。

    不跑 `office.py --help`：doctor 本身就是 office.py 以子进程调起的，
    再反向调一次是自嵌套，且解析 argparse 输出比解析注册点脆。
    """
    office_py = skill_dir / 'scripts' / 'office.py'
    try:
        src = office_py.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return []
    return re.findall(r"sub\.add_parser\('([a-z_]+)'", src)


def check_doc_command_claims(project_root: Path, skill_dir: Path, rep: Report):
    """文档写的子命令数量与清单必须与 office.py 实际注册一致。

    存在理由（2026-10-31）：本模块原先只校验 REPO_WIKI 头部那 4 个画像数字，
    "N 子命令"这类手写数字没有任何闸在看——顺着一个被报出来的漂移横扫，
    又抓到 REPO_WIKI 目录树写 12（实际 13）、§3.1 清单漏列 `doctor` 两处。
    只覆盖「对外现状面」（README 中英 / REPO_WIKI / SKILL.md）：
    `.ai/HANDOFF.md` 与 memory 流水里的是**历史读数**，按"不改写诊断历史"原则排除。
    """
    cmds = canonical_subcommands(skill_dir)
    if len(cmds) < 5:
        rep.add(WARN, '文档口径',
                '未从 office.py 解析出子命令注册表（`sub.add_parser` 形态变了？），跳过口径检查')
        return

    docs = [('README.md', project_root / 'README.md'),
            ('README.en.md', project_root / 'README.en.md'),
            ('docs/REPO_WIKI.md', project_root / 'docs' / 'REPO_WIKI.md'),
            ('SKILL.md', skill_dir / 'SKILL.md')]
    present = [(label, p) for label, p in docs if p.is_file()]
    if not present:
        rep.add(WARN, '文档口径', '四份现状面文档都不在（独立分发副本？），跳过口径检查')
        return

    problems = []
    for label, path in present:
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        # a) 数量声明：任何 "N 子命令 / N subcommands" 都要等于实际数
        for i, ln in enumerate(lines):
            for m in re.finditer(r'(\d+)\s*个?\s*(?:子命令|subcommands)', ln):
                if int(m.group(1)) != len(cmds):
                    problems.append(f'{label}:{i + 1} 声明 {m.group(1)} 子命令，'
                                    f'实际 {len(cmds)} 个')
        # b) 清单完整性：一段文字里出现 ≥6 成真实命令名，才认定它"在列举全部子命令"
        #    （阈值随实际数浮动）。低于阈值的是特性散文（如"redline + revise + live 三态闭环"），
        #    它们没有穷举承诺，拿去要求列齐 13 个只会造出假 FAIL。
        #    命中后向前跳 3 行，避免同一份清单被折行窗口重复报成两个缺陷。
        threshold = max(5, -(-len(cmds) * 6 // 10))   # 向上取整的 60%
        i = 0
        while i < len(lines):
            if sum(1 for c in cmds if re.search(r'\b' + c + r'\b', lines[i])) >= 3:
                window = '\n'.join(lines[i:i + 3])
                in_window = [c for c in cmds if re.search(r'\b' + c + r'\b', window)]
                if len(in_window) >= threshold:
                    miss = [c for c in cmds if c not in in_window]
                    if miss:
                        problems.append(f'{label}:{i + 1} 子命令清单漏列 ' + ' / '.join(miss))
                i += 3
            else:
                i += 1
    # 完全相同的读数只报一次
    uniq = list(dict.fromkeys(problems))

    if uniq:
        for p in uniq:
            rep.add(FAIL, '文档口径', p + '——改文档对齐 `office.py --help`')
    else:
        rep.add(OK, '文档口径',
                f'{len(present)} 份现状面文档的子命令数量与清单全部与实际一致'
                f'（{len(cmds)} 个：{"/".join(cmds)}）')


def check_lane_claims(project_root: Path, skill_dir: Path, rep: Report):
    """链路清单口径：现状面文档列举的 lane 必须与 office.py 的渲染入口一致。

    五条链路 = word / paper（含 --type report）/ notes / slides / book。
    存在理由（2026-11-03 审计）：README.md:128 与 README.en.md:128 长期写
    `word` / `paper` / `notes` / `report` / `slides`（漏 book、把 report 当独立
    链路）；check_doc_command_claims 只守子命令数，链路清单漂移无人看。
    判据：一行里连续列举 ≥3 个反引号 lane 名，才算"在承诺链路清单"；
    散文提及（如"redline + revise + live 三态"）不触发。
    """
    docs = [('README.md', project_root / 'README.md'),
            ('README.en.md', project_root / 'README.en.md'),
            ('docs/REPO_WIKI.md', project_root / 'docs' / 'REPO_WIKI.md'),
            ('SKILL.md', skill_dir / 'SKILL.md')]
    problems = []
    for label, path in docs:
        if not path.is_file():
            continue
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        for i, ln in enumerate(lines, 1):
            toks = re.findall(r'`([a-zA-Z-]+)`', ln)
            lane_toks = [t for t in toks
                         if t in ('word', 'paper', 'notes', 'report', 'slides', 'book')]
            if len(lane_toks) < 3:
                continue
            joined = ' / '.join(lane_toks)
            if 'book' not in lane_toks:
                problems.append(f'{label}:{i} 链路清单漏 book（{joined}）')
            if 'report' in lane_toks and '--type report' not in ln:
                problems.append(f'{label}:{i} 把 report 当独立链路（{joined}）'
                                f'——report 是 paper 的 --type 变体')
    uniq = list(dict.fromkeys(problems))
    if uniq:
        for p in uniq:
            rep.add(FAIL, '链路口径', p)
    else:
        rep.add(OK, '链路口径',
                '现状面文档的链路清单与渲染入口一致'
                '（word / paper(含 --type report) / notes / slides / book）')


# ============================================================
# 7. 凭据形态扫描（入库内容级）
# ============================================================

# (标签, 编译好的正则)。前六条是**固定形状**，几乎不存在假阳性；
# 最后一条"赋值型"要求右值是引号字面量且 >=16 位且含数字或符号——
# 因为 `token = text.split(...)` 这类普通变量赋值在本仓库合法存在，
# 不加这个形状约束会天天误报（判据要能证伪，也要能被放过）。
CREDENTIAL_PATTERNS = [
    ('AWS AKIA', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('GitHub token', re.compile(r'\b(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}\b')),
    ('OpenAI sk-', re.compile(r'\bsk-[A-Za-z0-9]{20,}\b')),
    ('私钥块', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('JWT', re.compile(r'\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b')),
    ('带密码的 URL', re.compile(r'://[^/\s:@]+:[^/\s:@]{3,}@[A-Za-z0-9.\-]+')),
    ('IM webhook', re.compile(r'(?i)hooks\.slack\.com|oapi\.dingtalk\.com/robot|discord\.com/api/webhooks')),
    ('赋值型字面量', re.compile(
        r'(?i)\b(api[_-]?key|secret|passwd|password|access[_-]?token|'
        r'private[_-]?token|client[_-]?secret)\b\s*[:=]\s*(["\'])([^"\'\s]{16,})\2')),
]


def check_credentials(project_root: Path, skill_dir: Path, rep: Report):
    """扫文本文件里的凭据形状——命中即 FAIL。

    存在理由：本仓库是公开仓库，隐私护栏查的是"个人材料目录有没有被跟踪"，
    但**已跟踪文件的内容里混进 token** 是另一条独立出口（脚本改环境、示例配置、
    复制粘贴的链接都可能带进来），按出口枚举必须单独立一条。
    分发包模式（无 .git）：凭据是内容级风险，不依赖版本控制，退化为
    rglob 扫描 skill 目录文本文件（2026-11-03 审计：原先无 git 直接跳过，
    分发件被塞 token 会漏）。
    已知边界：二进制（docx/pdf/png/字体）按 NUL 嗅探跳过——OOXML 里塞凭据这条
    路本检查照不到，只能靠 review；扫描上限 3MB。
    """
    tracked = None
    try:
        out = subprocess.run(['git', '-C', str(project_root), 'ls-files', '-z'],
                             capture_output=True, text=True,
                             encoding='utf-8', errors='replace', timeout=30)
        if out.returncode == 0:
            tracked = [f for f in out.stdout.split('\0') if f]
    except (OSError, subprocess.SubprocessError):
        tracked = None

    if tracked is not None:
        files = [project_root / rel for rel in tracked]
        base = project_root
        scope = f'{len(tracked)} 个入库文本文件'
    else:
        # 分发包模式：无 .git → 扫 skill 目录本身；压缩包/字体/图片按后缀跳过
        # （避免把 16MB zip 读进内存），其余二进制仍由 NUL 嗅探兜底。
        files = []
        for p in skill_dir.rglob('*'):
            if not p.is_file():
                continue
            if '.git' in p.parts or '__pycache__' in p.parts:
                continue
            if p.suffix.lower() in ('.zip', '.docx', '.pdf', '.png', '.jpg', '.jpeg',
                                    '.gif', '.webp', '.ttf', '.otf', '.woff', '.woff2'):
                continue
            files.append(p)
        base = skill_dir
        scope = f'{len(files)} 个包内文本文件（无 .git，本地目录扫描）'

    hits = []
    scanned = 0
    for p in files:
        try:
            if not p.is_file() or p.stat().st_size > 3_000_000:
                continue
            raw = p.read_bytes()
        except OSError:
            continue
        if b'\x00' in raw[:8192]:          # 二进制：内容级扫描照不到，见 docstring
            continue
        text = raw.decode('utf-8', errors='replace')
        scanned += 1
        rel = os.path.relpath(str(p), str(base)).replace(os.sep, '/')
        for label, rx in CREDENTIAL_PATTERNS:
            for m in rx.finditer(text):
                if label == '赋值型字面量':
                    value = m.group(3)
                    if not re.search(r'[0-9!@#$%^&*+=_/\\]', value):
                        continue          # 纯字母值（如示例里的 your-key-name）不当凭据
                line = text[:m.start()].count('\n') + 1
                hits.append(f'{rel}:{line} 命中「{label}」')

    if hits:
        # 不截断：截断读数会藏掉整族缺陷（本项目踩过）
        for h in hits:
            rep.add(FAIL, '凭据形态', h + '——公开仓库不许出现凭据，轮换后删除')
    else:
        rep.add(OK, '凭据形态',
                f'{scope} 零凭据形状命中（扫描 {scanned} 个；8 类形态；二进制跳过，上限 3MB）')


# ============================================================
# 8. TeX 宏名合法性（控制序列名不能含数字）
# ============================================================

# LaTeX 的控制序列名只认字母：`\hrpH1Size` 会被切成 `\hrpH` + `1Size`，
# 定义不成立，`1Size` 还会被当正文排出——2026-11-01 就是这条让五类链路
# 每次编译顶出 40+ 条错误（全被 nonstopmode 咽掉，PDF 看着正常）。
# 只查"定义处"，使用处交给编译日志断言（check_tex_log）。
TEX_BAD_NAME_RE = re.compile(
    r'\\(?:renewcommand|newcommand|providecommand|DeclareRobustCommand)\s*\{?\s*\\'
    r'([A-Za-z@]*[0-9][A-Za-z0-9]*)|\\def\s*\\([A-Za-z@]*[0-9][A-Za-z0-9]*)')


def check_tex_macro_names(project_root: Path, rep: Report):
    """断言模板里没有"名字含数字"的宏定义。"""
    bad = []
    scanned = 0
    for rel in SYNC_FILES:
        p = project_root / 'templates' / rel
        if not p.exists():
            continue
        scanned += 1
        for i, line in enumerate(
                p.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if line.lstrip().startswith('%'):
                continue
            code = line.split('%')[0]
            m = TEX_BAD_NAME_RE.search(code)
            if m:
                name = m.group(1) or m.group(2)
                stem = re.match(r'[A-Za-z@]*', name).group(0)
                bad.append(f'{rel}:{i} 宏名 `\\{name}` 含数字'
                           f'——TeX 会切成 `\\{stem}` + `{name[len(stem):]}`')
    if bad:
        for b in bad:
            rep.add(FAIL, '宏名合法性', b + '，改名用英文数词（One/Two/Three）')
    else:
        rep.add(OK, '宏名合法性',
                f'{scanned} 份模板无含数字的宏名定义（控制序列名只认字母）')


# ============================================================
# 入口
# ============================================================
def run_doctor(project_root: Path, skill_dir: Path, skip_privacy=False):
    rep = Report()
    check_syntax(skill_dir, rep)
    check_paths(project_root, skill_dir, rep)
    check_cls_sync(project_root, skill_dir, rep)
    check_toolchain(rep)
    if not skip_privacy:
        check_privacy(project_root, rep)
    check_stats_freshness(project_root, rep)
    check_doc_command_claims(project_root, skill_dir, rep)
    check_lane_claims(project_root, skill_dir, rep)
    check_credentials(project_root, skill_dir, rep)
    check_tex_macro_names(project_root, rep)
    return rep


def main():
    import argparse
    ap = argparse.ArgumentParser(description='harryopo-office 自检（环境 + 防回归护栏）')
    ap.add_argument('--skip-privacy', action='store_true', help='跳过 git 跟踪检查')
    ap.add_argument('--json', action='store_true', help='输出 JSON（供 AI 消费）')
    ap.add_argument('--stats', action='store_true',
                    help='只输出仓库画像统计（供文档引用，避免手写数字漂移）')
    args = ap.parse_args()

    here = Path(__file__).resolve()
    skill_dir = here.parent.parent
    project_root = _find_project_root(skill_dir)

    if args.stats:
        print(render_stats_line(project_root))
        return 0

    rep = run_doctor(project_root, skill_dir, skip_privacy=args.skip_privacy)

    if args.json:
        import json
        print(json.dumps({
            'project_root': str(project_root),
            'fail': rep.count(FAIL), 'warn': rep.count(WARN), 'ok': rep.count(OK),
            'items': [{'level': lv, 'section': sec, 'message': m}
                      for lv, sec, m in rep.rows],
        }, ensure_ascii=False, indent=2))
    else:
        print(rep.render())

    return 1 if rep.has(FAIL) else 0


if __name__ == '__main__':
    sys.exit(main())
