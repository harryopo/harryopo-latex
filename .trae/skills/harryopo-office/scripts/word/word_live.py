#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
word_live.py — Word 实时修订会话适配器（COM 本地后端）

方案书 v3 P2「word-mcp-live 适配器」的本地实现：不绑定外部 MCP 项目，
以 pywin32 COM 驱动"打开中"的 Word 做带修订痕迹的实时编辑。
CLI 边界即适配层——将来换 word-mcp-live 后端只需保持同一子命令契约。

子命令：
    status  <docx>                                  会话/修订/批注概览
    edit    <docx> --find 原文 --replace 新文       开关式查找替换（自动开修订模式）
    comment <docx> --find 锚文本 --text 批注内容    给命中文本加批注
    accept  <docx>                                  接受全部修订
    reject  <docx>                                  拒绝全部修订

铁律：
    - 优先附着用户已打开的 Word 会话（GetActiveObject），绝不 Quit 用户实例；
    - 文档保持打开状态（live session），每次操作后 Save 落盘；
    - COM 不可用（无 pywin32/无 Word）→ 明确报错退出码 2，不静默降级。
"""

import argparse
import os
import re
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REV_TYPE = {1: '插入', 2: '删除', 3: '格式更改', 4: '行/段重排', 5: '列表重排',
            7: '单元格更改', 8: '行/列移动', 9: '内容修订', 10: '行/列属性修订',
            11: '表格重排'}


def _reauthor(docx_path, since_iso, to_author):
    """把 w:date >= since_iso（UTC ISO 串）的修订/批注元素作者改为 to_author。

    Microsoft 365 登录态下，修订/批注作者固定取账号显示名，
    Application.UserName 赋值不生效——只能在 Save 后对 OOXML 做时间窗归因。
    时间窗外（用户手工改稿）的标记不受影响。"""
    elem_re = re.compile(r'<w:(?:ins|del|comment|commentRangeStart|commentRangeEnd|'
                         r'commentReference)\b[^>]*>')
    dst = Path(docx_path)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.docx',
                                      dir=str(dst.parent))  # 同盘目录，rename 原子替换
    tmp.close()
    with zipfile.ZipFile(str(docx_path)) as zin:
        names = zin.namelist()
        data = {n: zin.read(n) for n in names}
    changed = 0
    for target in ('word/document.xml', 'word/comments.xml'):
        if target not in data:
            continue
        xml = data[target].decode('utf-8')

        def _fix(m):
            nonlocal changed
            tag = m.group(0)
            d = re.search(r'w:date="([^"]+)"', tag)
            if d and d.group(1) >= since_iso and f'w:author="{to_author}"' not in tag:
                changed += 1
                return re.sub(r'w:author="[^"]*"', f'w:author="{to_author}"', tag)
            return tag

        new = elem_re.sub(_fix, xml)
        if new != xml:
            data[target] = new.encode('utf-8')
    if changed:
        with zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(n, data[n])
        os.replace(tmp.name, str(docx_path))
    else:
        os.unlink(tmp.name)
    return changed


def _attach():
    """返回 (word, we_started)。附着已有会话优先，避免打扰用户正在编辑的窗口。"""
    try:
        import win32com.client
    except ImportError:
        print('[ERROR] 需要 pywin32（python -m pip install pywin32）且本机安装 Word',
              file=sys.stderr)
        sys.exit(2)
    try:
        return win32com.client.GetActiveObject('Word.Application'), False
    except Exception:
        word = win32com.client.Dispatch('Word.Application')
        return word, True


def _open_doc(word, docx_path):
    """在会话中找到目标文档（已打开则复用），否则打开并置为可见（live 语义）"""
    abs_path = os.path.abspath(str(docx_path))
    name = os.path.basename(abs_path).lower()
    for i in range(1, word.Documents.Count + 1):
        d = word.Documents.Item(i)
        try:
            if os.path.basename(str(d.FullName)).lower() == name:
                return d, False
        except Exception:
            continue
    word.Visible = True
    return word.Documents.Open(abs_path), True


def _doc_find(doc, text):
    """用 Selection.Find 收集全部命中位置 [(start,end),...]

    实测教训：本机 Word 16 经 COM 的 Range.Find 完全无视 Range 起点
    （每轮都从文档头返回第一处命中，边替换边搜会 200 次空转同一坐标），
    必须走 Selection.Find + Collapse(wdCollapseEnd) 逐轮推进；
    替换阶段倒序赋值，保证未处理命中的坐标不被前面的编辑扰动。"""
    word = doc.Application
    sel = word.Selection
    doc.Activate()
    sel.HomeKey(Unit=6)  # wdStory：光标移到文档头
    hits = []
    while len(hits) < 200:
        f = sel.Find
        f.ClearFormatting()
        f.Text = text
        f.Wrap = 0        # wdFindStop：到文档尾即停，不回绕
        f.Forward = True
        f.MatchCase = True
        if not f.Execute():
            break
        hits.append((sel.Start, sel.End))
        sel.Collapse(0)   # wdCollapseEnd：从命中末尾继续
    return hits


def cmd_status(docx, **kw):
    word, _ = _attach()
    doc, opened = _open_doc(word, docx)
    n_rev = doc.Revisions.Count
    n_com = doc.Comments.Count
    print(f'[会话] {"本适配器打开" if opened else "已在 Word 中打开"}: {doc.Name}')
    print(f'[修订] 未接受修订 {n_rev} 处')
    for i in range(1, min(n_rev, 10) + 1):
        r = doc.Revisions.Item(i)
        t = REV_TYPE.get(int(r.Type), f'type={r.Type}')
        try:
            print(f'   - {t} | {r.Author} | {str(r.Range.Text)[:40]!r}')
        except Exception:
            print(f'   - {t}')
    if n_com:
        print(f'[批注] {n_com} 条')
        for i in range(1, min(n_com, 10) + 1):
            c = doc.Comments.Item(i)
            print(f'   - {c.Author}: {c.Range.Text[:40]!r}')
    if n_rev == 0 and n_com == 0:
        print('[干净] 无未处理修订与批注')


def _utc_stamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _close_doc(word, docx_path):
    """关闭文档（调用方已 Save）以释放文件锁——reauthor 必须在锁释放后进行"""
    name = os.path.basename(os.path.abspath(str(docx_path))).lower()
    for i in range(1, word.Documents.Count + 1):
        if os.path.basename(str(word.Documents.Item(i).FullName)).lower() == name:
            word.Documents.Item(i).Close(False)
            return


def cmd_edit(docx, find, replace, author='AI Review', **kw):
    word, _ = _attach()
    doc, _ = _open_doc(word, docx)
    positions = _doc_find(doc, find)
    if not positions:
        print(f'[未命中] 文档中找不到：{find!r}')
        return 1
    prev_track = bool(doc.TrackRevisions)
    t0 = _utc_stamp()
    doc.TrackRevisions = True
    for s, e in reversed(positions):
        doc.Range(s, e).Text = replace   # 修订模式下赋值生成原生 w:del + w:ins
    doc.TrackRevisions = prev_track
    doc.Save()
    _close_doc(word, docx)             # 释放文件锁后做作者归因，再重开保持 live 会话
    n = _reauthor(docx, t0, author)
    word.Documents.Open(os.path.abspath(str(docx)))
    print(f'[完成] 修订替换 {len(positions)} 处（作者 {author}，已留痕并保存，'
          f'Word 窗口内可见删除线/下划线；作者归因 {n} 条）')
    return 0


def cmd_comment(docx, find, text, author='AI Review', **kw):
    word, _ = _attach()
    doc, _ = _open_doc(word, docx)
    positions = _doc_find(doc, find)
    if not positions:
        print(f'[未命中] 文档中找不到锚文本：{find!r}')
        return 1
    s, e = positions[0]
    t0 = _utc_stamp()
    doc.Comments.Add(doc.Range(s, e), text)
    doc.Save()
    _close_doc(word, docx)
    _reauthor(docx, t0, author)
    word.Documents.Open(os.path.abspath(str(docx)))
    shown = text[:30] + '…' if len(text) > 30 else text
    print(f'[完成] 已批注（作者 {author}）：{find!r} → {shown}')
    return 0


def _resolve_all(docx, accept):
    word, _ = _attach()
    doc, _ = _open_doc(word, docx)
    n = doc.Revisions.Count
    if accept:
        doc.Revisions.AcceptAll()
    else:
        doc.Revisions.RejectAll()
    doc.Save()
    print(f'[完成] 已{"接受" if accept else "拒绝"}全部修订（{n} 处）并保存')


def cmd_accept(docx, **kw):
    _resolve_all(docx, True)


def cmd_reject(docx, **kw):
    _resolve_all(docx, False)


def main():
    ap = argparse.ArgumentParser(prog='word_live.py',
                                 description='Word 实时修订会话适配器（COM）')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, help_ in [('status', '会话/修订/批注概览'),
                        ('accept', '接受全部修订'), ('reject', '拒绝全部修订')]:
        p = sub.add_parser(name, help=help_)
        p.add_argument('docx')
    p = sub.add_parser('edit', help='修订模式查找替换')
    p.add_argument('docx')
    p.add_argument('--find', required=True)
    p.add_argument('--replace', required=True)
    p.add_argument('--author', default='AI Review', help='修订作者名（默认 AI Review）')
    p = sub.add_parser('comment', help='给命中文本加批注')
    p.add_argument('docx')
    p.add_argument('--find', required=True, help='锚文本')
    p.add_argument('--text', required=True, help='批注内容')
    p.add_argument('--author', default='AI Review', help='批注作者名（默认 AI Review）')
    args = vars(ap.parse_args())
    cmd = args.pop('cmd')
    docx = Path(args.pop('docx'))
    if not docx.exists():
        print(f'[ERROR] 文件不存在: {docx}', file=sys.stderr)
        sys.exit(1)
    sys.exit({'status': cmd_status, 'edit': cmd_edit, 'comment': cmd_comment,
              'accept': cmd_accept, 'reject': cmd_reject}[cmd](docx, **args) or 0)


if __name__ == '__main__':
    main()
