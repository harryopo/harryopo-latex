# LaTeX 时序图构建方法调研报告

## 一、主流方案对比

| 方案 | 工具 | 特点 | 适用场景 |
|------|------|------|----------|
| **纯 TikZ 手绘** | TikZ + calc/arrows.meta | 灵活度高，完全自定义 | 复杂定制化需求 |
| **pgf-umlsd** | 专用宏包，基于 TikZ | 语法简洁，自动布局 | UML 标准时序图 |
| **tikz-uml** | 专用宏包，基于 TikZ | 功能丰富，支持多种 UML 图 | 复杂 UML 图 |

## 二、pgf-umlsd 调研（推荐方案）

### 2.1 核心优势
- **自动布局**：消息标签自动定位，避免与箭头重叠
- **标准 UML 语法**：`\begin{call}`、`\begin{messcall}`、`\begin{sdblock}` 等
- **内置调整机制**：`\postlevel`、`\prelevel` 解决文字重叠问题
- **成熟稳定**：v0.7，2009年发布，广泛使用

### 2.2 关键命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `\newthread{a}{:Thread A}` | 创建线程（参与者） | `\newthread{user}{:User}` |
| `\newinst[1]{i}{:Instance}` | 创建实例（对象） | `\newinst[1]{z}{:智配安装器}` |
| `\begin{call}{caller}{func()}{callee}{ret}` | 同步调用 | `\begin{call}{z}{扫描硬件}{d}{参数}` |
| `\begin{messcall}{from}{msg}{to}` | 消息传递 | `\mess{user}{启动应用}{z}` |
| `\begin{sdblock}{title}{desc}` | 组合片段（循环/条件） | `\begin{sdblock}{Loop}{拉取模型}` |
| `\postlevel` | 推迟当前消息时间轴 | 解决文字重叠 |
| `\prelevel` | 提前当前消息时间轴 | 多线程并行 |
| `\setthreadbias{west/center/east}` | 调整生命线偏移 | 避免多条线重叠 |

### 2.3 消息标签位置控制

pgf-umlsd 的消息标签**默认放在箭头上方**，不会遮挡箭头线条。当文字过多时：
- 使用 `\postlevel` 将消息时间轴推迟，为上方文字腾出空间
- 使用 `\prelevel` 将消息时间轴提前

### 2.4 完整示例

```latex
\documentclass{article}
\usepackage[margin=12mm]{geometry}
\usepackage[underline=true,rounded corners=false]{pgf-umlsd}

\begin{document}

\begin{sequencediagram}
    % 创建参与者
    \newthread{user}{: User}
    \newinst[1]{z}{: 智配安装器}
    \newinst[2]{d}{: 硬件检测}
    \newinst[3]{r}{: 推荐引擎}
    \newinst[4]{de}{: 一键部署器}
    \newinst[5]{b}{: 后端 API}
    \newinst[6]{o}{: Ollama}

    % 阶段1：推荐
    \begin{sdblock}{推荐}{推荐方案}
        \mess{user}{启动应用}{z}
        \begin{call}{z}{扫描硬件}{d}{参数}
            \begin{callself}{d}{执行检测}{}
            \end{callself}
        \end{call}
        \begin{call}{z}{传递参数}{r}{方案}
        \end{call}
    \end{sdblock}

    % 阶段2：确认
    \begin{sdblock}{确认}{用户确认}
        \mess{z}{展示方案}{user}
        \mess{user}{确认部署}{z}
    \end{sdblock}

    % 阶段3：请求
    \begin{sdblock}{请求}{后端调用}
        \begin{call}{z}{下发任务}{de}{}
            \begin{callself}{de}{编排部署}{}
            \end{callself}
        \end{call}
        \mess{de}{POST /api/install}{b}
    \end{sdblock}

    % 阶段4：安装
    \begin{sdblock}{安装}{Ollama安装}
        \begin{call}{b}{安装 Ollama}{o}{}
        \end{call}
        \postlevel
        \mess{o}{OK}{b}
    \end{sdblock}

    % 阶段5：拉取（循环）
    \begin{sdblock}{拉取}{Loop: 拉取模型}
        \mess{b}{POST /api/pull}{o}
        \mess{o}{流式进度}{b}
    \end{sdblock}

    % 阶段6：WebUI
    \begin{sdblock}{WebUI}{启动界面}
        \mess{b}{启动 WebUI}{o}
        \mess{o}{Ready}{b}
        \mess{b}{服务就绪}{de}
    \end{sdblock}

    % 阶段7：完成
    \begin{sdblock}{完成}{部署完成}
        \mess{de}{更新状态}{z}
        \mess{z}{部署成功}{user}
    \end{sdblock}

\end{sequencediagram}

\end{document}
```

## 三、最佳实践

### 3.1 文字不遮挡原则
1. **消息标签默认在箭头上方**：pgf-umlsd 自动处理
2. **文字过长时使用 `\postlevel`**：推迟消息时间轴，避免重叠
3. **返回消息用 `\mess`**：虚线箭头，标签在箭头下方
4. **自调用用 `\begin{callself}`**：指向自身的箭头，标签在旁边

### 3.2 布局优化
1. **参与者间距**：`\newinst[n]{name}{:Title}`，n 越大越靠右
2. **生命线偏移**：`\setthreadbias{west/center/east}` 避免多条线重叠
3. **组合片段**：用 `\begin{sdblock}` 包裹相关消息，增强可读性

### 3.3 视觉规范
1. **同步调用**：`\begin{call}` 实线 + 实心箭头
2. **异步消息**：`\mess` 实线 + 开放箭头
3. **返回消息**：`\postlevel` + `\mess` 虚线 + 开放箭头
4. **自关联**：`\begin{callself}` 指向自身的箭头

## 四、结论

**推荐使用 pgf-umlsd 宏包**，原因：
1. 自动处理消息标签位置，文字不会遮挡箭头
2. 语法简洁，符合 UML 标准
3. 内置 `\postlevel`/`\prelevel` 解决文字重叠问题
4. 支持组合片段（Opt/Loop/Alt）

**替代方案**：如果 pgf-umlsd 无法满足定制化需求，可以继续使用纯 TikZ，但需要：
1. 消息标签使用 `node[midway, above]` 放在箭头上方
2. 增大泳道间距，避免文字重叠
3. 使用 `\postlevel` 类似机制手动调整时间轴

## 五、下一步行动

1. 将当前时序图迁移到 pgf-umlsd 语法
2. 测试 `\postlevel` 解决文字重叠问题
3. 验证输出效果，确保文字不再遮挡箭头和参与者框
