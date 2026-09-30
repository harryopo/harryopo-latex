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
    ],
    'harryopo-base.sty': [
        (r'\\ifnum\\harryopo@nomath=0', '公式字体判定（\\ifnum 修复；\\ifx 写法恒假会让 XITS Math 永不加载）'),
        (r'\\usetikzlibrary\{positioning\}', 'tikz 相对定位库（缺失报 PGF Math Error）'),
    ],
    'harryopo-slides.cls': [
        (r'\\LoadClass\[.*\]\{ctexbeamer\}', 'beamer 基类（\\LoadClass；.cls 用它而非 \\documentclass）'),
    ],
}

# 需保持一致的文件（项目根为准，单向同步到 skill）
SYNC_FILES = [
    'cls/harryopo-base.sty',
    'cls/harryopo-paper.cls',
    'cls/harryopo-report.cls',
    'cls/harryopo-slides.cls',
    'cls/flushend.sty',
    'math-notes/harryopo-mathnotes.cls',
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_cls_sync(project_root: Path, skill_dir: Path, rep: Report):
    """比对项目根与 skill 内嵌 templates/ 是否同步，并断言必含段存在"""
    skill_tpl = skill_dir / 'templates'

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


# ============================================================
# 2. 关键文件 / 目录存在性
# ============================================================

def check_paths(project_root: Path, skill_dir: Path, rep: Report):
    required = [
        ('项目根 templates/cls', project_root / 'templates' / 'cls'),
        ('项目根 templates/fonts', project_root / 'templates' / 'fonts'),
        ('项目根 templates/paper', project_root / 'templates' / 'paper'),
        ('项目根 templates/math-notes', project_root / 'templates' / 'math-notes'),
        ('项目根 templates/slides', project_root / 'templates' / 'slides'),
        ('skill SKILL.md', skill_dir / 'SKILL.md'),
        ('skill templates/cls', skill_dir / 'templates' / 'cls'),
        ('skill templates/fonts', skill_dir / 'templates' / 'fonts'),
        ('skill templates/slides', skill_dir / 'templates' / 'slides'),
        ('skill 内嵌 diagram-design', skill_dir / 'skills' / 'diagram-design'),
    ]
    for label, path in required:
        rep.add(OK if path.exists() else FAIL, '关键路径', f'{label}: {path}'
                + ('' if path.exists() else '  ← 缺失'))

    # 字体数量（19 个是基线：方正6 + XITS7 + Heros4 + lmmono1 + cour1）
    for label, path in (('项目根 fonts', project_root / 'templates' / 'fonts'),
                        ('skill fonts', skill_dir / 'templates' / 'fonts')):
        if not path.exists():
            continue
        n = len([f for f in path.iterdir() if f.is_file()])
        rep.add(OK if n == 19 else WARN, '关键路径', f'{label}: {n} 个字体'
                + ('' if n == 19 else f'（基线 19，差 {n - 19:+d}）'))


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
        out = subprocess.run(['git', '-C', str(project_root), 'ls-files'],
                             capture_output=True, text=True,
                             encoding='utf-8', errors='replace', timeout=30)
        if out.returncode != 0:
            rep.add(WARN, '隐私护栏', 'git ls-files 执行失败，跳过检查')
            return
        tracked = set(out.stdout.splitlines())
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


# ============================================================
# 入口
# ============================================================

def run_doctor(project_root: Path, skill_dir: Path, skip_privacy=False):
    rep = Report()
    check_paths(project_root, skill_dir, rep)
    check_cls_sync(project_root, skill_dir, rep)
    check_toolchain(rep)
    if not skip_privacy:
        check_privacy(project_root, rep)
    return rep


def main():
    import argparse
    ap = argparse.ArgumentParser(description='harryopo-office 自检（环境 + 防回归护栏）')
    ap.add_argument('--skip-privacy', action='store_true', help='跳过 git 跟踪检查')
    ap.add_argument('--json', action='store_true', help='输出 JSON（供 AI 消费）')
    args = ap.parse_args()

    here = Path(__file__).resolve()
    skill_dir = here.parent.parent
    project_root = _find_project_root(skill_dir)
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
