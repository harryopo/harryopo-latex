# 2026-07-26 harryopo-latex 方正字体应用修复

## 背景
用户反馈 PDF 内容未使用方正黑体、小标宋等方正家族字体，违反 skill 规范。

## 根因（两层）

### 根因 1：fontspec 语法错误（致命）
`\setCJKmainfont[...]{FZSSJW}` 写法导致 fontspec 把整个 options 串当作字体名解析。

**.log 报错**：
```
(fontspec) The font "Extension = , Path = ../fonts/" cannot be found.
LaTeX Font Warning: Font shape `TU/Extension=.TTF,Path=../fonts/(0)' undefined
```

**根因分析**：
- fontspec v2.9+ 仅接受 `\setCJKmainfont{字体名}[options]`（name 在前）
- 旧代码写成 `\setCJKmainfont[options]{字体名}`（options 在前）
- fontspec 误把 `Extension = .TTF, Path = ../fonts/, ...` 整体当字体名

**修复**：
```latex
\setCJKmainfont{FZSSJW}[
    Extension = .TTF,
    BoldFont = FZHTJW,
    ItalicFont = FZKTJW,
    Path = ../fonts/
]
```

### 根因 2：subsection 标题未用 \fzht
`\subsection` 标题用 `\bfseries\color{SubColor}`，缺少方正黑体指令。

**修复**（paper.cls / report.cls）：
```latex
\titleformat{\subsection}
    {\large\bfseries\fzht\color{SubColor}}   % 加 \fzht
    {}{0pt}{}
```

### 根因 3：方正字体族未指定 BoldFont
`\newfontfamily\hrypht{FZHTJW}[...]` 缺少 BoldFont，导致 "Font shape undefined" 警告。

**修复**：所有方正字体族的 BoldFont/ItalicFont 指向自身（中文无真粗斜体）：
```latex
\newCJKfontfamily\hrypht{FZHTJW}[
    Extension=.TTF, Path=../fonts/,
    BoldFont=FZHTJW, ItalicFont=FZHTJW
]
```

## 验证结果

**`pdffonts test-4problems.pdf` 输出**：
```
XITS-Regular              ← 西文/数字
XITS-Bold                 ← 西文粗体
FZSSJW (CID TrueType)     ← 方正书宋（正文）
FZHTJW (CID TrueType)     ← 方正黑体（subsection/页眉）
FZKTJW (CID TrueType)     ← 方正楷体（作者/页眉）
FZXBSJW (CID TrueType)    ← 方正小标宋（标题）
```

**全部方正字体已嵌入，LaTeX Font Warning 警告消失**（仅剩 xeCJK Redefining 信息性告警）。

## 修改文件清单
- [harryopo-base.sty](file:///d:/ai/latex/.trae/skills/harryopo-latex/templates/cls/harryopo-base.sty)
  - `\setCJKmainfont{FZSSJW}[options]` 修正语法
  - `\setCJKsansfont{FZHTJW}[options]` 修正语法
  - 所有 `\newfontfamily` / `\newCJKfontfamily` 加 BoldFont/ItalicFont 自指
- [harryopo-paper.cls](file:///d:/ai/latex/.trae/skills/harryopo-latex/templates/cls/harryopo-paper.cls)
  - subsection 标题加 `\fzht`
- [harryopo-report.cls](file:///d:/ai/latex/.trae/skills/harryopo-latex/templates/cls/harryopo-report.cls)
  - subsection 标题加 `\fzht`

## 字体规范（最终落表）

| LaTeX 命令 | 方正字体 | ttf 文件 | 用途 |
|------------|----------|----------|------|
| `\setCJKmainfont` | 方正书宋 | FZSSJW.TTF | 正文 |
| `\setCJKsansfont` | 方正黑体 | FZHTJW.TTF | 无衬线 |
| `\fzxb` | 方正小标宋 | FZXBSJW.TTF | 文档/章标题 |
| `\fzdbs` | 方正大标宋 | FZDBSJW.TTF | 节标题 |
| `\fzht` | 方正黑体 | FZHTJW.TTF | subsection/关键词标签 |
| `\fzkt` | 方正楷体 | FZKTJW.TTF | 作者/页眉 |
| `\fzfs` | 方正仿宋 | FZFSJW.TTF | 机构/日期 |

## 踩坑
- fontspec v2.9 不接受 `[options]{name}` 语法，**必须** `{name}[options]`
- 中文字体 BoldFont/ItalicFont 需显式自指，否则 font spec 报 "shape undefined" 警告
- ctex 默认的 SimSun/SimHei/KaiTi 字体在 TeX Live 默认不安装，触发 ctex 自己的 warning（信息性）
- xelatex 编译时 `Path = ../fonts/` 相对路径必须从编译 cwd 出发，cwd 在 templates/paper/ 时指向 templates/fonts/（正确）
