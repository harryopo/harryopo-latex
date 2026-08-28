# -*- coding: utf-8 -*-
"""
make-word-template.py — 公文/学术 Word 模板示例（基于模板引擎）

演示用法：通过 word_template_engine.WordTemplateEngine 生成完整论文。
切换字体方案只需改 config 参数。
"""

import sys
from pathlib import Path
from word_template_engine import WordTemplateEngine


def main():
    # ====== 初始化引擎（切换方正/开源只需改这一行）======
    config = Path(__file__).parent / 'configs' / 'fangzheng.json'
    engine = WordTemplateEngine(config)

    # ====== 自动目录（第一页）======
    engine.add_toc()

    # ====== 标题 + 摘要 ======
    engine.add_title(
        '基于大语言模型的智能体架构设计与实现',
        subtitle='——面向多轮对话场景的编排流水线与上下文管理',
        author='张三  计算机学院  2025000101'
    )
    engine.add_abstract(
        '随着大语言模型（LLM）能力的飞速提升，如何将 LLM 从被动的"问答机器"升级为主动的"智能体（Agent）"'
        '成为当前研究的热点。本文提出了一种基于六步编排流水线的智能体架构，包含意图分类、策略选择、'
        '难度自适应、多维上下文构建、系统提示组装和流式响应六个阶段。通过引入预算制懒加载的上下文'
        '构建器和教学策略驱动的提示组装机制，该架构在保持回答质量的同时将 Token 消耗降低了 38%。'
        '实验表明，本地决策链路的平均延迟为 52-207ms，适合实时交互场景。',
        keywords_text='大语言模型；智能体架构；编排流水线；上下文管理；教学策略；流式响应'
    )

    # ====== 正文 ======

    # --- 一、引言 ---
    engine.add_heading1('一、引言')
    engine.add_body('大语言模型（Large Language Model, LLM）在自然语言理解与生成方面展现了前所未有的能力。'
                     '然而，直接使用 LLM 进行问答交互存在三个核心局限：第一，模型缺乏对用户意图的主动识别能力；'
                     '第二，上下文窗口有限导致长对话信息丢失；第三，模型给出的回答往往是"百科全书式"的泛泛而谈，'
                     '缺乏针对性和教学性[1]。')
    engine.add_body('智能体（Agent）架构旨在解决上述问题。通过引入编排流水线、上下文管理器和策略引擎，'
                     'Agent 能够根据用户意图动态调整行为，提供更精准、更具个性化的交互体验[2]。'
                     '本文的核心贡献如下：')
    for idx, label in enumerate(['一', '二', '三']):
        text = [
            '提出六步编排流水线架构，将 LLM 交互从单次调用升级为多阶段决策链路',
            '设计预算制懒加载的上下文构建器，Token 消耗降低 38%（中位数）',
            '引入 Bloom 认知层级驱动的难度自适应机制，实现教法与难度的双联动',
        ][idx]
        p = engine.doc.add_paragraph()
        engine._set_spacing(p, before=2, after=2)
        engine._set_indent(p, 2)
        engine._make_run(p, f'（{label}）', engine._get_font('heading3'), size=12)
        engine._make_run(p, text, engine._get_font('body'), size=12)

    # --- 二、相关工作 ---
    engine.add_heading1('二、相关工作')

    engine.add_heading2('2.1 大语言模型应用架构')
    engine.add_body('当前主流的 LLM 应用架构可分为三类：直接调用型（如 ChatGPT）、检索增强生成型（RAG[3]）'
                     '和智能体编排型（Agent Orchestration[4]）。直接调用型最简单但缺乏上下文管理；'
                     'RAG 通过向量检索注入外部知识，但未解决意图识别和策略选择问题；Agent 编排型通过'
                     '多阶段流水线实现端到端的智能交互，是当前最先进的方案。')

    engine.add_heading2('2.2 教学策略驱动的对话系统')
    engine.add_body('教学策略驱动的对话系统借鉴了教育心理学中的 Bloom 认知层级理论[5]。Bloom 将认知能力'
                     '分为记忆、理解、应用、分析、评价和创造六个层级。苏格拉底追问法和费曼复述法是两种'
                     '经典的主动学习策略[6]。')

    # --- 三、系统架构设计 ---
    engine.add_heading1('三、系统架构设计')

    engine.add_heading2('3.1 总体架构')
    engine.add_body('本系统采用三进程架构（主进程、渲染进程、Preload 桥接），Agent 编排引擎运行在主进程中。'
                     '整体架构如图 1 所示，包含六个核心模块：意图分类器、策略选择器、状态追踪器、上下文管理器、'
                     '提示组装器和流式响应处理器。')
    engine.add_figure_placeholder(
        '图1：智能体编排系统总体架构图',
        note='注：三进程架构中，主进程负责 Agent 编排与本地数据库操作；渲染进程负责 UI 渲染与用户交互；'
             'Preload 桥接层通过 contextIsolation 机制实现安全的 IPC 通信。'
    )

    engine.add_heading2('3.2 六步编排流水线')
    engine.add_body('六步编排流水线是本系统的核心，其流程如图 2 所示。每一步的设计目标与延迟分布见表 1。')
    engine.add_figure_placeholder('图2：六步编排流水线流程图')
    engine.add_table(
        ['步骤', '模块名称', '功能描述', '平均延迟'],
        [
            ['①', '意图分类器', '本地关键词打分，识别4类用户意图', '1-5ms'],
            ['②', '策略选择器', '意图到教学模式的映射决策', '<1ms'],
            ['③', '状态追踪器', 'Bloom层级自适应升降级', '<1ms'],
            ['④', '上下文管理器', '5维上下文预算制懒加载', '50-200ms'],
            ['⑤', '提示组装器', '四段动态系统提示拼装', '<1ms'],
            ['⑥', '流式响应器', 'AI SDK流式输出+reasoning归一化', '500-2000ms'],
        ],
        caption_text='表1：六步编排流水线步骤详情与性能画像',
        note='注：步骤①-⑤全部在本地执行，合计延迟 52-207ms。步骤⑥为唯一涉及网络请求的环节。'
    )

    engine.add_heading2('3.3 多维上下文构建器')
    engine.add_body('上下文构建器负责在每次 AI 调用前组装结构化上下文。为控制 Token 消耗，本设计采用'
                     '预算制懒加载策略：每个维度分配独立的 Token 预算，按优先级依次加载，预算耗尽时'
                     '低优先级维度自动跳过。各维度的配置参数见表 2。')
    engine.add_table(
        ['优先级', '构建器名称', '数据源', 'Token预算'],
        [
            ['90', 'BookContextBuilder', '向量语义搜索 + 关键词回退', '1500'],
            ['80', 'MethodologyContextBuilder', '方法论相关性评分 Top 5', '1000'],
            ['70', 'KnowledgeCardContextBuilder', '知识卡相关性评分 Top 10', '800'],
            ['50', 'MemoryContextBuilder', '长期记忆 Top 3 + 摘要', '500'],
            ['40', 'UserProfileContextBuilder', '动态生成用户画像', '200'],
        ],
        caption_text='表2：五维上下文构建器配置（总预算 4000 Token）'
    )
    engine.add_body('该设计包含三条硬规则：（一）预算不足时低优先级构建器自动跳过；（二）每个构建器独立'
                     '失败不拖垮整体（fail-soft 柔性容错）；（三）超预算截断并显式标记截断位置。')

    # --- 数学公式示例 ---
    engine.add_body('渐进式通道压缩策略的核心公式如下，设第 i 个阶段的输出通道数为：')
    eq1 = engine.build_omath(
        engine.math_sub('C', 'i'),
        engine.math_run('=C'),
        engine.math_sub('', '0'),
        engine.math_run('·α'),
        engine.math_sup('', 'i'),
    )
    engine.add_equation(eq1, caption_text='式(1)：渐进式通道压缩公式')
    engine.add_body('其中 C₀ 为基础通道数，α ∈ (0, 1] 为压缩因子，N 为阶段总数。本文取 C₀ = 64，α = 0.75。')

    engine.add_body('注意力模块中使用的 Sigmoid 激活函数定义为：')
    eq2 = engine.build_omath(
        engine.math_run('σ(x)='),
        engine.math_frac('1', '1+e⁻ˣ'),
    )
    engine.add_equation(eq2, caption_text='式(2)：Sigmoid 激活函数')

    engine.add_body('通道注意力通过对各通道特征进行加权求和实现，其计算公式为：')
    eq3 = engine.build_omath(
        engine.math_sub('A', 'c'),
        engine.math_run('='),
        engine.math_frac('Σwᵢgᵢ', 'Σwᵢgᵢ'),
    )
    engine.add_equation(eq3, caption_text='式(3)：通道注意力计算公式')
    engine.add_body('其中 σ 为 Sigmoid 函数，wᵢ 为第 i 个通道的权重，gᵢ 为第 i 个通道的全局池化值。')

    engine.add_heading2('3.4 难度自适应机制')
    engine.add_body('难度自适应基于会话状态机实现，核心规则如下：连续答对 3 次触发 Bloom 层级升级；'
                     '连续答错 2 次触发降级。当 Bloom 层级达到 4 级以上时自动切换苏格拉底追问模式，'
                     '2 级以下则切换为直接回答模式。策略与意图的映射关系见表 3。')
    engine.add_table(
        ['意图类型', '教学模式', '初始Bloom层级'],
        [
            ['知识查询', '直接回答（direct_answer）', '1（记忆）'],
            ['深度讨论', '苏格拉底追问（socratic）', '3（应用）'],
            ['教学实践', '费曼复述（feynman）', '2（理解）'],
            ['闲聊问候', '直接回答（direct_answer）', '1（记忆）'],
        ],
        caption_text='表3：意图到教学策略的映射矩阵'
    )

    # --- 四、实验结果 ---
    engine.add_heading1('四、实验结果')

    engine.add_heading2('4.1 实验设置')
    engine.add_body('实验环境：Windows 11，Intel i7-12700H，32GB RAM。AI 服务商为 DeepSeek R1 与 '
                     'OpenAI GPT-4o。测试数据集为 50 组中等复杂度的多轮对话，每组对话平均 8-12 轮。')

    engine.add_heading2('4.2 Token 消耗对比')
    engine.add_body('将本系统的预算制懒加载方案与全量加载方案进行对比，结果见表 4。在 50 次对话中，'
                     '本方案平均节省 Token 38%（中位数），最高节省 55%。')
    engine.add_table(
        ['指标', '全量加载', '预算制懒加载', '节省比例'],
        [
            ['平均 Token/次', '4,200', '2,600', '38%'],
            ['中位 Token/次', '3,800', '2,356', '38%'],
            ['最大 Token/次', '6,500', '2,925', '55%'],
            ['最小 Token/次', '2,100', '1,400', '33%'],
        ],
        caption_text='表4：Token 消耗对比（50 次中等复杂度对话）'
    )

    engine.add_heading2('4.3 损失函数设计')
    engine.add_body('模型训练采用均方误差（MSE）损失函数，其定义如下：')
    eq4 = engine.build_omath(
        engine.math_run('L='),
        engine.math_frac('1', 'N'),
        engine.math_run(' Σ '),
        engine.math_frac('1', '2'),
        engine.math_run('(y'),
        engine.math_sub('', 'i'),
        engine.math_run('-ŷ'),
        engine.math_sub('', 'i'),
        engine.math_run(')'),
        engine.math_sup('', '2'),
    )
    engine.add_equation(eq4, caption_text='式(4)：均方误差损失函数')
    engine.add_body('其中 N 为样本总数，yᵢ 为真实标签，ŷᵢ 为模型预测值。')

    engine.add_heading2('4.4 延迟分析')
    engine.add_body('本地决策链路（步骤①-⑤）的平均延迟为 52-207ms，其中上下文构建占主要部分（50-200ms）。'
                     '唯一涉及网络请求的流式首 Token 延迟为 500-2000ms，取决于 AI 服务商的响应速度。'
                     '延迟分布见图 3。')
    engine.add_figure_placeholder('图3：各步骤延迟分布箱线图')

    # --- 五、结论与展望 ---
    engine.add_heading1('五、结论与展望')
    engine.add_body('本文提出了一种基于六步编排流水线的智能体架构，通过预算制懒加载的上下文构建器和 '
                     'Bloom 认知层级驱动的难度自适应机制，在保持回答质量的同时显著降低了 Token 消耗。'
                     '实验结果表明，本地决策链路的平均延迟控制在 207ms 以内，适合实时交互场景。')
    engine.add_body('未来的工作将聚焦三个方向：（一）扩展上下文构建器维度，引入时间感知和情感分析；'
                     '（二）探索基于强化学习的策略自动优化机制；（三）将架构推广到多模态交互场景（语音、图像）。')

    # --- 参考文献 ---
    engine.add_heading1('参考文献')
    engine.add_references([
        'Brown T, Mann B, Ryder N, et al. Language models are few-shot learners[C]. NeurIPS, 2020.',
        'Yao S, Zhao J, Yu D, et al. ReAct: Synergizing reasoning and acting in language models[C]. ICLR, 2023.',
        'Lewis P, Perez E, Piktus A, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks[C]. NeurIPS, 2020.',
        'Wang L, Ma C, Feng X, et al. A survey on large language model based autonomous agents[J]. arXiv:2308.11432, 2023.',
        'Bloom B S. Taxonomy of educational objectives[M]. New York: David McKay, 1956.',
        'Paul R, Elder L. Critical thinking: The Socratic method[J]. Journal of Developmental Education, 1997, 20(3): 36-37.',
    ])

    # ====== 保存 ======
    output = Path(__file__).parent / 'harryopo-公文模板.docx'
    engine.save(str(output))


if __name__ == '__main__':
    main()
