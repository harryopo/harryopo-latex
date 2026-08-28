"""
doc-html-pdf · Markdown → JSON 蒸馏工具
========================================

把任意 Markdown 文档蒸馏为 doc-html-pdf 排版用的结构化 JSON。

特性：
  - 支持 YAML frontmatter（title/subtitle/version/date/author/school/kind...）
  - 支持多种章节标题格式（中文编号 / 数字编号 / 无编号自动补）
  - 段落自动合并（连续非空行合并为一个 paragraph）
  - 表格 / 列表 / 代码块 / 引用块（→ callout）自动识别
  - 不绑定任何项目，kind 只是元信息，可任意填写

用法：
  python scripts/distill.py --md <输入.md> --out <输出.json> [--kind <类型>] [--title <标题>]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# ============== 标题正则 ==============
# 章节（## 级），按优先级匹配
SECTION_PATTERNS = [
    re.compile(r"^##\s+第\s*([一二三四五六七八九十百]+)\s*章[、.\s]+(.+)$"),       # ## 第一章 标题
    re.compile(r"^##\s+([一二三四五六七八九十百]+)\s*[、.\s]+(.+)$"),              # ## 一、标题
    re.compile(r"^##\s+(\d+(?:\.\d+)*)\s*[、.\s]+(.+)$"),                          # ## 1. 标题 / ## 1.2 标题
    re.compile(r"^##\s+(.+)$"),                                                    # ## 标题（无编号）
]
# 小节（### 级）
SUBSECTION_PATTERNS = [
    re.compile(r"^###\s+(\d+(?:\.\d+)*)\s*[、.\s]+(.+)$"),                         # ### 1.1 标题
    re.compile(r"^###\s+([一二三四五六七八九十百]+)\s*[、.\s]+(.+)$"),             # ### 一、标题
    re.compile(r"^###\s+(.+)$"),                                                   # ### 标题（无编号）
]

CN_NUMS = "零一二三四五六七八九十百"

# 行内 / 块级数学公式（KaTeX 渲染）
MATH_PAT = re.compile(r"(\$\$[^$]+\$\$|\$[^$\n]+\$)")


def strip_inline(md: str) -> str:
    """去除行内 Markdown 记号（**、*、`、[text](url)），公式片段受保护不受影响"""
    math_tokens = []

    def hold(m):
        math_tokens.append(m.group(0))
        return f"\x00MATH{len(math_tokens) - 1}\x00"

    s = MATH_PAT.sub(hold, md)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    s = re.sub(r"\[(.+?)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\x00MATH(\d+)\x00", lambda m: math_tokens[int(m.group(1))], s)
    return s.strip()


def cn_num(n: int) -> str:
    """阿拉伯数字 → 中文数字（1→一，支持 1~99）"""
    digits = "零一二三四五六七八九"
    if n < 10:
        return digits[n]
    tens, ones = divmod(n, 10)
    out = digits[tens] + "十"
    if ones:
        out += digits[ones]
    return out


def parse_frontmatter(lines: list) -> tuple[dict, int]:
    """解析 YAML frontmatter（--- 包裹）。返回 (meta, 正文起始行号)"""
    meta = {}
    if not lines or lines[0].strip() != "---":
        return meta, 0
    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        m = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.+)$", lines[end].strip())
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()
        end += 1
    if end >= len(lines):  # 没有闭合，视为普通文本
        return {}, 0
    return meta, end + 1


def extract_head_meta(lines: list) -> dict:
    """从文档头部（前 15 行）正则提取版本/作者/日期/学校等"""
    meta = {}
    for line in lines[:15]:
        m = re.search(r"版本[：:]\s*(v?[\d.]+)", line)
        if m:
            meta.setdefault("version", m.group(1))
        m = re.search(r"最后更新[：:]\s*([\d-]+)", line)
        if m:
            meta.setdefault("date", m.group(1))
        m = re.search(r"作者[：:]\s*(.+)", line)
        if m:
            meta.setdefault("author", m.group(1).strip())
        m = re.search(r"学校[：:]\s*(.+)", line)
        if m:
            meta.setdefault("school", m.group(1).strip())
        m = re.search(r"班级[：:]\s*(.+)", line)
        if m:
            meta.setdefault("class", m.group(1).strip())
    return meta


def strip_inline(md: str) -> str:
    """去除行内 Markdown 记号（**、*、`、[text](url)）"""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", md)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    s = re.sub(r"\[(.+?)\]\([^)]+\)", r"\1", s)
    return s.strip()


def parse_table(lines: list) -> dict | None:
    """解析 Markdown 表格"""
    rows = []
    for line in lines:
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [strip_inline(c.strip()) for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return None
    return {"type": "table", "headers": rows[0], "rows": rows[1:]}


def parse_markdown(md_text: str, kind: str = "doc") -> dict:
    """把 Markdown 解析为结构化 JSON"""
    lines = md_text.split("\n")

    # 1) frontmatter + 头部元信息
    meta, start = parse_frontmatter(lines)
    meta.update(extract_head_meta(lines[start:]))

    # 2) 文档标题（# 级，frontmatter title 优先）
    title = meta.get("title", "")
    for line in lines[start:]:
        m = re.match(r"^#\s+(.+)", line)
        if m:
            title = m.group(1).strip()
            break

    # 3) 章节解析
    sections = []
    current_section = None
    section_counter = 0
    preamble_blocks = []  # 第一个章节之前的引言内容（不丢弃）

    i = start
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        # 当前块的落点：在章节内 → 章节 blocks；在章节前 → preamble
        target = current_section["blocks"] if current_section else preamble_blocks

        # 章节标题（##）
        sm = None
        for pat in SECTION_PATTERNS:
            sm = pat.match(stripped)
            if sm:
                break
        if sm:
            if current_section:
                sections.append(current_section)
            section_counter += 1
            num = sm.group(1) if len(sm.groups()) == 2 else cn_num(section_counter)
            sect_title = sm.group(2).strip() if len(sm.groups()) == 2 else sm.group(1).strip()
            current_section = {
                "num": num,
                "title": sect_title,
                "level": 1,
                "blocks": [],
            }
            i += 1
            continue

        # 小节标题（###）
        ssm = None
        for pat in SUBSECTION_PATTERNS:
            ssm = pat.match(stripped)
            if ssm:
                break
        if ssm and current_section:
            current_section["blocks"].append({
                "type": "heading",
                "level": 2,
                "num": ssm.group(1),
                "text": ssm.group(2).strip(),
            })
            i += 1
            continue

        # 代码块（```arch 语言 → 架构图）
        if line.startswith("```"):
            code_lines = []
            lang = line[3:].strip()
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if lang.split(maxsplit=1)[0] == "arch":
                arch_title = lang.split(maxsplit=1)[1].strip() if " " in lang else ""
                layers = []
                for cl in code_lines:
                    m = re.match(r"^(.*?):\s*(.+)$", cl.strip())
                    if m:
                        layers.append({
                            "name": m.group(1).strip(),
                            "items": [x.strip() for x in m.group(2).split("|")],
                        })
                if layers:
                    target.append({
                        "type": "architecture",
                        "title": arch_title,
                        "layers": layers,
                    })
            else:
                target.append({
                    "type": "code-block",
                    "lang": lang,
                    "code": "\n".join(code_lines),
                })
            i += 1
            continue

        # 块级数学公式（$$ ... $$，支持单行闭合与跨行）
        if stripped.startswith("$$"):
            if stripped.count("$$") >= 2 and stripped.endswith("$$"):
                # 单行闭合：$$...$$
                content = stripped[2:-2].strip()
                i += 1
            else:
                # 跨行：收集到下一个 $$ 行
                content_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].strip().startswith("$$"):
                        i += 1
                        break
                    content_lines.append(lines[i])
                    i += 1
                content = "\n".join(content_lines).strip()
            if content:
                target.append({"type": "math", "tex": content, "display": True})
            continue

        # 表格（连续 | 开头行）
        if stripped.startswith("|") and stripped.endswith("|"):
            table_buffer = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_buffer.append(lines[i].strip())
                i += 1
            table_data = parse_table(table_buffer)
            if table_data:
                target.append(table_data)
            continue

        # 列表（- / * / 1.）
        list_pat = re.compile(r"^([-*]|\d+\.)\s+(.+)$")
        if list_pat.match(stripped):
            items = []
            variant = "bullet"
            while i < len(lines):
                m = list_pat.match(lines[i].strip())
                if not m:
                    break
                if m.group(1) in ("-", "*"):
                    variant = variant if variant == "bullet" else variant
                else:
                    variant = "numbered"
                items.append(strip_inline(m.group(2)))
                i += 1
            target.append({
                "type": "list",
                "variant": variant,
                "items": items,
            })
            continue

        # 引用块（> xxx）→ callout
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]).strip())
                i += 1
            qtext = "\n".join(quote_lines)
            # 首行带 **标题** 则作为 callout 标题
            m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", qtext)
            if m and m.group(2):
                target.append({
                    "type": "callout",
                    "variant": "info",
                    "title": m.group(1),
                    "text": m.group(2),
                })
            else:
                target.append({
                    "type": "callout",
                    "variant": "info",
                    "title": "说明",
                    "text": qtext,
                })
            continue

        # 普通段落：累积连续非空行，空行结束
        if stripped and not stripped.startswith("#") \
                and not stripped.startswith("---"):
            para_lines = []
            while i < len(lines):
                t = lines[i].strip()
                if not t:
                    break
                if t.startswith("#") or t.startswith("```") or t.startswith(">") \
                        or t.startswith("$$") or t.startswith("|") \
                        or re.match(r"^([-*]|\d+\.)\s+", t):
                    break
                para_lines.append(t)
                i += 1
            para = strip_inline(" ".join(para_lines))
            if para:
                target.append({"type": "paragraph", "text": para})
            continue

        i += 1

    if current_section:
        sections.append(current_section)

    # 4) 构造完整 JSON（全部字段可缺省，模板自动降级）
    total_blocks = sum(len(s["blocks"]) for s in sections) + len(preamble_blocks)
    title = title or meta.get("title", "未命名文档")
    return {
        "kind": kind,
        "meta": {
            "title": title,
            "subtitle": meta.get("subtitle", ""),
            "version": meta.get("version", ""),
            "date": meta.get("date", ""),
            "author": meta.get("author", ""),
            "school": meta.get("school", ""),
            "class": meta.get("class", ""),
        },
        "cover": {
            "kicker": kind.upper().replace("-", " · "),
            "title": title,
            "subtitle": meta.get("subtitle", ""),
            "stats": [
                {"num": str(len(sections)), "label": "章节数", "sub": "Sections"},
                {"num": str(total_blocks), "label": "内容块", "sub": "Blocks"},
            ],
        },
        "preamble": preamble_blocks,
        "toc": [{"num": s["num"], "title": s["title"]} for s in sections],
        "sections": sections,
    }


def main():
    parser = argparse.ArgumentParser(description="doc-html-pdf · Markdown → JSON 蒸馏工具")
    parser.add_argument("--md", required=True, help="Markdown 源文件路径")
    parser.add_argument("--out", required=True, help="输出 JSON 路径")
    parser.add_argument("--kind", default="doc", help="文档类型（仅作元信息，如 report/user-guide/whitepaper）")
    args = parser.parse_args()

    md_path = Path(args.md)
    if not md_path.exists():
        print(f"❌ 文件不存在：{md_path}")
        sys.exit(1)

    md_text = md_path.read_text(encoding="utf-8")
    result = parse_markdown(md_text, args.kind)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ 蒸馏完成：{md_path.name} → {out_path.name}")
    print(f"   标题：{result['meta']['title']}")
    print(f"   章节数：{len(result['sections'])}")
    total_blocks = sum(len(s["blocks"]) for s in result["sections"])
    print(f"   块数：  {total_blocks}")


if __name__ == "__main__":
    main()
