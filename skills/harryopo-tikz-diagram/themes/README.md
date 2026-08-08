# harryopo-tikz-diagram 主题配色系统

两套配色主题，一键切换。

---

## 主题速览

| 主题 | 主色调 | 风格 | 适合场景 |
|------|--------|------|----------|
| **蓝色（blue）** | 深蓝灰 → 浅蓝灰 | 专业、稳重、技术感 | 技术文档、学术论文、企业系统架构图 |
| **绿色（green）** | 深绿 → 浅绿 | 清新、自然、教学感 | 课件、教材、环保/生物主题 |

---

## 加载主题

```latex
% 引入主题加载器
\input{themes/theme-loader.tex}

% 加载指定主题（blue 或 green）
\loadtikzsiztheme{green}
```

默认加载蓝色主题。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `blue.yaml` | 蓝色主题配置 |
| `green.yaml` | 绿色主题配置 |
| `theme-loader.tex` | LaTeX 主题加载器 |
| `README.md` | 本文档 |
