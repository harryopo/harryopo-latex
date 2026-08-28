# 开源精简美观 Markdown 查看器调研报告

> 调研日期：2026-08-14 ｜ 定位：**查看器/预览器/阅读器**（排除完整编辑器：Typora、Mark Text、Obsidian、StackEdit 等）
> 数据来源：OSS Finder 知识库快照 + 实时 GitHub topics 搜索（markdown-reader / markdown-viewer）+ 2026 年评测文章
> ⚠️ stars 数为调研时点快照，使用时请以仓库实时数据为准

---

## 一、快速结论（Top 推荐）

| 场景 | 首选 | 备选 |
|------|------|------|
| 终端看 md | **glow**（Go，颜值标杆） | mdcat（Rust 流式）、leaf、ink |
| 本地浏览器预览 | **grip**（GitHub 官方排版） | md-preview（原生无 Electron） |
| 自建 Web 查看器 | **markdown-it + github-markdown-css** | md-block（一行标签） |
| Windows 桌面查看 | **Neilooo/md-reader**（Tauri 2，5MB） | rmdv（Rust 原生） |
| 浏览器扩展 | **md-reader**（417★） | Markdown Preview Plus |
| 零构建发布站 | **Docsify** | docute、mdBook、VitePress |

---

## 二、分类推荐（按推荐度排序）

### A. 终端 TUI（零配置、开箱即看）

| 项目 | Stars | 语言 | 许可证 | 特点 |
|------|-------|------|--------|------|
| **glow**（charmbracelet） | ~18k | Go | MIT | Charm 团队出品，终端渲染颜值标杆；glamour 样式引擎、真彩/256 色、表格、语法高亮、图片（iTerm2/Kitty）、目录导航、fuzzy 搜索、stash 收藏。`glow README.md` 一条命令 |
| **mdcat**（sharkdp） | ~2.5k | Rust | MIT+Apache-2.0 | `fd`/`bat` 作者出品，管道友好的流式渲染器（cat 的 MD 版）；syntect 高亮、表格、脚注、Sixel 图像，自动分页 less |
| **leaf**（RivoLink） | 1.8k | Rust | - | Terminal Markdown previewer，GUI-like 体验，支持 termux（手机终端） |
| **ink**（borghei） | 新 | Rust | - | ratatui 构建，"actually looks good" 的终端阅读器：语法高亮、内联图片、mermaid 图、8 主题、tabs、搜索 |

### B. Web 查看 / 发布（浏览器即看）

| 项目 | Stars | 语言 | 特点 |
|------|-------|------|------|
| **Docsify** | ~28k | JS | 零构建——一个 index.html 引入一个 js，md 即内容，浏览器端实时渲染；侧边栏目录、搜索、代码高亮、主题定制 |
| **grip** | ~7k | Python | `pip install grip && grip README.md` → 浏览器打开 `localhost:6419` 即 100% GitHub 官方排版，自动刷新 |
| **github-markdown-css**（sindresorhus） | ~8k | CSS | 把 GitHub 官方排版审美提炼成单个 CSS，套 `.markdown-body` 类即得 GitHub 阅读体验——自建查看器的样式基石 |
| **VitePress** | ~14k | TS | Vite 驱动的下一代文档站，默认主题极简克制，代码高亮/搜索/暗色开箱即用 |
| **mdBook**（rust-lang） | ~20k | Rust | Rust 官方 Book 同款，教科书级干净：左目录、顶部搜索、优雅排版 |
| **docute** | ~4k | JS | Docsify 同族但更极简，一个 HTML 即站点 |
| **Quartz**（jackyzha0） | ~7.5k | TS | 把 Obsidian 笔记库变成带双向链接、Graph 视图的优雅静态站 |
| **Emanote**（srid） | ~700 | Haskell | 低 star 高颜值代表：无边框、大留白、优雅字体，实时热重载 |

### C. 桌面应用（原生/轻量）

