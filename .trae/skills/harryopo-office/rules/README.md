# 规范包（Rule Pack）

`govcheck` 的检查参数不写死在代码里，而是读**规则包**——一个描述"某套排版规范要求什么"的 YAML 文件。内置包 `gbt9704-2012.yaml`（GB/T 9704-2012 党政机关公文格式）；你可以复制它做成**学校学位论文规范包**或**期刊格式包**，让同一套检查器服务不同规范。

## 用法

```bash
# 默认包（gbt9704-2012）
python office.py govcheck 通知-paper.tex

# 指定包
python office.py govcheck 论文.tex --pack my-school-2026
python office.py govcheck 论文.docx --pack 路径/到/包.yaml

# 列出可用包
python office.py govcheck --list-packs
```

包的查找顺序：显式路径 → `rules/<name>.yaml`（skill 内置目录）→ 当前目录。

## 包结构（schema: harryopo-rulepack/1）

```yaml
schema: harryopo-rulepack/1     # 固定值，检查器据此识别
name: ××大学硕士学位论文规范     # 显示在报告标题
basis_doc: ××大学研究生院 2026 版 # 规范出处说明

docx:        # 检查 .docx 时的参数（全部可选，缺省项跳过）
  page:      { width_mm: 210, height_mm: 297, tol_mm: 1.5, basis: "第X章 第X条" }
  margins:
    top:     { mm: 30, tol_mm: 1.0, basis: "第X章 第X条" }
    # bottom / left / right 同构
  body:
    size_pt: 12              # 期望正文字号
    tol_pt: 0.6
    size_basis: "..."
    font_keywords: [宋体, SimSun]   # 命中任一即通过；缺省 = 跳过字体检查
    font_basis: "..."
  line:
    pt: 20                   # 固定值行距
    tol_pt: 1.1
    basis: "..."

tex:         # 检查 .tex/.cls 时的参数（解析 harryopo-paper.cls gov 分支）
  margins:   # 同 docx.margins 结构
  body_zihao: { value: "4", basis: "..." }        # 期望 \zihao{N}
  linespread: { value: 1.25, tol: 0.05, pt_label: 15, basis: "..." }
  heading_fonts:                   # 检查 gov 分支里出现的字体宏；[] = 跳过
    - { macro: heiti, label: 一级标题, basis: "..." }
```

每个条目的 `basis` 字段是**规范出处**（章节/条款号），原样出现在检查报告里——写清楚它，报告才能当整改依据用。

## 自制步骤

1. `cp gbt9704-2012.yaml my-school-2026.yaml`
2. 对照学校研究生院的格式要求改数值与 `basis` 出处
3. 放进本目录（或任意路径用显式路径引用）
4. `office.py govcheck 论文.tex --pack my-school-2026`

## 边界（如实说明）

- 检查的是**可量化的版式参数**（页面/边距/字号/行距/字体宏）。内容性规范（摘要写法、图表编号规则、参考文献著录细节）不在覆盖范围
- `tex` 模式依赖 harryopo-paper.cls 的 gov 分支结构（`\if@govmode` + `\geometry` + `\zihao` + `\linespread`）；学校若强制用官方 Word 模板，走 `docx` 模式
- 字体名匹配是**子串匹配**（docx 模式），字体改名可能导致误报——`font_keywords` 多写几个别名可缓解
