"""
============================================================
练习 3（进阶）：实现显式 ReAct 状态循环
============================================================

【题目描述】
使用 LangGraph 实现一个显式的 ReAct / Action-Observation Loop Agent。

场景：通用助手，需要具备以下 2 个工具：
  1. search_docs — 查询知识库中的资料（返回模拟结果即可）
  2. calculate — 执行简单计算（返回模拟结果或真实计算结果均可）

与练习 2 的区别是：这次不只要求“能调工具”，而是要把推理、行动、观察、结束这些阶段明确建模为状态推进过程。

【要求】
1. 使用 StateGraph 定义显式状态，状态中至少包含：
   - messages：消息历史
   - observations：每一步工具调用后的观察结果
   - step_count：当前循环次数
   - max_steps：最大允许循环次数
   - error：最近一次错误信息（没有则为 None）
   - finished：是否结束
2. 至少设计以下职责明确的节点（名称可自行决定）：
   - reason：让模型判断当前是否需要调用工具，以及下一步要做什么
   - act：执行模型给出的工具调用
   - observe：把工具结果写回状态，并准备进入下一轮推理
   - finalize：在无需继续调用工具、达到最大步数、或出现无法恢复的问题时生成最终回答
3. 支持一次用户请求中进行多轮工具调用，而不是只调用一次工具就结束
4. 每次工具调用后，都要把 observation 追加到状态中，便于后续调试和审计
5. 增加明确的循环边界：
   - 达到 max_steps 后必须停止
   - 模型没有返回 tool_calls 时进入 finalize
   - 工具执行失败时，将错误写入 state，并决定是继续、重试一次，还是直接结束
6. 至少准备 4 个测试输入，覆盖以下情况：
   - 不需要工具的问题
   - 只需要一次工具调用的问题
   - 需要连续两次及以上工具调用的问题
   - 工具执行失败的问题
7. 不要求暴露思维链内容，但要让代码结构能体现 ReAct 的核心循环：
   - Reason -> Act -> Observation -> Reason

【思考提示】
- 为什么练习 2 的“llm_call -> tool_node -> llm_call”还不算显式 ReAct？
- 哪些信息应该持久保存在 state 中，哪些只需要进入当前 prompt？
- observation 是只保存给模型看的文本，还是保存结构化结果？
- 达到最大步数时，finalize 节点应该如何向用户解释“为什么提前停止”？
- 如果工具报错，应该把错误直接交给模型，还是先做结构化处理再交给模型？

【学习目的】
- 理解 tool calling 是能力接口，ReAct 是控制流模式
- 学会把“推理、行动、观察、结束”拆成显式节点，而不是隐含在单个调用里
- 练习设计可审计、可停止、可恢复扩展的 agent 状态
- 理解循环边界、错误处理、终止条件在 agent 工程中的重要性
- 为后续学习 routing、planner-executor、multi-agent 打基础
============================================================
"""
import operator
from typing_extensions import TypedDict, Annotated
from langchain.messages import SystemMessage, ToolMessage, AnyMessage
from langchain.tools import tool


from llm import get_llm

class State(TypedDict):
   messages: Annotated[list[AnyMessage], operator.add]
   step_count: Annotated[int]
   max_steps: Annotated[int] = 3
   