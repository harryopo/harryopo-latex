# 特征请求 — d:\ai\latex

## 待评估

### feat: 创建完整示例文件
- **背景**: 目前仅有 example-paper.tex/pdf、example-paper-twocolumn.tex/pdf、example-report.pdf
- **缺失**: example-book.tex、example-notes.tex（计划但未实施）
- **优先级**: 低（核心模板已完成）

### feat: harryopo-mathnotes 与 base.sty 统一
- **背景**: math-notes 当前完全独立，不共享 base.sty 的字体/颜色/代码配置
- **挑战**: math-notes 有自己独特的字体体系（XITS+方正+TeX Gyre Heros）和 mdframed 边框体系
- **方案**: 可考虑 base.sty 提供"轻量模式"（仅代码高亮+数学+图表），供 math-notes 按需加载
- **优先级**: 中（短期不必要，长期有整合价值）

### feat: 自动构建与 CI
- **背景**: 当前仅 build.ps1 手动编译
- **建议**: GitHub Actions 自动编译所有示例并上传 PDF artifacts
- **优先级**: 低

### feat: 模板参数化
- **背景**: 当前字号/页边距硬编码在 .cls 中
- **建议**: 通过 kvoptions 提供 9pt/10pt/11pt/12pt 选项、A4/A5 纸张选项
- **优先级**: 低
