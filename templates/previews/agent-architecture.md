# 基于大语言模型的多智能体协作架构设计与实现

作者：张明、李华

**摘要：** 大语言模型在单一智能体任务上表现优异，但在复杂长程任务中受限于单轮推理容量与工具调用的规模。本文提出一种基于大语言模型的多智能体协作架构，将规划器、执行器、检索器与审查器解耦为独立智能体，通过消息总线与协作调度算法实现任务分解、结果汇聚与质量回退。实验表明，该架构在 HotpotQA 与 MATH 基准上分别取得 12.4% 与 9.8% 的相对提升，同时将无效工具调用率降低至 6.2%。

**关键词：** 大语言模型；多智能体；协作调度；检索增强生成；消息总线

## 一、引言

近年来，以大语言模型（Large Language Model, LLM）为代表的通用推理引擎在代码生成、数学推理与问答任务上取得了突破性进展。然而，单个智能体在长程规划中常出现目标漂移（goal drift），且有限的上下文窗口难以容纳大量工具调用结果。为此，研究者提出将复杂任务分解为多个子任务，由分工明确的智能体协作完成。

多智能体协作的核心挑战在于**任务分解粒度**与**结果一致性**。设整体任务为 $T$，规划器将其分解为 $N$ 个子任务 $T = \{t_1, t_2, \dots, t_N\}$，每个子任务由对应的执行器处理。若分解粒度过粗，单智能体负担过重；若过细，则通信开销 $O(N^2)$ 迅速增长。本文通过层级规划与消息总线机制，将通信复杂度控制在 $O(N)$ 量级。

本文的主要贡献如下：

1. 提出解耦式多智能体架构，明确规划器、执行器、检索器与审查器的职责边界；
2. 设计基于注意力权重的协作调度算法，实现智能体间负载的动态均衡；
3. 构建可回退的质量审查链路，显著降低级联错误（cascading error）的传播。

## 二、相关工作

### 2.1 单智能体增强范式

链式思考（Chain-of-Thought）通过显式中间推理提升模型表现 [1]；ReAct 将推理与行动交替执行，使智能体具备感知环境的能力 [2]。Voyager 将技能库与 LLM 结合，实现终身学习型智能体 [3]。上述方法均局限于单上下文执行，无法并行利用多个领域的专业能力。

### 2.2 多智能体框架

AutoGen 提出基于对话的多智能体编排机制，通过可配置的对话策略实现角色分工 [4]。MetaGPT 将软件公司 SOP（Standard Operating Procedure）映射为智能体角色，以文档作为中间产物实现信息传递 [5]。本文与上述工作的区别在于：引入显式的调度层与审查回退机制，而非仅依赖自由对话达成一致。

## 三、系统总体架构

本系统采用"总线 + 角色"的分层架构，如图 1 所示。顶层为协作调度器，负责任务分解与负载均衡；中间层为消息总线，承载智能体间的结构化消息；底层为四个角色智能体，各自持有独立的工具集与记忆缓冲。

```super-diagram
{
  "type": "architecture",
  "canvas": {"width": 960, "height": 620, "theme": "light"},
  "title": "图1：多智能体系统总体架构（调度器、消息总线与四类角色智能体）",
  "subtitle": "调度器 → 消息总线 → 四类角色智能体",
  "nodes": [
    {"id": "scheduler", "en": "Scheduler", "zh": "协作调度器", "x": 400, "y": 60, "w": 160, "h": 64, "type": "backend"},
    {"id": "bus", "en": "Message Bus", "zh": "消息总线", "x": 120, "y": 260, "w": 600, "h": 56, "type": "bus"},
    {"id": "planner", "en": "Planner", "zh": "规划器", "x": 100, "y": 440, "w": 160, "h": 64, "type": "backend"},
    {"id": "executor", "en": "Executor", "zh": "执行器", "x": 300, "y": 440, "w": 160, "h": 64, "type": "backend"},
    {"id": "retriever", "en": "Retriever", "zh": "检索器", "x": 500, "y": 440, "w": 160, "h": 64, "type": "db"},
    {"id": "reviewer", "en": "Reviewer", "zh": "审查器", "x": 700, "y": 440, "w": 160, "h": 64, "type": "security"}
  ],
  "edges": [
    {"from": "scheduler", "to": "bus", "label": "任务分解"},
    {"from": "bus", "to": "planner", "label": "路由"},
    {"from": "bus", "to": "executor", "label": "路由"},
    {"from": "bus", "to": "retriever", "label": "路由"},
    {"from": "bus", "to": "reviewer", "label": "路由"}
  ]
}
```