| 项目 | Stars | 平台 | 特点 |
|------|-------|------|------|
| **Neilooo/md-reader** | 139 | Windows | Tauri 2 + Vue 3，**5MB 极致轻量**；KaTeX 公式、Mermaid 图、语法高亮、全文搜索、Edge 内核 WYSIWYG PDF 导出 |
| **rmdv**（minchenlee） | 新 | 跨平台 | Rust 原生，**无 Electron 无浏览器**，~150ms 冷启动；Mermaid/Graphviz DOT/LaTeX math/思维导图；**可通过 IPC 被 agent 控制** |
| **md-preview**（vorojar） | 242 | 跨平台 | Rust + 系统 WebView（wry），无 Electron，本地优先；多文档 tabs、会话恢复、Finder 集成、离线 Mermaid/KaTeX |
| **davidhoo/MarkdownReader** | 121 | macOS | SwiftUI 原生 + cmark-gfm + WKWebView；三栏布局（文件树/渲染/大纲）、Mermaid/KaTeX/PlantUML/Prism.js、**33 主题**、i18n、PDF 导出 |
| **QLMarkdown** | ~1k | macOS | QuickLook 插件，Finder 按空格即预览任意 .md，系统级集成最优雅 |

### D. 浏览器扩展

| 项目 | Stars | 特点 |
|------|-------|------|
| **md-reader**（md-reader/md-reader） | 417 | "The best way to read Markdown in Browser"，Chrome 扩展，TypeScript |
| **Markdown Here** | ~60k | 在 Gmail/Outlook/微信公众平台等富文本编辑器里选中 md 一键渲染成排版好的富文本，纯本地处理 |
| **MarkDownload** | ~1.5k | 网页一键抓取为干净 Markdown（保留链接/图片），可发到 Obsidian/Notion |

### E. 自建积木（库/组件）

| 项目 | Stars | 特点 |
|------|-------|------|
| **marked** | ~34k | 零依赖、极快，浏览器/Node 通用，自定义渲染器 |
| **markdown-it** | ~20k | CommonMark 兼容 + 插件体系（footnote/task list/katex/mermaid） |
| **md-block**（Lea Verou） | ~1.3k | 原生 Web Component：`<md-block src="README.md">` 一行标签渲染，零依赖可离线、Shadow DOM 样式隔离、可嵌套组合 |
| **markdown-nice** | ~4k | 中文排版颜值天花板（公众号/知乎场景），内置 20+ 精主题——自建样式时必参考其主题设计 |

---

## 三、排除说明

| 项目 | 排除原因 |
|------|----------|
| Typora / Mark Text / Obsidian / Joplin / Zettlr | 完整编辑器/笔记应用 |
| StackEdit / Dillinger / Vditor / Milkdown / ByteMD | Web 编辑器（以输入为核心） |
| Marp / Slidev / reveal.js | 演示文稿工具 |
| Pandoc | 格式转换器（无界面） |

---

## 四、结合本项目（d:\ai\latex）的落地建议

本项目办公文档平台规划了"阶段 2：本地预览服务器"。Markdown 查看器可融入：

1. **自建单文件查看器（首选，契合"AI 产 MD → 预览"范式）**
   `markdown-it` + `github-markdown-css` + `highlight.js` = 一个 HTML 文件的精美查看器；或更极致用 `md-block` 一个标签搞定。零依赖、可离线、风格可定制（方正字体中文化适配）。

2. **本地预览服务器组件**
   - 简单方案：`grip`（GitHub 官方排版）或 Docsify 静态托管
   - 原生方案：`rmdv`（Rust，~150ms 冷启动，**IPC 可被 agent 控制**——与项目"AI agent 驱动"理念契合）
   - Windows 桌面：`Neilooo/md-reader`（5MB，KaTeX/Mermaid 全支持）

3. **颜值参考范本**：glow 的终端配色、mdBook 的排版克制、markdown-nice 的中文主题设计。

---

## 五、待补查（需网络实时核验）

- Gitee 中文小众"markdown 预览"项目
- npm `markdown-preview` / `markdown-viewer` 包
- 各项目 2025-2026 年新提交与 stars 实时值
