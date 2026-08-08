# 错误记录 — d:\ai\latex

## 2026-06-21

### ERROR: 初始 LS 工具返回了过时/缓存结果
- **上下文**: Super Memory 工作流开始时，LS 工具显示 templates/ 包含 harryopo-base.sty, harryopo-paper.cls 等 6 个文件
- **实际情况**: Get-ChildItem 和 Test-Path 确认这些文件不存在，templates/ 仅含 examples/ 和 math-notes/
- **影响**: 导致后续 Read 工具返回了之前缓存的内容（harryopo-base.sty, harryopo-paper.cls, build.ps1），这些内容可能来自之前的会话
- **处理**: 更新记忆为实际文件状态

### WARNING: 核心模板文件缺失
- **缺失文件**:
  - templates/harryopo-base.sty（共享基础包）
  - templates/harryopo-paper.cls（论文文档类 - example-paper.tex 依赖此文件）
  - templates/harryopo-report.cls（报告文档类）
  - templates/harryopo-book.cls（书籍文档类）
  - templates/harryopo-notes.cls（笔记文档类）
  - templates/build.ps1（编译脚本）
  - templates/examples/example-report.pdf 无对应 .tex
- **现有 example-paper.tex 引用了不存在的 harryopo-paper.cls** — 现有的 PDF 可能是清理前编译的，当前无法重新编译

### WARNING: 中文book 子项目 — 部分 bib 引用缺失
- **问题**: 编译中文book/main.tex 时 `Visscher2008` 等部分 bib 引用显示 "?"
- **根因**: main.bib 文件不完整，部分引用的条目不存在
- **影响**: 仅影响引用显示，不影响编译和排版
- **处理**: 需要补全 bib 条目（低优先级）