各核心模块的职责与关键组件如表 1 所示。

> **表1：** 核心模块与职责

| 模块 | 职责 | 关键组件 |
| --- | --- | --- |
| 协作调度器 | 任务分解、优先级排序、负载均衡 | 调度算法、任务队列 |
| 消息总线 | 结构化消息路由与持久化 | 发布-订阅通道、事件日志 |
| 规划器 | 生成子任务序列与验收标准 | 提示模板、约束解析器 |
| 执行器 | 调用外部工具并汇总结果 | 工具注册表、结果规范化 |
| 检索器 | 面向知识库的检索增强 | 向量索引、重排序器 |
| 审查器 | 校验输出质量并触发回退 | 规则引擎、一致性检查 |

> 注：模块职责划分遵循高内聚、低耦合原则，各角色仅通过消息总线交互。

## 四、多智能体协作调度

### 4.1 注意力加权调度

调度器依据各执行器的历史成功率 $p_i$ 与当前负载 $l_i$ 计算任务分配权重。设第 $i$ 个执行器的得分为 $w_i = p_i \cdot (1 - l_i)$，则归一化分配概率为

$$
a_i = \frac{\exp(\beta w_i)}{\sum_{j=1}^{N} \exp(\beta w_j)}
$$

其中 $\beta$ 为温度系数，控制分配的集中程度。$\beta$ 越大，任务越倾向于集中在历史表现最好的执行器上；$\beta \to 0$ 时退化为均匀随机分配。

### 4.2 审查与回退

审查器对执行器输出 $o_i$ 计算置信度 $c_i = \Phi(o_i)$，当 $c_i$ 低于阈值 $\tau$ 时触发回退：将该子任务重新入队并交由备选执行器处理，最多重试 $K$ 次。该机制可形式化为

$$
o_i^{*} = \arg\max_{k \le K} \Phi(o_i^{(k)})
$$

### 4.3 调度策略对比

不同调度策略的特性对比如表 2 所示。

> **表2：** 调度策略对比

| 策略 | 时间复杂度 | 负载均衡 | 级联错误抑制 | 适用场景 |
| --- | --- | --- | --- | --- |
| 轮询调度 | $O(1)$ | 优 | 弱 | 同质执行器 |
| 贪心调度 | $O(N)$ | 中 | 中 | 短期任务 |
| 注意力加权调度 | $O(N)$ | 优 | 强 | 异构执行器 |
| 强化学习调度 | $O(N)$ | 优 | 强 | 长周期任务 |

## 五、数据流与交互

智能体间的消息流转过程如图 2 所示：调度器将子任务封装为标准消息并投递到消息总线；执行器消费消息、调用工具并回写结果；审查器读取结果后决定放行或触发回退；最终由汇聚器合并各子任务产物。

