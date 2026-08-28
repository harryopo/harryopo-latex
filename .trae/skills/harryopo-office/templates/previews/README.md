# 预览指南 — harryopo MD 预览方案

## 文件清单

| 模板 | MD 文件 | 对应 LaTeX 模板 |
|------|---------|----------------|
| 论文单栏 | `paper-single-column.md` | `harryopo-paper` |
| 论文双栏 | `paper-twocolumn.md` | `harryopo-paper[twocolumn]` |
| 报告 | `report.md` | `harryopo-report` |
| 论文 Showcase | `paper-showcase.md` | `harryopo-paper`（完整特性） |
| 报告 Showcase | `report-showcase.md` | `harryopo-report`（完整特性） |

## CSS 样式：`harryopo-preview.css`

模拟 harryopo 蓝主题的 MD 预览样式：

- 标题层级颜色（MainColor/SubColor/SmallColor）
- 三线表样式（与 booktabs 一致）
- 引用块蓝色边线（与 quote 环境一致）
- 代码块 GitHub 风格（与 listings 一致）
- 中文字体优先 Source Han / Noto CJK（无方正系列时的回退）
- 行高 1.75、段首缩进 2em（与最终 PDF 接近）

## 预览方法

### 方法 1：VS Code（推荐）

1. 安装扩展：**Markdown Preview Enhanced**
2. 打开任意 MD 文件
3. 在文件顶部加 front-matter：

```yaml
---
css: harryopo-preview.css
---
```

或使用全局设置：`.vscode/settings.json`

```json
{
    "markdown-preview-enhanced.previewCss": [
        "file:///d:/ai/latex/.trae/skills/harryopo-latex/templates/previews/harryopo-preview.css"
    ]
}
```

### 方法 2：typora

1. 菜单 → 偏好设置 → 外观 → 主题
2. 打开主题文件夹
3. 复制 `harryopo-preview.css` 到主题目录
4. 重启 typora
5. 主题列表选择 `harryopo`

### 方法 3：浏览器

用 `markdown-it` + `harryopo-preview.css` 渲染：

```bash
npx -y md-to-pdf paper-single-column.md \
  --stylesheet harryopo-preview.css
```

或写一个简单的 HTML：

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="harryopo-preview.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div id="content"></div>
    <script>
        fetch('paper-single-column.md')
            .then(r => r.text())
            .then(t => document.getElementById('content').innerHTML = marked(t));
    </script>
</body>
</html>
```

## 设计还原度

| 元素 | 还原度 | 说明 |
|------|--------|------|
| 标题层级（颜色/字号） | 95% | 颜色与 PDF 一致，字号按比例缩放 |
| 表格（三线表） | 100% | 顶/中/底横线一致 |
| 引用块（蓝色边线） | 100% | 边框 + 背景色一致 |
| 代码块 | 90% | 字体回退，背景色一致 |
| 列表 | 100% | 圆点/编号一致 |
| 行高/段距 | 80% | 浏览器渲染与 PDF 微差 |
| 字体（方正系列） | 0% | 浏览器无方正书宋，回退思源/思源宋体 |
| 双栏 | 0% | 浏览器无原生双栏，结构 1:1 即可 |
| 页眉/页脚/页码 | 0% | 浏览器无对应能力 |
| 图表编号 | 50% | 需手动写"图 1"/"表 1" |

## 实用建议

1. **MD 阶段聚焦内容**：标题层级、章节顺序、表格数据、引用准确性
2. **不追求视觉一致**：字体/分栏/页码差异不可避免，无需纠结
3. **最终视觉确认靠 PDF**：内容改好后再编译 PDF 看实际效果
4. **MD 直接生成 LaTeX**：内容确认后，调用 harryopo-latex skill 的 `convert.py` 直接生成 .tex

## 核心 Markdown → LaTeX 转换规则

| MD 语法 | LaTeX 命令 |
|---------|-----------|
| `# H1` | `\section*{}` |
| `## H2` | `\subsection*{}` |
| `### H3` | `\subsubsection*{}` |
| `#### H4` | `\subhead{}` |
| 表格 | `tabularx`（自适应宽度） |
| 代码块 | `lstlisting`（带语法高亮） |
| 行内代码 | `\inlinecode{}` |
| 引用 | `quote` 环境 |
| 公式块 | `equation` 环境 |
| 链接 | `\href{url}{text}` |
| 图片 | `figure` 环境（caption 在图下方） |

## 已知限制

- 目录（TOC）：MD 渲染器无 LaTeX `\tableofcontents` 风格的目录，需靠标题层级判断
- 交叉引用：MD 渲染器无 `\ref{}` `\cite{}` 机制
- 算法伪代码：MD 无原生支持，建议用代码块 + 缩进模拟
