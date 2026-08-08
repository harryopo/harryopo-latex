# 办公文档可视化 + 途中可编辑技术方案深度调研报告

> **调研日期**: 2026-08-08
> **调研背景**: 用户核心想法——"办公文件可视化，可以在途中进行编辑，因为 AI 做的肯定有些要修改"
> **调研范围**: Word/docx 可视化编辑、LaTeX/PDF 实时预览、AI 生成→人审阅→再生成交互模式、最前沿可视化方案、技术栈选型
> **核心问题**: 要实现"AI 生成办公文档 → 浏览器可视化 → 途中可编辑修改 → 最终输出"，最佳技术架构是什么？推荐哪些开源组件？

---

## 目录

1. [核心结论与推荐架构（TL;DR）](#1-核心结论与推荐架构tldr)
2. [调研 A：浏览器中可视化预览和编辑 Word/docx 的方案](#2-调研-a浏览器中可视化预览和编辑-worddocx-的方案)
3. [调研 B：LaTeX/PDF 可视化编辑和实时预览](#3-调研-blatexpdf-可视化编辑和实时预览)
4. [调研 C：AI 生成 → 人审阅编辑 → 再生成的交互模式](#4-调研-c-ai-生成--人审阅编辑--再生成的交互模式)
5. [调研 D：最前沿的可视化方案](#5-调研-d最前沿的可视化方案)
6. [调研 E：技术栈选型与最佳架构方案](#6-调研-e技术栈选型与最佳架构方案)
7. [综合决策矩阵与落地路线图](#7-综合决策矩阵与落地路线图)
8. [参考资料](#8-参考资料)

---

## 1. 核心结论与推荐架构（TL;DR）

### 1.1 一句话结论

**最佳架构 = "结构化中间表示（Markdown/JSON/ProseMirror Doc）作为编辑内核 + TipTap/ProseMirror 作为前端编辑器 + Yjs 实现协作与 AI 流式插入 + diff 审阅模式实现人机协同 + pandoc/python-docx/LaTeX 作为最终输出引擎"。**

这不是单一方案，而是当前开源生态中验证最充分、组件最成熟、最贴合"AI 生成→可视化→可编辑→输出"闭环的组合。

### 1.2 为什么是这个答案

用户的需求本质上是三层闭环：
1. **生成层**：AI（LLM）把自然语言/需求转成文档内容
2. **编辑层**：人在浏览器里看到可视化结果，可以直接改，也可以审阅 AI 的修改建议
3. **输出层**：最终要产出"办公文档"——可能是 Word/docx、PDF、LaTeX 排版件

这三层的难点完全不同：
- 生成层靠 LLM，难点是可控性和格式约束
- 编辑层的难点是"所见即所得 + 精确 diff + 不破坏格式 + 人保留最终控制权"
- 输出层的难点是从内部表示到目标格式的高保真转换

没有任何单一商业产品（ONLYOFFICE、Google Docs、Overleaf）能同时最优地覆盖这三层。但开源组件的组合可以——这就是本报告要论证的。

### 1.3 推荐技术栈速览

| 层 | 推荐组件 | 备选 | 理由 |
|---|---|---|---|
| 前端框架 | React 19 / Next.js 15 | Vue 3 + Nuxt | 生态最大，编辑器组件支持最好 |
| 编辑器内核 | TipTap (ProseMirror) | Lexical、Plate(Slate) | 50+ 扩展、docx 导入导出、协作成熟 |
| 协作/AI 同步 | Yjs + Hocuspocus/y-websocket | Automerge | CRDT 黄金标准，离线优先 |
| AI 编辑 UX | inline diff（Cursor 风格）+ 接受/拒绝 | 建议模式、版本对比 | 颗粒度可控，人保留最终决定权 |
| docx 渲染/预览 | docx-preview（高保真）/ mammoth.js（语义提取） | ONLYOFFICE iframe | 视保真度需求二选一 |
| docx 深度编辑 | ONLYOFFICE Docs (Community Edition) | Collabora Online | OOXML 原生，私有部署免费 |
| LaTeX 在线预览 | Overleaf Community Edition / WasmTex | latex-wasm、SwiftLaTeX | 生产级 vs 轻量嵌入 |
| PDF 标注 | react-pdf-highlighter-plus / pdf.js | PSPDFKit(商业) | 开源、React 友好 |
| 最终输出 docx | python-docx / docxtemplater / pandoc | officegen | 模板化、样式可控 |
| 最终输出 PDF/LaTeX | XeLaTeX + pandoc | Typst | 已有 harryopo 体系 |
| 后端服务 | FastAPI(Python) / Node.js | Django | 与 AI/LLM 生态亲和 |

---

## 2. 调研 A：浏览器中可视化预览和编辑 Word/docx 的方案

本节解决"如何在浏览器里把 Word/docx 显示出来，并且能编辑"。

### 2.1 方案分类总览

| 方案类别 | 代表产品 | 保真度 | 可编辑性 | 私有部署 | 复杂度 | 适合场景 |
|---|---|---|---|---|---|---|
| **在线 Office 套件（iframe 嵌入）** | ONLYOFFICE、Collabora Online | ★★★★★ | ★★★★★ | ✅ 免费/付费 | 中-高 | 需要"像 Word 一样"的完整编辑 |
| **纯前端 docx 渲染** | docx-preview、mammoth.js | ★★★~★★★★ | ❌ 只读 | ✅ 免费 | 低 | 预览、提取内容 |
| **富文本编辑器 + docx 导入** | TipTap、Lexical、ProseMirror | ★★★ | ★★★★ | ✅ 免费 | 中-高 | 自定义编辑器产品 |
| **私有部署协作平台** | Nextcloud+ONLYOFFICE、CryptPad | ★★★★★ | ★★★★★ | ✅ | 中 | 团队文件协作 |

### 2.2 在线 Word 编辑器（ONLYOFFICE / Collabora / WOPI 方案）

#### 2.2.1 ONLYOFFICE Docs（Document Server）

**定位**：浏览器里的"网页版 Office"，OOXML 原生支持，是目前对 Microsoft 格式兼容性最好的开源方案。

**核心特性**：
- **格式原生支持**：`.docx/.xlsx/.pptx` 原生读写（不是转成 ODF 再转回），round-trip 保真度最高
- **实时协作**：两种协同模式（Fast 快速模式 / Strict 严格模式），支持评论、修订、聊天
- **修订/批注**：完整的 track changes、评论线程、审阅工作流
- **JWT 安全**：通过 JWT 保护文档服务器与集成前端的通信
- **WOPI 协议**：可与 Nextcloud、ownCloud、Seafile、SharePoint 集成

**版本与许可**：
- **Community Edition**：免费开源（AGPL-3.0），不限用户数，Docker 一键部署
- **Developer Edition**：本地服务器部署，可与自有 Web 应用集成
- **Server Pro**：企业版，提供沙箱编译、SSO、Git 集成等
- **DocSpace**（2026 年 3.7 版新增）：轻量单容器安装、ARM Docker 支持、内置 AI 代理

**部署要求**：CPU 双核 2GHz+、RAM 4GB+、HDD 40GB+、Docker，一条命令启动：
```
docker run -i -t -d -p 80:80 --restart=always -e JWT_SECRET=my_jwt_secret onlyoffice/documentserver
```

**适用判断**：如果产品需要"用户打开就像在 Word 里编辑"的完整体验，ONLYOFFICE 是最强开源选择。

#### 2.2.2 Collabora Online（CODE）

**定位**：基于 LibreOffice 内核的在线协作套件，是 LibreOffice 在浏览器中的延伸。

**核心特性**：
- **引擎**：LibreOffice Core 运行在服务端，渲染到浏览器
- **格式一致性**：与桌面版 LibreOffice 渲染一致，ODF 格式原生最优
- **WOPI 集成**：通过 WOPI 协议与文件存储平台对接
- **架构优势**：每文档由单节点服务，节点无状态，扩展性好；不像 ONLYOFFICE 需要 Redis+PostgreSQL+RabbitMQ 多组件

**版本与许可**：
- **CODE（Collabora Online Development Edition）**：免费滚动发布，适合测试/小团队（20 连接/10 文档限制）
- **Collabora Online**：企业订阅版，有 SLA 和长期支持，MPL-2.0 许可
- 全部代码开源（对比 ONLYOFFICE 的"Open Core + 不透明二进制"）

**部署**：Docker 镜像 `collabora/code`，基线内存约 1.3GB，每并发文档约 +100MB。

**ONLYOFFICE vs Collabora 关键差异**：

| 维度 | ONLYOFFICE | Collabora Online |
|---|---|---|
| 许可证 | AGPL-3.0（核心开源，部分二进制不透明） | MPL-2.0（全部开源） |
| 原生格式 | OOXML（.docx/.xlsx/.pptx） | ODF（.odt/.ods/.odp） |
| Office 格式保真度 | ★★★★★ 最佳 | ★★★★ 良好 |
| 高可用架构 | 需 Redis+PostgreSQL+RabbitMQ+NFS | 仅需标准 Linux 基础系统，节点无状态 |
| 修订/批注 | ✅ 完整 | ✅ 完整 |
| 端到端加密 | ❌ | ❌ |
| 私有部署 | ✅ | ✅ |

**选型建议**：
- 与外部频繁交换 Microsoft Office 文件 → **ONLYOFFICE**（OOXML 原生）
- 已用 LibreOffice 桌面版，要统一引擎 → **Collabora Online**
- 要求全部代码可审计 → **Collabora Online**（MPL，全开源）

#### 2.2.3 WOPI 协议说明

WOPI（Web Application Open Platform Interface）是 ONLYOFFICE/Collabora 与文件存储平台之间的标准协议：
1. 用户在存储平台（如 Nextcloud）打开文档
2. 存储平台生成 WOPI token，告诉浏览器在 iframe 加载编辑器
3. 编辑器用 token 通过 WOPI 端点获取文件，编辑后通过同一通道保存回去

这意味着：**只要你实现 WOPI host 接口，就能把 ONLYOFFICE/Collabora 嵌入你自己的文件管理系统**。这是构建私有化文档协作平台的标准方式。

### 2.3 纯前端 docx 渲染（docx-preview / mammoth.js）

这类方案不依赖服务器，完全在浏览器里解析 docx（本质是 ZIP+XML），适合预览和内容提取，但**不能直接编辑**。

#### 2.3.1 docx-preview

**定位**：尽量还原原始排版（分页、字体、表格），效果与 Office 打开几乎一致，适合预览。

- 基于 JSZip 解压 docx 容器，渲染为 HTML/CSS
- 支持页眉页脚、脚注尾注、分页渲染
- 渲染效果接近 Word 原版
- 只读预览，无编辑能力
- Apache-2.0，约 975KB

#### 2.3.2 mammoth.js

**定位**：把 docx 转成语义化的干净 HTML/Markdown/纯文本，**牺牲排版保真度换取内容准确性**。

- 标题→h1/h2，列表→ul/ol，加粗→strong，基于语义映射
- 支持自定义 style map（如把 `WarningHeading` 映射到 `h1.warning`）
- 多语言版本：JavaScript、Python、Java/JVM、.NET
- 输出 HTML 片段（UTF-8），不是完整 HTML 文档
- 页眉页脚支持有限（docx-preview 更好）
- BSD-2-Clause，约 2.17MB

**docx-preview vs mammoth.js vs docxtemplater 对比**：

| 库 | 定位 | 保真度 | 可编辑 | 模板化 | Stars | 许可证 |
|---|---|---|---|---|---|---|
| **docx-preview** | 浏览器渲染预览 | 高（还原排版） | ❌ | ❌ | 2,030 | Apache-2.0 |
| **mammoth.js** | 语义内容提取 | 中（语义优先） | ❌ | ❌ | 6,268 | BSD-2-Clause |
| **docxtemplater** | 模板数据合并 | 低（模板填充） | ❌ | ✅✅✅ | 3,608 | MIT |
| **jszip** | 底层 ZIP 解压 | — | — | — | 10,367 | MIT/GPL |
| **officegen** | 从零生成 Office | — | ❌ | 部分 | 2,714 | MIT |

**使用策略**：
- 只需要预览 → docx-preview
- 需要 AI 理解文档内容 → mammoth.js 提取语义
- 需要把数据填入 Word 模板 → docxtemplater
- 二者常配合：mammoth 提取内容给 AI 处理，docx-preview 展示原貌

### 2.4 富文本编辑器（ProseMirror / Lexical / TipTap / Slate.js）

这类方案是构建**自定义文档编辑器产品**的基石——你掌控文档模型、编辑行为、协作逻辑，而不是套用现成 Office 界面。这正是"AI 文档可视化+编辑"产品最需要的层。

#### 2.4.1 四大编辑器框架对比（2026 年）

| 编辑器 | 底层 | 框架支持 | AI 内置 | 协作 | 上手时间 | 许可证 | 适合 |
|---|---|---|---|---|---|---|---|
| **TipTap** | ProseMirror | React/Vue/Svelte | 付费 AI 工具包 | Hocuspocus(Yjs) | 2-4 周 | MIT 核心 + 付费云 | 自定义编辑器产品 |
| **Lexical** | Meta 自研 | React 优先 | 需自建 | Yjs 绑定 | 4-6 周 | MIT | 完全定制、极致性能 |
| **Plate** | Slate.js | React | 需自建 | Yjs | 4-6 周 | MIT | Notion 风格块编辑 |
| **CKEditor 5** | 自研 | React/Angular/Vue | 付费 AI | 自有方案 | 1-3 小时 | GPL/商业 | 企业 CMS |
| **Editor.js** | 自研 | 框架无关 | ❌ | 需配 | 2 小时 | Apache-2.0 | 块式（Notion 风格） |

#### 2.4.2 TipTap——本场景的首选

**为什么 TipTap 最适合"AI 文档可视化+编辑"**：
1. **docx 导入导出**：`@tiptap-pro/extension-import-docx` 和 `extension-export-docx` 实现 docx↔编辑器 JSON 双向转换（导入走云端转换 API，导出纯客户端）
2. **ConvertKit**：为 docx 往返专门设计的 schema（段落间距、图片裁剪、表格单元格格式），保证 round-trip 质量
3. **协作成熟**：Hocuspocus（基于 Yjs CRDT）提供实时多人编辑，有云端托管版（$149-999/月）或自部署
4. **扩展生态**：50+ 官方扩展（表格、任务列表、@提及、占位符等），一行配置添加
5. **被 Notion、纽约时报、Atlassian 编辑器使用**（底层 ProseMirror）

**TipTap 的 docx 端到端流程**：
```
docx 文件 → import-docx 扩展（发到 Tiptap Convert API）→ Tiptap JSON → 编辑器渲染
                                                                      ↓ 用户编辑
docx 文件 ← export-docx 扩展（纯客户端）← Tiptap JSON ←·····
```

**注意**：round-trip 不是逐字节相同（下标/上标、段落行高、浮动表格有损耗），详见 Tiptap 特性支持矩阵。

#### 2.4.3 TipTap 中构建 AI Copilot 的实战模式（来自 Liveblocks 案例）

Liveblocks 为客户 Distribute 在 TipTap 编辑器里构建 AI Copilot 的关键技术决策值得直接借鉴：

1. **让 LLM 输出完整文档而非"编辑操作序列"**
   - 一开始尝试让 LLM 输出"引用 node ID 的编辑操作流"——不稳定（模型容易丢失结构、破坏引用、输出畸形操作）
   - **反转方案**：模型输出**完整编辑后的文档**（用受限的 JSX 风格标记，镜像 schema），并附简短"改了什么为什么"的注释；然后系统自己 diff 出精确编辑

2. **扩展文本 diff（extended-text diffing）**
   - 纯字符/词 diff 会忽略 node 边界和语义
   - 纯树 diff 会把节点内文字编辑当成整节点替换
   - 混合方法：把文档展平成"带结构元数据的 token 序列"再 diff，兼顾两种视图

3. **流式响应实时化**
   - 不等完整模型响应才显示（会卡顿），而是 token 到达即流式生成 diff，用户能实时看 AI 工作
   - 挑战：流式文档不完整，需要临时缓冲和渐进渲染

4. **严格 schema 校验**
   - 系统提示词中明确允许的标记元素和"绝不修改"的特殊块
   - 保证 AI 输出不破坏文档结构

### 2.5 私有部署的文档协作平台

#### 2.5.1 三大自托管 Office 套件对比（2026）

| 维度 | OnlyOffice | Collabora Online | CryptPad |
|---|---|---|---|
| 许可证 | AGPL-3.0 | MPL-2.0 | AGPL-3.0 |
| 原生格式 | OOXML | ODF | 自定义加密；可导出 ODF/OOXML/PDF |
| Office 保真度 | ★★★★★ 最佳 | ★★★★ 良好 | ⚠️ 有限（仅导出） |
| 实时协作 | ✅ | ✅ | ✅ |
| 修订/批注/修订跟踪 | ✅ | ✅ | ⚠️ 基础 |
| **端到端加密** | ❌ | ❌ | ✅ |
| 桌面应用 | ✅ | ✅(LibreOffice) | ❌(PWA) |
| Nextcloud 集成 | ✅ 官方 | ✅ 官方 | ✅ 应用 |
| 资源要求 | 4GB RAM, 2vCPU | 4GB RAM, 2vCPU | 1GB RAM, 1vCPU |
| 免费用户限制 | 不限 | 20 连接/10 文档 | 不限 |
| 可自托管 | ✅ | ✅ | ✅ |

#### 2.5.2 Nextcloud + ONLYOFFICE/Collabora

**架构**：Nextcloud 作文件存储与权限管理，ONLYOFFICE/Collabora 作编辑引擎，通过 WOPI 或官方连接器集成。

**部署**（以 Collabora + Docker 为例）：
```yaml
services:
  collabora:
    image: collabora/code:25.04.9.2.1
    ports: ["9980:9980"]
    environment:
      - aliasgroup1=https://cloud.example.com:443  # WOPI host
      - extra_params=--o:ssl.enable=false --o:ssl.termination=true
      - server_name=office.example.com
    cap_add: [MKNOD]
```
Nextcloud 侧安装 Nextcloud Office 应用，填入编辑器 URL 即可。点击文档即在 Collabora 编辑器中打开，支持多人实时编辑。

**关键配置陷阱**：必须设置 `net.frame_ancestors` 允许你的 Nextcloud 域名嵌入 iframe，否则会"连接被拒绝"。

#### 2.5.3 CryptPad——端到端加密首选

**独特价值**：文档在客户端加密，**连服务器运维方都无法读取内容**。基于 ChainPad（CRDT 变体），AGPL-3.0，XWiki SAS 维护，获荷兰/法国公共资金。

**部署**：Debian 12、2GB RAM、2 CPU、20GB 存储、Node.js LTS。2025.12.0 版起 OnlyOffice 组件需单独安装脚本。

**适用**：隐私敏感场景（法律、医疗、政务），但 Office 格式保真度有限，更适合内部协作而非对外交付 Word。

### 2.6 小结：Word/docx 方案选型决策

```
需要"像 Word 一样编辑"？
├─ 是 → 需要 OOXML 高保真？
│       ├─ 是 → ONLYOFFICE Docs（Community 免费私有部署）
│       └─ 否（用 LibreOffice 体系）→ Collabora Online
└─ 否（要自定义编辑器/嵌入产品）
        ├─ 只读预览
        │       ├─ 高保真排版 → docx-preview
        │       └─ 提取语义内容给 AI → mammoth.js
        └─ 可编辑
                ├─ 要 docx 往返 → TipTap + ConvertKit + import/export-docx
                └─ 纯内部格式 → TipTap / Lexical / Plate
```

---

## 3. 调研 B：LaTeX/PDF 可视化编辑和实时预览

### 3.1 Overleaf 开源方案

#### 3.1.1 Overleaf Community Edition（CE）

**定位**：业界标杆在线 LaTeX 编辑器的开源自托管版本，基于 Ruby on Rails + Node.js + MongoDB + Redis + LaTeX（TeX Live）。

**CE vs Server Pro 功能对比**：

| 功能 | Community Edition | Server Pro |
|---|---|---|
| 强大的 LaTeX 编辑器 | ✅ | ✅ |
| 完整项目历史 | ✅ | ✅ |
| 评论 | ❌ | ✅ |
| 实时 track changes | ❌ | ✅ |
| 内部协作 | ❌ | ✅ |
| 私有模板管理 | ❌ | ✅ |
| Git 集成 | ❌ | ✅ |
| 符号面板 | ❌ | ✅ |
| SSO（SAML/LDAP） | ❌ | ✅ |
| **沙箱编译** | ❌ | ✅ |
| 优化的 TeX Live | ❌ | ✅ |

**重要警告**：CE **没有沙箱编译**——LaTeX 编译以容器同等权限运行，可访问文件系统/网络/环境变量。**不适合多用户或生产环境**，仅限完全可信环境。生产部署强烈建议 Server Pro。

**部署**：官方提供 toolkit（Docker Compose），社区也有 LXC 单脚本安装（Ubuntu 24.04）。基线约 8GB RAM。

**适用**：自托管给可信小团队的在线 LaTeX 编辑器。对于本项目（harryopo LaTeX 模板体系），如果想做"在线预览+编辑 LaTeX"，Overleaf CE 是生产级选择，但需注意安全限制。

### 3.2 LaTeX 实时预览（浏览器内编译）

#### 3.2.1 WebAssembly LaTeX 引擎家族

| 项目 | 引擎 | 大小 | 特色 | 状态 |
|---|---|---|---|---|
| **SwiftLaTeX** | pdftex.wasm / xetex.wasm / dvipdfm.wasm | ~数 MB | 可选 WYSIWYG（WIP），纯本地计算 | 活跃 |
| **TexLive.js** | TeX Live → WASM | 大 | 全功能 TeX Live，含所有包 | 维护 |
| **Siglum** | busytex.wasm（TeX Live 2025） | 29MB 引擎 + 195MB 包 | 懒加载包，CTAN 代理 | 活跃（2026） |
| **WasmTex** | pdfLaTeX WASM + 多引擎 | 中 | 内置 LSP、SyncTeX、Monaco、pdf.js | 活跃（2026） |
| **TeXbrain** | TeX Live WASM + pdf.js | — | 含 git 集成、本地 FS 访问、增量编译 | 活跃（2026） |

#### 3.2.2 WasmTex——最完整的嵌入式方案

WasmTex 是一个**可嵌入的浏览器 LaTeX 编辑器 SDK**，值得重点关注：
- Monaco 编辑器 + 浏览器内 pdfLaTeX（WASM）+ PDF.js 实时预览
- 自动检测需要 XeLaTeX/LuaLaTeX 的文档（fontspec、unicode-math、CJK、`\directlua`），路由到完整多引擎管线
- 内置 LaTeX 语言服务器（补全、悬停、跳转定义、诊断、ChkTeX 风格 linter、签名帮助、折叠）
- SyncTeX 支持 PDF↔源码双向定位
- TeX Live 包从公共 CDN 流式加载，无需自托管
- 多入口：`wasmtex`（完整 SDK）、`wasmtex/headless`（无 DOM 编译器）、`wasmtex/node`（Node 运行）、`wasmtex/lsp`（语言服务核心）

**对本项目意义**：若要把 harryopo 模板做成"浏览器里写 LaTeX 实时看 PDF"，WasmTex 提供了比 Overleaf 轻量得多的嵌入式方案，且天然支持 XeLaTeX（本项目硬性要求）。但 WASM 引擎对中文字体（方正、XITS）的支持需要验证——这是已知风险点。

### 3.3 VS Code + LaTeX Workshop 的本地可视化

本地开发的标准方案：
- **LaTeX Workshop** 扩展：编译 + 实时 PDF 预览 + 正反向跳转（SyncTeX）
- **Tinymist**（Typst 体系）：已取代废弃的 Typst LSP / Typst Preview 插件
- **File System Access API**（Chrome/Edge）：允许浏览器编辑器直接读写本地项目文件夹（TeXbrain 即用此 API）

**对本项目**：CLAUDE.md 已规定"必须用 XeLaTeX，编译 3 遍"，VS Code + LaTeX Workshop 是本地开发主战场，在线方案是补充。

### 3.4 PDF 在浏览器中标注/编辑

#### 3.4.1 核心库对比

| 库/产品 | 类型 | 标注能力 | 编辑能力 | 许可证 | 适合 |
|---|---|---|---|---|---|
| **pdf.js**（Mozilla） | 开源基础 | 需自建叠加层 | 只读 | Apache-2.0 | 渲染底座 |
| **react-pdf-highlighter-plus** | 开源 React | 高亮、区域、自由文本、手绘、形状、签名、搜索、导出 | 标注级 | MIT | React 应用标注 |
| **pdfjs-annotation-extension-for-react (InkLayer)** | 开源 React | 13 种标注工具、原生 PDF 标注编辑、评论回复 | 标注级 | 已弃用 | 企业级标注 |
| **PSPDFKit / Nutrient** | 商业 | 全功能 | 全功能（含 Document Authoring） | 商业 | 商业产品 |
| **pdf-lib** | 开源 | 程序化 | 创建/合并/修改 | MIT | 后端/程序化处理 |

**典型架构**：pdf.js 渲染 PDF → Canvas/SVG 叠加层捕获交互 → 标注数据以 JSON 存储（与页面坐标系绑定，跨屏幕尺寸可移植）→ 可导出回 PDF 或单独存储。

#### 3.4.2 react-pdf-highlighter-plus 能力清单

值得重点关注的开源 React 标注库，基于 PDF.js，视口无关坐标存储：
- 文本高亮（可选/复制/改样式）
- 区域高亮（Alt+拖拽矩形）
- 自由文本便签（可拖动、可编辑、自带样式面板）
- 图片与签名（上传或手绘）
- 自由手绘
- 形状（矩形/圆/箭头，可编辑描边）
- PDF 内全文搜索（上/下一个导航）
- 导出带标注的 PDF
- 明暗主题、缩放、完全可定制样式

**对本项目意义**：如果产品需要"AI 生成 PDF → 用户在 PDF 上批注修改意见 → AI 据此再修改"，这类库提供了标注层；但**真正的文本编辑还得回到源文档（LaTeX/docx）层面**，PDF 标注只能作为"修改意图"的载体。

### 3.5 Typst 的在线编辑

#### 3.5.1 Typst 简介

Typst 是 Rust 写的现代排版系统，目标是"LaTeX 级排版能力 + 比 LaTeX 易学得多"：
- 类 Markdown 轻量语法（`= Title`、`*bold*`、`$x^2$`）
- 增量编译，毫秒级实时预览（vs LaTeX 数十秒）
- 内置图灵完备脚本语言（变量、函数、条件、循环）
- 内置参考文献（YAML + CSL）
- 清晰错误提示（行号列号 + 友好描述 + 修复建议）

#### 3.5.2 在线编辑生态

| 方案 | 类型 | 特色 |
|---|---|---|
| **typst.app** | 官方托管 | 协作、云存储、团队 |
| **Tinymist** | LSP（VS Code 等） | 语法高亮、补全、诊断、格式化（Typstyle）、实时预览；已整合废弃的 Typst LSP/Preview 插件 |
| **typst.ts** | WASM 编译器 | 浏览器内编译 |
| **tyraria** | 开源在线编辑器 | 基于 tinymist + typst.ts 复刻 typst.app 体验，Vue + Monaco |
| **TeXlyre** | 开源协作平台 | LaTeX + Typst，Yjs CRDT，WebRTC P2P，SwiftLaTeX WASM，AGPL-3.0 |
| **giga.tools Typst Editor** | 在线免注册 | 浏览器内 WASM 编译，隐私优先 |

**对本项目意义**：Typst 是 LaTeX 的潜在替代，但目前 harryopo 体系深度绑定 LaTeX/ctex/XeLaTeX，迁移成本高。Typst 可作为**未来简化排版的备选**——尤其对"AI 生成 → 用户改 → 输出"的场景，Typst 的毫秒级预览体验远优于 LaTeX。若新建产品线，Typst 值得认真评估。

---

## 4. 调研 C：AI 生成 → 人审阅编辑 → 再生成的交互模式

这是本调研最核心的部分——回答"AI 做的肯定有些要修改，怎么让修改体验最好"。

### 4.1 四种主流 AI 编辑交互范式

| 范式 | 代表 | 人控制粒度 | 实现复杂度 | 适合文档类型 |
|---|---|---|---|---|
| **Inline Diff（Cursor 风格）** | Cursor, Athens, doXmind | 逐词/逐句 | 中 | 代码、结构化文档 |
| **建议模式（Track Changes）** | Google Docs+Gemini, Word+Copilot | 逐处接受/拒绝 | 中-高 | 长文、协作文档 |
| **全文重生成（Artifacts）** | Claude Artifacts | 整体接受/重生成 | 低 | 原型、短文档 |
| **对话式编辑（Canvas）** | ChatGPT Canvas, Notion AI | 选段+对话指令 | 中 | 写作、迭代文档 |

### 4.2 Inline Diff 模式（Cursor 风格用于文档）

#### 4.2.1 模式描述

来自编程界 Cursor 的"Cmd+K"内联编辑模式，被 Athens、doXmind 等写作工具移植到文档：
1. 选中一段文字
2. 用自然语言描述要怎么改
3. AI 生成修改，以**内联 diff**呈现：绿色新增、红色删除
4. 用户**逐处接受/拒绝**，或批量操作
5. 接受后自动创建版本快照

**为什么这个模式适合"AI 文档可视化+编辑"**：
- **可见性**：用户看到 AI 改了什么，不是"拿到一个新版本再心算对比"
- **颗粒度**：AI 改了五句话，可以接受三句拒绝两句
- **安全感**：主导权在人，AI 不会偷偷改文档
- **快**：比"复制到 ChatGPT 改完再粘回来"快得多

#### 4.2.2 doXmind 的完整实现（"Cursor for Writing"）

doXmind 是这一范式的典型产品，其功能集值得参考：
- **AI 自动补全**：上下文感知幽灵文本，短补全（词/短语）+ 长补全（标题/冒号/列表后多句续写），Tab 接受
- **AI 对话+文档工具**：AI 不只回复，通过工具**直接编辑文档**，支持联网、深度思考、图片视觉分析
- **快捷编辑**：选中→右键→修语法/提清晰度/精简/扩写/调语气/翻译
- **差异审阅**：每处 AI 编辑都是行内 diff，快捷键导航，逐条/批量接受拒绝，接受后自动版本快照
- **写作审阅**：四维全文分析（正确性/清晰度/语气/吸引力），每条建议分类，可逐条采纳
- **知识库**：上传 PDF/DOCX/PPTX 作参考，AI 引用并基于自有素材建议
- **版本历史**：时间线 + 类型徽章（手动/AI/快捷编辑/恢复），预览/diff/一键恢复

### 4.3 建议模式（Google Docs + Gemini / Word + Copilot）

#### 4.3.1 Google Docs + Gemini 的"评论工作流"（2026 年 7 月上线）

Google 把评论从"被动标注"变成了 Gemini 可处理的原材料，四种能力：
1. **评论摘要与问答**：综合几十个开放讨论帖，提取主题、行动项、未解决问题（"总结 Sarah 的所有评论"、"这份文档还有哪些未解决问题"）
2. **主动插入评论**：Gemini 作为"文字编辑"在文中插入评论，或 @特定成员要求数据核实
3. **上下文草稿回复**：在开放帖中生成回复，并可搜索 Google Drive 附加相关文件
4. **直接编辑建议**：根据审阅者反馈重写段落或整节（"重写引言以回应 Roberta 的反馈"→生成建议编辑→用户一键审阅批准）

**关键设计**：所有动作都是**草稿**，用户必须手动批准——Gemini 不会自主发布评论或执行永久文本修改。

**2026 年 4 月 Docs 更新**还加了：
- 持久底部栏（pill 形，带提示词框和 `@`/附件菜单）
- 编辑现在以"**仅你可见的建议编辑**"形式到达，直到你批准/拒绝（而非直接粘进文档）
- Refine 菜单：一键改写/缩短/扩写/项目化/总结 + "匹配写作风格"（扫全文统一语调）+ "匹配文档格式"（镜像参考稿的字体/标题/表格）

#### 4.3.2 Microsoft Word + Copilot

- 每处 AI 编辑以**精确到词的 tracked change**出现，可逐处接受/拒绝
- 读取并回复锚定到对应文档段的评论帖
- 生成/更新摘要、插入带动态字段的页眉页脚、多步骤编辑的实时进度消息
- 基于 Work IQ 层适配组织和用户画像
- 2026 年 4 月发布、6 月正式可用，需 Microsoft 365 Copilot 许可

### 4.4 全文重生成模式（Claude Artifacts）

#### 4.4.1 模式特点

Claude Artifacts 在聊天旁的渲染窗格实时渲染代码/HTML/React/SVG/Markdown：
- 每次修订请求**重生成整个 artifact**（不像 Canvas 跟踪行级编辑）
- 不支持用户在 artifact 窗口内直接编辑（通过 prompt 迭代）
- 2026 年 4 月起 Cowork 支持连接 MCP 服务器的"live artifacts"——可从数据库/API 刷新真实数据

**优劣**：
- 优：适合交互原型（计算器、图表、小游戏），即时渲染
- 劣：迭代细化不够流畅（每次整体重生成），长文档编辑体验差

### 4.5 对话式编辑模式（ChatGPT Canvas / Notion AI）

#### 4.5.1 ChatGPT Canvas

- 打开**全宽工作区**在对话旁，像"Google Docs + 左侧研究笔记"
- 用户**直接在工作区编辑文档**，无需再发提示
- 可高亮一句让 GPT 只改那段
- 支持 File Search 和 Code Interpreter
- 可分享链接，接收者查看/编辑（需 ChatGPT 账号）
- 手动版本历史
- 写作模式 + 编码模式自动切换

#### 4.5.2 Notion AI

- 多级触发：斜杠命令 `/ai`、空行按空格、选中→"万事问 AI"
- 高亮文本→下拉菜单改写/翻译/总结/提取待办
- `/summarize`、`/action items`、`/自定义 AI 区块`（结合页面上下文生成独特内容）
- Notion Agent（2025）：接管任务从头到尾，查看工作区+连接应用，创建/编辑页面/数据库/图表
- 可个性化 Agent 外观，用"指令和技能"塑造响应方式
- 审阅与批准：Agent 提案需用户批准后才执行

### 4.6 四种模式横向对比与选型

| 维度 | Inline Diff (Cursor/Athens) | 建议模式 (Gemini/Copilot) | 全文重生成 (Artifacts) | 对话式 (Canvas/Notion) |
|---|---|---|---|---|
| **人控制粒度** | 逐词/句 | 逐处 | 整体 | 选段 |
| **可见性** | ★★★★★ 最强 | ★★★★ | ★★★ | ★★★★ |
| **长文档适配** | ★★★★ | ★★★★★ | ★★ | ★★★★ |
| **实现复杂度** | 中（需 diff 引擎） | 中-高（需 track changes） | 低 | 中 |
| **AI"理解"文档** | 部分 | 上下文+评论 | 整体重写 | 选段上下文 |
| **协作支持** | 可加 | 原生强 | 弱 | 中 |
| **适合"AI 办公文档"** | ★★★★ | ★★★★★ | ★★ | ★★★★ |

**对本项目的推荐**：**Inline Diff + 建议模式混合**——
- 大段 AI 生成/重写时用 Inline Diff（让用户看到每处变化）
- 局部润色/修订时用建议模式（接受/拒绝单点）
- 避免全文重生成（丢失用户已认可的部分）

### 4.7 版本对比与审计（Git 风格）

一个被多数工具忽略但重要的发现（来自 Provenance 项目的 UI 研究）：

> **没有任何现有工具在接受内容后保留持久的 AI 来源标记，也没有工具提供 AI 交互的审计追踪。** 每个写作工具——Google Docs、Notion、Lex、Wordtune、Grammarly——在接受建议的那一刻就失去了 AI 文本和人类文本的区分。

这既是差异化机会，也是合规风险。doXmind 的"版本历史带类型徽章（手动/AI/快捷编辑/恢复）"是值得借鉴的审计方案。

**可迁移的 10 大模式**（来自 30+ 工具研究）：

| # | 模式 | 来源 | 适用界面 |
|---|---|---|---|
| 1 | 内联 diff + track changes 样式 | Cursor Cmd+K | 编辑器（内联 AI） |
| 2 | 多个备选建议同时展示 | Wordtune, Copilot | 编辑器（内联 AI） |
| 3 | 三级 AI 升级（环境→范围→探索） | Cursor | 编辑器（所有 AI 模式） |
| 4 | 按会话分组的时间线 | Slack + GitHub | 验证页 |
| 5 | 渐进披露 + 类型徽章 | Stripe | 验证页 |
| 6 | 发布前后果警告 | GitHub PR + Substack | 徽章预览 |
| 7 | 文本来源颜色编码 | iA Writer | 编辑器（来源标记） |
| 8 | 快速事件自动分组 | Google Docs history | 验证时间线 |
| 9 | 全宽行列表 + 元数据 | Linear, Vercel | 仪表盘 |
| 10 | 建议卡片 + refine 循环 | Google Docs+Gemini | 编辑器（AI 建议） |

---

## 5. 调研 D：最前沿的可视化方案

### 5.1 AI 文档生成的"可视化中间态"

#### 5.1.1 核心问题

传统"一次性输出"模式痛点：
- **等待焦虑**：长文本生成 5-15 秒空白+转圈，用户以为坏了
- **纠错滞后**：方向错了只能全重来或手动大段改
- **过程不可控**：无法在生成中介入
- **缺乏手感**：剥夺观察逻辑演进的机会

#### 5.1.2 流式输出范式改变

AgentCPM 研报助手等工具把"生成-等待-接收"单向过程，变成"发起-观察-互动"协同过程：
- **实时质量监控**：边生成边读，发现偏差立即停止调整
- **理解 AI 逻辑**：观察从主题句到论据到下一章的展开
- **提升参与感**：人机协同增强回路
- **缓解等待压力**：文字持续出现提供积极反馈

### 5.2 流式生成 UX 的工程要点

来自多份流式 UX 研究的关键工程实践：

#### 5.2.1 布局稳定性
- **预留空间**：流式容器设 `min-height`（聊天 120-200px，长文更高），防止下方内容跳动
- `contain: layout` 告诉浏览器元素内尺寸变化不触发全页重排
- 完成后 `min-height: auto`

#### 5.2.2 滚动锚定
- **不要每个 token 都 `scrollToBottom()`**——用户滚上去读历史时被强制拉回来是最差的
- 用 IntersectionObserver 检测用户是否在底部，在底部才自动滚，否则显示"跳到最新"按钮（Slack/Discord 模式）

#### 5.2.3 打字指示器
- 发送到首个 token 有 200ms-数秒空窗
- 三点打字指示器或骨架屏填补，且必须**平滑过渡到真实内容**（指示器应在首个 token 将出现的位置，淡出）

#### 5.2.4 结构化内容处理
- 流式中的代码块/表格是语法不完整的，增量渲染会出错
- 检测到代码围栏或表格开始时，**缓冲 token 直到块完整**再整体渲染（显示"生成代码中..."骨架）
- Markdown 用流式感知解析器（如 marked 的流式模式）

#### 5.2.5 格式即时应用
- 粗体、标题、列表在流式过程中就应用格式，不要等完成
- 显示闪烁光标在生成点，传达"正在写"而非"正在加载"

### 5.3 结构化数据是可靠 AI 编辑的基石

来自 AI 简历构建器实战的关键洞察：

> AI 编辑文档"失控"的根因不是 AI 的意图问题，而是**缺乏约束**。没有结构，同一个请求可能重写整个技能区、丢掉一半工作经历、生成不像你的摘要。

**三大核心要求**：
1. **Schema**：每个字段有可预测结构，UI 一致渲染
2. **实时反馈**：改动即时出现，不等不猜
3. **外科手术式更新**：修改精确目标，不碰相邻内容

**为什么结构防错**：
- **隔离**：每个字段在特定路径（`/skills/0/name`），编辑不会溢出到相邻内容
- **校验**：Schema 强制在数据到达文档前捕获畸形数据
- **可预测**：UI 知道如何渲染每种字段类型，无论谁改的

**对本项目的直接启示**：**不要让 AI 直接生成"扁平文本"再渲染**。应该让 AI 生成/编辑**结构化中间表示**（如 ProseMirror JSON、带 schema 的 Markdown、或自定义 JSON），由前端按 schema 渲染。这正是 TipTap/ProseMirror schema 系统的价值。

### 5.4 对话式编辑文档的产品全景

| 产品 | 模式 | 特色 | 局限 |
|---|---|---|---|
| **ChatGPT Canvas** | 对话+工作区 | 直接编辑、选段改写、版本回退、分享协作 | 需 ChatGPT 账号，无实时多人 |
| **Claude Artifacts** | 渲染窗格 | 实时渲染 HTML/React/SVG/Mermaid，可发布/嵌入 | 不支持窗内直接编辑，整体重生成 |
| **Notion AI / Agent** | 块级+Agent | 多级触发、知识库、Agent 全流程接管 | 限于 Notion 生态 |
| **Athens** | Inline diff | Cursor 风格写作、Markdown WYSIWYG、双 AI 模式 | 新产品，生态小 |
| **doXmind** | Inline diff + 审阅 | 四维写作审阅、知识库、版本审计、演示模式 | 桌面端，本地优先 |
| **Type.ai** | 对话+应用 | 全文审阅、风格学习、大上下文 | 聊天优先模型 |
| **Lex** | 块级 | 极简写作 | AI 较弱 |

---

## 6. 调研 E：技术栈选型与最佳架构方案

### 6.1 推荐架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                        浏览器前端                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 对话/指令面板 │  │ TipTap 编辑器 │  │ 预览面板          │  │
│  │ (AI 触发)    │←→│ (ProseMirror) │←→│ docx-preview /   │  │
│  │              │  │ + Yjs 协作    │  │ pdf.js / WASM    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│         │                ↑ diff ↓ accept/reject              │
│         │          ┌──────────────────┐                      │
│         └────────→ │ AI 编辑层        │                      │
│                    │ (inline diff 渲染)│                      │
│                    └──────────────────┘                      │
└────────────────────────────┬────────────────────────────────┘
                             │ WebSocket (Yjs) / SSE (流式)
┌────────────────────────────┴────────────────────────────────┐
│                        后端服务                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ LLM 网关  │  │ Hocuspocus   │  │ 输出引擎              │  │
│  │ (流式)   │  │ (Yjs 协作服务)│  │ pandoc/python-docx/  │  │
│  │          │  │              │  │ XeLaTeX              │  │
│  └──────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 业务层：项目管理、权限、版本、审计                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 前端选型

#### 6.2.1 框架：React 19 / Next.js 15

**理由**：
- 编辑器组件生态最丰富（TipTap、Lexical、Plate 都是一等 React 公民）
- react-pdf-highlighter-plus 等标注库原生 React
- Next.js App Router + Server Components 对 AI 流式场景友好
- 团队若强 Vue，TipTap 也一等支持 Vue（无损失）

#### 6.2.2 编辑器：TipTap（ProseMirror）

**为什么不是 Lexical/Plate**：
- **docx 往返**：TipTap 有官方 import-docx/export-docx 扩展（付费 Pro，但解决了最难的部分）；Lexical/Plate 需自建 docx 转换
- **协作成熟度**：Hocuspocus 是最成熟的协作方案；Lexical 的 Yjs 绑定较新，Plate 需替换协作基础设施
- **扩展生态**：50+ 官方扩展覆盖大部分需求
- **业界背书**：底层 ProseMirror 驱动 Notion、纽约时报、Atlassian

**什么情况选 Lexical**：追求极致性能（5000+ 节点文档 Lexical 比 ProseMirror 快 20-40%）、完全自定义文档模型、React 深度集成。

**什么情况选 Plate(Slate)**：要 Notion 风格块编辑器、独特文档模型。

#### 6.2.3 协作与 AI 同步：Yjs

**为什么 Yjs 而非 OT/自建**：
- **CRDT 数学保证收敛**：无需中央服务器仲裁，离线编辑自动合并
- **业界标准**：Notion、Figma 等都用 Yjs 或类似 CRDT
- **编辑器绑定成熟**：y-prosemirror（TipTap 用）、y-lexical 都有
- **传输无关**：WebSocket、WebRTC、IndexedDB（离线）都支持

**生产架构**：
- **Hocuspocus**（Node.js）作协作服务：WebSocket 连接、操作中继、持久化、权限
- 可自部署或用云端托管（$149-999/月）
- 新人加入时同步状态向量，增量更新二进制编码压缩传输

**Yjs vs Automerge 选型**：
- 测量和文档大小：Yjs 通常更紧凑
- 需要保留多少历史：影响 tombstone 膨胀
- 生态深度：Yjs 编辑器绑定更多

#### 6.2.4 预览层

| 目标格式 | 推荐组件 | 备注 |
|---|---|---|
| docx 高保真预览 | docx-preview | 与编辑器并排，展示"将导出的样子" |
| PDF 预览 | pdf.js + react-pdf-highlighter-plus | 支持标注 |
| LaTeX 实时预览 | WasmTex（嵌入式）/ Overleaf CE（完整产品） | WasmTex 更轻，Overleaf 更重 |
| Typst 预览 | typst.ts + tinymist | 毫秒级，未来备选 |

### 6.3 AI 编辑层设计

#### 6.3.1 核心原则（综合各方案最佳实践）

1. **AI 输出完整编辑后的文档（结构化），系统自己 diff**——不让 LLM 输出"操作序列"（不稳定）
2. **用受限标记/JSON 镜像编辑器 schema**——系统提示词明确允许的元素和"绝不修改"的块
3. **流式 token 即时生成 diff**——不等完整响应，实时渲染 AI 工作
4. **扩展文本 diff**——展平为带结构元数据的 token 序列再 diff，兼顾语义和颗粒度
5. **inline diff + 接受/拒绝**——人保留最终控制权，逐处或批量
6. **接受后版本快照 + 类型徽章**——审计追踪（手动/AI/快捷）

#### 6.3.2 AI 编辑 UX 三级升级（借鉴 Cursor）

| 级别 | 触发 | 范围 | 例子 |
|---|---|---|---|
| **环境（ambient）** | 自动，无显式请求 | 补全、提示 | Tab 补全、幽灵文本 |
| **范围（scoped）** | 选段+指令 | 选中部分 | 选中段落→"改成更正式的语气" |
| **探索（exploratory）** | 对话，开放 | 整文档 | "给这份报告加一节竞品分析" |

#### 6.3.3 保持 AI 冲突解决不在同步路径

来自生产经验的设计决策：
- AI 建议**不直接进 Yjs 文档**，而是作为"待审建议"层
- 用户接受后才提交为正式编辑（经 Yjs 正常流程）
- 避免 AI 慢响应阻塞协作同步

### 6.4 后端选型

#### 6.4.1 主服务：FastAPI（Python）

**理由**：
- 与 AI/LLM 生态最亲和（LangChain、torch、transformers 等都是 Python 优先）
- 异步原生（asyncio）适合流式 LLM 响应和 WebSocket
- 性能足够（非超高频场景）
- 团队若强 Node.js，可选 NestJS/Express

**职责**：
- LLM 网关（流式代理、重试、限流、成本控制）
- 文档 CRUD、项目管理、权限
- 触发输出引擎（pandoc/python-docx/XeLaTeX）
- 与 Hocuspocus 协作的权限钩子

#### 6.4.2 协作服务：Hocuspocus（Node.js）

独立 Node 进程，专门处理 Yjs WebSocket 连接和持久化，通过钩子与主服务协作做权限校验。

#### 6.4.3 输出引擎

| 目标 | 工具 | 说明 |
|---|---|---|
| **docx** | python-docx + Jinja2 模板 | 样式可控、模板化、可版本控制；或 docxtemplater（JS） |
| **PDF（普通）** | pandoc + LaTeX 引擎 / weasyprint | pandoc 通用转换 |
| **PDF（高质量排版）** | XeLaTeX（harryopo 体系） | 已有完整模板体系 |
| **格式互转** | pandoc | Markdown↔docx↔HTML↔PDF↔LaTeX↔epub |
| **PowerPoint** | python-pptx / reveal.js | 按需 |

**AI 生成 docx 的典型流水线**（来自实战案例）：
```
用户需求 → LLM 流式生成内容（分节）→ Jinja2 模板渲染占位符
→ python-docx 写入并应用预定义样式（CustomHeading1/CustomBody）
→ 表格自动填充 → docx.save()
```
关键：**用 `styles.add_style()` 一次性定义"标题1""正文缩进""表格正文"三类样式**，后续只引用样式名，格式 100% 统一。

### 6.5 实时预览和编辑的闭环

完整的"AI 生成 → 可视化 → 编辑 → 输出"数据流：

```
1. 用户在对话面板提需求
2. 后端 LLM 流式生成结构化内容（ProseMirror JSON / 带 schema Markdown）
3. 前端 TipTap 流式渲染（token 到达即插入，格式即时应用）
4. 用户在编辑器直接修改 或 通过对话指令让 AI 改
5. AI 编辑以 inline diff 呈现，用户逐处接受/拒绝
6. 接受的编辑进入 Yjs 文档，协作同步
7. 版本快照 + 审计徽章记录
8. 用户点"导出"→ 后端从 ProseMirror JSON 转 docx/PDF/LaTeX
9. 导出文件下载或在预览面板展示
```

**关键技术点**：
- 步骤 2-3：LLM 输出结构化（不是扁平文本），系统保证 schema 合规
- 步骤 5：diff 引擎用扩展文本 diff（结构感知）
- 步骤 8：导出是"单向"，编辑继续在内部表示上，导出是快照

---

## 7. 综合决策矩阵与落地路线图

### 7.1 按产品形态选型

| 产品形态 | 推荐方案 | 理由 |
|---|---|---|
| **"AI 写完一键出 Word"，少量编辑** | mammoth.js/docx-preview 预览 + 后端 python-docx 输出 | 最简单，够用 |
| **"像 Word 一样编辑 + AI 辅助"** | ONLYOFFICE CE 嵌入 + 其内置 AI | 完整 Office 体验，省自建编辑器 |
| **"自定义 AI 文档产品"（推荐）** | React + TipTap + Yjs + diff 审阅 + pandoc/python-docx 输出 | 最灵活，差异化空间大 |
| **"团队私有协作 + AI"** | Nextcloud + ONLYOFFICE/Collabora + AI 插件 | 现成平台，低开发量 |
| **"隐私优先"** | CryptPad + OnlyOffice 组件 | 端到端加密 |
| **"学术/排版精品"** | Overleaf CE 或 WasmTex + harryopo LaTeX | 排版质量最高 |

### 7.2 落地路线图（MVP → 完整产品）

#### Phase 1：MVP（验证核心闭环，2-4 周）
- React + TipTap 基础编辑器（段落/标题/列表/表格/图片）
- 对话面板 → LLM 流式生成 → 插入编辑器
- docx 导出（python-docx 或 TipTap export-docx）
- 基础版本历史

#### Phase 2：AI 编辑体验（4-8 周）
- Inline diff 渲染 + 接受/拒绝
- AI 三级升级（补全/选段改写/全文档指令）
- 结构化 schema 约束 AI 输出
- docx 导入（mammoth 或 TipTap import-docx）

#### Phase 3：协作与高保真（8-16 周）
- Yjs + Hocuspocus 实时协作
- docx-preview 高保真预览面板
- pdf.js 标注层
- 审计追踪（AI/人工来源标记）

#### Phase 4：高级输出（16+ 周）
- XeLaTeX 输出（对接 harryopo 体系）
- WasmTex 实时 LaTeX 预览
- 多格式导出（PDF/PPT/epub）
- 模板市场

### 7.3 关键风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| WASM LaTeX 引擎对中文字体支持不确定 | 在线 XeLaTeX 预览可能失败 | 先验证 XeLaTeX WASM + 方正/XITS 字体；不行则用服务端编译 |
| docx round-trip 不逐字节一致 | 导入再导出有损耗 | 明确告知用户；用 docx-preview 展示导出效果预览 |
| LLM 输出不遵守 schema | 破坏文档结构 | 严格系统提示 + 输出校验 + 重试；用"完整文档+系统 diff"而非"操作序列" |
| Yjs tombstone 膨胀 | 长文档内存增长 | 定期 GC；监控文档大小 |
| ONLYOFFICE AGPL 传染性 | 商业产品许可问题 | 用其作独立服务（iframe 集成）非衍生作品；或选 Collabora(MPL) |
| 流式渲染布局抖动 | 体验差 | 预留 min-height + IntersectionObserver 滚动锚定 |

---

## 8. 参考资料

### 在线 Office 套件
- [ONLYOFFICE Docs Docker 部署](https://helpcenter.onlyoffice.com/docs/installation/docs-developer-install-docker.aspx)
- [ONLYOFFICE DocSpace 3.7 自托管](https://www.onlyoffice.com/blog/2026/07/onlyoffice-docspace-3-7-server)
- [Collabora Online FAQ](https://www.collaboraonline.com/faqs/)
- [Collabora 与 OnlyOffice 对比](https://www.collaboraoffice.com/comparing-collabora-with-onlyoffice/)
- [Self-Hosting Collabora Online with Docker](https://selfhosting.sh/apps/collabora-online/)
- [Integrating Collabora with OpenCloud on Debian 13](https://pieterbakker.com/collabora-online-opencloud-debian-13-incus/)
- [OnlyOffice vs Collabora vs CryptPad 2026](https://ossalt.com/guides/onlyoffice-vs-collabora-vs-cryptpad-2026)
- [Best Document Collaboration Tools for Data Sovereignty (2026)](https://ones.com/blog/best-document-collaboration-tools-for-data-sovereignty-2026/)
- [CryptPad 安装指南](https://docs.cryptpad.org/en/admin_guide/installation.html)
- [ONLYOFFICE for Nextcloud](https://helpcenter.onlyoffice.com/es/integration/nextcloud.aspx)

### docx 前端处理
- [docx-preview vs mammoth vs docxtemplater 对比](https://npm-compare.com/docx-preview,docxtemplater,jszip,mammoth,officegen)
- [mammoth.js README](https://github.com/Jioho/mammoth.js/blob/master/README.md)
- [在浏览器中预览 docx 示例](https://jstool.gitlab.io/zh-cn/demo/preview-ms-word-docx-document-in-browser/)
- [online-docx-viewer (mammoth.js)](https://github.com/BaseMax/online-docx-viewer)

### 富文本编辑器
- [Best WYSIWYG Editor 2026](https://eddyter.com/blogs/best-wysiwyg-editor-2026-top-tools-for-modern-web-apps)
- [TipTap Import DOCX](https://tiptap.dev/docs/conversion/import/docx/editor-import)
- [TipTap Import DOCX REST API](https://tiptap.dev/docs/conversion/import/docx/rest-api)
- [TipTap 端到端 walkthrough](https://tiptap.dev/docs/conversion/getting-started/guides/end-to-end-walkthrough)
- [TipTap vs Lexical vs Plate 2026](https://kanopylabs.com/blog/tiptap-vs-lexical-vs-plate)

### LaTeX/PDF
- [Overleaf Server Pro vs Community Edition](https://docs.overleaf.com/on-premises/welcome/server-pro-vs.-community-edition)
- [Self-hosted Overleaf (Docker)](https://github.com/crawbear/OverleafRepo)
- [Self-host Overleaf in LXC](https://github.com/fauky/overleaf-lxc)
- [TeXbrain（浏览器 LaTeX + git + pdf.js）](https://github.com/swimmingbrain/texbrain)
- [Siglum（busytex WASM）](https://github.com/SiglumProject/siglum)
- [TexLive.js 介绍](https://blog.csdn.net/gitblog_00081/article/details/137036236)
- [SwiftLaTeX](https://github.com/ApertureBioLabs/SwiftLaTeX)
- [WasmTex](https://github.com/corca-ai/wasmtex)
- [react-pdf-highlighter-plus](https://www.npmjs.com/package/react-pdf-highlighter-plus-r17)
- [pdfjs-annotation-extension-for-react (InkLayer)](https://www.npmjs.com/package/pdfjs-annotation-extension-for-react)
- [PSPDFKit / Nutrient PDF SDK](https://pspdfkit.com)
- [Typst 快速开始（中文）](https://typst.dev/guide/quick-start.html)
- [tyraria（typst.app 开源复刻）](https://github.com/ParaN3xus/tyraria)
- [TeXlyre（LaTeX+Typst 协作）](https://alternativeto.net/software/texlyre/about/)
- [Online Typst Editor (giga.tools)](https://giga.tools/document-tools/typst-online-editor)

### AI 编辑交互
- [Google Docs Smart Review: Gemini](https://www.ubergizmo.com/2026/07/google-docs-smart-review-gemini-now-reads-replies-and-edits/)
- [Gemini Turns Google Docs Comments Into Action](https://www.remio.ac/post/gemini-turns-google-docs-comments-into-action-but-reviewers-still-hold-the-last)
- [Gemini in Google Docs: Deep Writing Workflow (2026)](https://aitoolsguidebook.com/en/articles/gemini-docs-deep-workflow/)
- [Alterações e comentários com IA: Gemini e Copilot](https://exame.com/tecnologia/examelab/alteracoes-e-comentarios-com-ia-como-usar-gemini-e-copilot-para-revisar-documentos/)
- [Claude Artifacts vs ChatGPT Canvas](https://techbink.com/claude-artifacts-vs-chatgpt-canvas/)
- [Claude artifacts vs ChatGPT Canvas: 2026 comparison](https://www.shareduo.com/blog/claude-artifacts-vs-chatgpt-canvas)
- [ChatGPT Canvas vs Claude Artifacts (teams)](https://aismartventures.com/posts/chatgpt-canvas-vs-claude-artifacts-which-ai-collaboration-feature-is-better-for-teams/)
- [Canvas 和 Artifacts 区别（中文）](https://cloud.tencent.com/developer/article/2461313)
- [Notion AI 使用指南（中文）](https://www.notion.com/zh-cn/help/guides/notion-ai-for-docs)
- [Notion AI FAQs](https://www.notion.com/vi/help/notion-ai-faqs)
- [Type.ai vs Athens（Cursor 风格写作）](https://tryathens.com/blog/type-ai-vs-athens)
- [doXmind（AI 原生写作平台）](https://github.com/doXmind)
- [Provenance UI/UX 竞品研究（30+ 工具）](https://github.com/benjaminshoemaker/provenance/blob/main/UI_RESEARCH.md)
- [Building an AI copilot inside your Tiptap text editor (Liveblocks)](https://liveblocks.io/blog/building-an-ai-copilot-inside-your-tiptap-text-editor)

### 流式生成 UX
- [Generative AI UX Patterns: Designing for Uncertainty](https://designpixil.com/blog/generative-ai-ux-patterns)
- [AI-Powered Resume Builder with Real-Time Streaming](https://www.nickroth.com/work/resume-chatbot/)
- [Designing for the Stream: UX Patterns for AI-Generated Content](https://reptile.haus/journal/designing-for-the-stream-ux-patterns-that-actually-work-for-ai-generated-content/)
- [AgentCPM 研报助手：流式输出](https://blog.csdn.net/weixin_27645199/article/details/159195067)

### 协作与 CRDT
- [CRDT based Peer-to-Peer Collaborative Editor](https://www.ijset.in/wp-content/uploads/IJSET_V14_issue2_400.pdf)
- [Docs 实时协作原理：Yjs CRDT 与 Hocuspocus](https://blog.csdn.net/gitblog_00938/article/details/153108265)
- [Ever wonder how real-time collaborative editing actually works](https://featuringcode.com/ever-wonder-how-real-time-collaborative-editing-actually-works)
- [How Real-Time Sync Works Under the Hood](https://www.sharecode.in/blog/how-realtime-sync-works)
- [Real-Time Collaborative Editing with CRDTs and AI](https://antigravitylab.net/en/articles/app-dev/antigravity-crdt-collaborative-editing)

### 技术栈与输出
- [ChatGPT 生成 Word 文档实战](https://blog.csdn.net/2600_94959803/article/details/157640422)
- [AI-Assisted Document Authoring Platform](https://github.com/vivekshahi918/ai-document-authoring)
- [DocGen（离线 AI 文档生成）](https://github.com/SanjayMarathi/DocGen)
- [Pandoc MCP Server](https://github.com/MaitreyaM/FILE-CONVERTER-MCP)

---

> **报告结语**：本调研覆盖了从纯前端渲染到完整 Office 套件、从 LaTeX WASM 到 Typst、从 Cursor 风格 diff 到 Gemini 建议模式、从 Yjs CRDT 到流式 UX 的全景。核心结论是：**开源生态已具备构建"AI 生成办公文档 → 浏览器可视化 → 途中可编辑 → 最终输出"完整闭环的所有组件**，关键在于围绕"结构化中间表示"这一核心理念，把 TipTap+Yjs+diff 审阅+多引擎输出有机组合。对本项目（harryopo LaTeX 体系）而言，XeLaTeX 输出层已就绪，前端可视化与 AI 编辑层是主要新增工作。