```super-diagram
{
  "type": "sequence",
  "canvas": {"width": 1100, "height": 780, "theme": "light"},
  "title": "图2：智能体间消息流转与回退过程",
  "subtitle": "调度器 → 消息总线 → 执行器/审查器，失败触发回退",
  "participants": [
    {"id": "scheduler", "en": "Scheduler", "zh": "调度器", "kind": "gateway"},
    {"id": "bus", "en": "Bus", "zh": "消息总线", "kind": "backend"},
    {"id": "executor", "en": "Executor", "zh": "执行器", "kind": "backend"},
    {"id": "reviewer", "en": "Reviewer", "zh": "审查器", "kind": "external"},
    {"id": "aggregator", "en": "Aggregator", "zh": "汇聚器", "kind": "backend"}
  ],
  "messages": [
    {"from": "scheduler", "to": "bus", "en": "DispatchTask", "zh": "投递子任务", "time": "0ms"},
    {"from": "bus", "to": "executor", "en": "RouteTask", "zh": "路由到执行器", "time": "5ms"},
    {"from": "executor", "to": "bus", "en": "TaskResult", "zh": "回写执行结果", "time": "120ms"},
    {"from": "bus", "to": "reviewer", "en": "VerifyOutput", "zh": "校验输出质量", "time": "130ms"},
    {"from": "reviewer", "to": "bus", "en": "Reject", "zh": "回退请求", "async": true, "time": "140ms"},
    {"from": "bus", "to": "executor", "en": "RetryTask", "zh": "重试子任务", "async": true, "time": "145ms"},
    {"from": "executor", "to": "aggregator", "en": "SubmitResult", "zh": "提交最终产物", "time": "260ms"},
    {"from": "aggregator", "to": "scheduler", "en": "MergedOutput", "zh": "合并结果汇报", "time": "300ms"}
  ]
}
```

> 注：所有消息均携带全局唯一的 trace id 与父任务 id，便于全链路追踪与问题定位。

## 六、关键实现

执行器智能体的核心逻辑如下：

```python
class ExecutorAgent:
    """执行器智能体：消费子任务消息，调用工具并回写结果。"""

    def __init__(self, name: str, tools: dict[str, callable], scheduler):
        self.name = name
        self.tools = tools          # 工具注册表：名称 -> 可调用对象
        self.scheduler = scheduler  # 协作调度器引用

    async def handle(self, message: dict) -> dict:
        """处理单条子任务消息。"""
        tool_name = message["tool"]
        args = message["args"]
        try:
            result = self.tools[tool_name](**args)
            return {"status": "ok", "agent": self.name, "output": result}
        except Exception as exc:
            # 失败结果交由调度器决定是否回退
            return {"status": "error", "agent": self.name, "error": str(exc)}
```

## 七、实验评估

### 7.1 实验设置

我们在 HotpotQA（多跳问答）与 MATH（数学推理）两个基准上评估所提架构。基线为单智能体 ReAct 范式 [2]，对比方法为 AutoGen [4] 与 MetaGPT [5]。所有方法均使用相同的底层模型与工具集，以保证公平。

### 7.2 主要结果

> **表3：** 各方法在基准上的表现（%）与无效工具调用率（%）

| 方法 | HotpotQA F1 | MATH 准确率 | 无效调用率 |
| --- | --- | --- | --- |
| ReAct（单智能体） | 52.1 | 41.3 | 18.7 |
| AutoGen | 56.8 | 44.2 | 12.4 |
| MetaGPT | 58.0 | 45.6 | 10.9 |
| 本文架构 | 58.5 | 45.4 | 6.2 |

实验表明，本文架构在 HotpotQA 上取得最优 F1，在 MATH 上接近 MetaGPT；无效工具调用率显著低于全部基线，验证了审查回退机制的有效性。

### 7.3 消融实验

移除审查回退后，无效调用率由 6.2% 上升至 15.1%，HotpotQA F1 下降 4.3 个百分点，证实审查链路是架构的关键组成部分。

## 八、结论与展望

本文提出了基于大语言模型的多智能体协作架构，通过解耦角色、消息总线与注意力加权调度，在任务质量与资源利用率之间取得良好平衡。后续工作将探索：(1) 基于强化学习的调度参数自适应； (2) 跨会话的长期记忆共享； (3) 面向大规模任务图的并行调度优化。

## 参考文献

[1] Wei J, Wang X, Schuurmans D, et al. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models[C]// NeurIPS 2022.

[2] Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models[C]// ICLR 2023.

[3] Wang G, Xie Y, Jiang Y, et al. Voyager: An Open-Ended Embodied Agent with Large Language Models[J]. TMLR, 2023.

[4] Wu Q, Bansal G, Zhang J, et al. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation[J]. arXiv:2308.08155, 2023.

[5] Hong S, Zhuge M, Chen J, et al. MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework[C]// ICLR 2024.

[6] Lewis P, Perez E, Piktus A, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks[C]// NeurIPS 2020.
