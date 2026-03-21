# Agent 编排模式总结

## 先给一个总判断

如果说 `001` 主要在回答：

**Agent 开发的本质是什么？**

那么这一版更偏向回答：

**Agent 系统到底是怎么编排起来的？**

一个很有用的理解方式是：

**Agent 编排，本质上是在组织“决策、执行、反馈、切换”这四件事。**

也就是说，一个 agent 系统并不只是“模型会不会调工具”，而是要回答这些问题：

- 现在该不该调用工具
- 该调用哪个工具
- 调完之后怎么根据结果继续推进
- 什么时候换一个子 agent
- 什么时候并行
- 什么时候重试
- 什么时候结束
- 什么时候交给人

所以所谓“编排模式”，本质上就是：

**如何组织这些控制流。**

## 可以把 agent 编排分成 3 层

这个分层很重要，因为很多讨论会把不同层的东西混在一起。

### 1. 单 agent 控制流层

这一层关注的是：

**一个 agent 自己怎么思考、调工具、看结果、再继续。**

比如：

- tool calling
- ReAct
- planner-executor
- reflection / critic loop

### 2. 多 agent 协作层

这一层关注的是：

**多个 agent 之间怎么分工、切换、委派。**

比如：

- router
- subagents
- handoffs
- orchestrator-workers
- hierarchical multi-agent

### 3. 运行时与协议层

这一层关注的是：

**agent 如何接入外部世界，以及如何跨系统协作。**

比如：

- MCP
- A2A
- durable execution
- checkpoint / resume
- streaming
- human-in-the-loop

如果不区分这三层，很容易把：

- “tool calling”
- “ReAct”
- “MCP”
- “多 agent”

都当成同一级概念。

其实它们不是。

## 一个更稳的总分类

我目前会把常见 agent 编排模式归成 5 类：

1. `固定流程型`
2. `工具循环型`
3. `规划执行型`
4. `多 agent 协作型`
5. `运行时增强型`

下面分别展开。

## 1. 固定流程型

核心特征是：

**流程路径大致已知，系统主要是在预定义结构里推进。**

这类模式更像 workflow，而不是强自主 agent。

### 1.1 Prompt Chaining

就是把任务拆成固定顺序的多步：

- 第一步产出第二步输入
- 第二步产出第三步输入
- 中间可以加校验

适合：

- 提纲 -> 初稿 -> 润色
- 抽取 -> 校验 -> 格式化
- 翻译 -> 审校 -> 本地化改写

优点：

- 简单
- 稳定
- 好调试

问题：

- 缺少弹性
- 不适合开放任务

### 1.2 Routing

Routing 是先判断任务类型，再把请求送进不同分支。

比如：

- 售后问题走退款流
- 技术问题走故障排查流
- 简单问题走便宜模型
- 复杂问题走强模型

适合：

- 分类明确
- 分支职责清晰
- 每条分支都能专门优化

### 1.3 Parallelization

并行主要有两种：

- `sectioning`：把不同子任务并行做
- `voting`：同一任务跑多次，最后投票或聚合

适合：

- 多源检索
- 多维评估
- 多专家并行审查
- 多候选答案打分

并行的价值主要有两个：

- 提升速度
- 提升置信度

### 1.4 Loop / Iterative Refinement

这是固定流程中的“循环版”。

流程大致已知，但允许多轮迭代，直到满足停止条件。

适合：

- 搜索补全
- 文本打磨
- 答案逐轮完善

关键点是一定要有：

- 最大迭代次数
- 明确退出条件

否则系统会空转。

## 2. 工具循环型

核心特征是：

**模型在循环里决定是否调用工具，并根据观察结果继续。**

这是现代 agent 最基础的一类形态。

### 2.1 Tool Calling / Function Calling

这是现在几乎所有 agent 框架的最小单位。

本质不是“模型会魔法”，而是：

- 你给模型一组带 schema 的工具
- 模型判断是否要调用
- 调用后拿到结构化结果
- 再继续生成或继续决策

它解决的是：

**模型如何从“只能生成文本”变成“可以采取动作”。**

适合：

- 查天气
- 查数据库
- 发 HTTP 请求
- 发邮件
- 执行代码

### 2.2 ReAct

ReAct 的经典形式是：

`Reason -> Act -> Observe -> Reason`

它强调两件事：

- 先形成下一步动作意图
- 再通过环境反馈纠正后续决策

ReAct 非常重要，因为它定义了 agent 的基本循环感。

但在现代工程里，它通常不会原样出现，而会变成：

- 工具调用循环
- 结构化工具调用
- 带约束的 agent loop

所以更准确地说：

**ReAct 是现代 tool-using agent 的思想原型。**

### 2.3 Action-Observation Loop

这可以看成更工程化的 ReAct。

核心不是暴露多少“思维链”，而是：

- 做动作
- 拿观察结果
- 更新状态
- 再决定下一步

对于真实系统，更关键的是 observation 的质量，而不是 thought 写得多漂亮。

## 3. 规划执行型

核心特征是：

**任务不再是一轮一轮临时想，而是先做某种规划，再执行。**

这类模式在复杂任务里非常重要。

### 3.1 Planner-Executor

这是最常见的一种。

基本结构：

- planner 先拆任务
- executor 按计划执行
- 必要时再更新计划

适合：

- 长任务
- 复杂 research
- 编码任务
- 多文件修改

它相比纯 ReAct 的优势是：

- 不容易一直在局部打转
- 更容易形成全局视图
- 更利于审计和人工接管

### 3.2 Orchestrator-Workers

它和 planner-executor 很像，但更强调：

- orchestrator 动态拆子任务
- workers 并行或分批执行
- 最后汇总

和普通 parallelization 的区别在于：

**子任务不是预先写死的，而是运行时动态生成的。**

适合：

- 深度研究
- 多文档分析
- 复杂代码库任务

### 3.3 Evaluator-Optimizer

这个模式是：

- 一个模型先生成
- 另一个模型评估
- 给反馈
- 再改

它的关键不在“两个模型”，而在：

**是否存在清晰可操作的评估标准。**

适合：

- 写作润色
- SQL 生成
- 代码生成
- 翻译优化

### 3.4 Reflection / Critic Loop

它和 evaluator-optimizer 接近，但通常更强调：

- 自我反思
- 自我纠错
- 局部修复

它适合加在复杂 agent 的后处理阶段，而不一定要单独做成完整系统。

## 4. 多 agent 协作型

核心特征是：

**一个系统里不止一个 agent，职责被分散给多个角色。**

但这类模式要谨慎用。

很多时候，一个 agent 加上好的工具和上下文选择，就够了。

### 4.1 Agents as Tools / Subagents

这是目前很实用的一种多 agent 方式。

做法是：

- 主 agent 保持总控
- 其他 agent 被包装成工具
- 主 agent 按需调用它们

优点：

- 总控清晰
- 最终输出可以统一
- 便于挂统一 guardrails

适合：

- 需要一个主 agent 对最终结果负责
- 需要多个专家能力，但不想让会话控制权到处切

### 4.2 Handoffs

handoff 的特点不是“调用别人帮一下忙”，而是：

**把当前会话的主导权切给另一个 agent。**

适合：

- 客服转专员
- 从通用助理切到订票 agent
- 从问答切到执行型 agent

它和 agents as tools 的关键区别是：

- `agents as tools`：主 agent 不放权
- `handoffs`：控制权转移

### 4.3 Router + Specialists

这是多 agent 里的经典结构：

- 先由 router 判断任务类型
- 再交给某个 specialist

它更偏静态分工，适合：

- 专家边界清晰
- 请求类型相对稳定

### 4.4 Hierarchical Multi-Agent

这是分层多 agent：

- 上层 agent 负责目标和拆解
- 下层 agent 负责具体执行
- 下层内部还可以继续拆

适合：

- 特别复杂的大任务
- 需要明显的上下文隔离

但复杂度很高，调试和评估成本也很高。

### 4.5 Skills

skills 有点特殊。

它不一定意味着多个 agent，而更像：

**按需加载某个专业能力包。**

一个 skill 里可能包含：

- 专门提示词
- 领域知识
- 工具集
- 触发条件

它解决的是：

**不要把所有知识和规则都塞进主 agent 的上下文里。**

## 5. 运行时增强型

这类不一定单独构成“模式”，但它们正在成为现代 agent 系统的关键基础设施。

### 5.1 Human-in-the-loop

当任务涉及高风险动作时，系统要能在关键节点暂停并请求人工确认。

比如：

- 发真实邮件
- 付款
- 删除数据
- 发布生产环境

这不是附属能力，而是生产系统的核心边界控制。

### 5.2 Durable Execution

长任务 agent 如果不能中断恢复，就很难上生产。

所以现在越来越强调：

- checkpoint
- resume
- thread state
- time travel

这意味着 agent 不再只是“一次调用”，而是一个可以恢复的运行实体。

### 5.3 MCP

MCP 不是单独的 agent 编排模式，而是：

**agent 接入工具、资源、提示模板的标准协议。**

它把 server primitives 分成：

- `tools`
- `resources`
- `prompts`

其中：

- tools 是模型可调用动作
- resources 是应用注入的上下文
- prompts 是用户可触发模板

MCP 的意义在于：

**把“如何接工具”这件事协议化。**

### 5.4 A2A

A2A 也不是单独的推理模式，而是：

**agent 和 agent 之间如何发现、通信、协作的协议。**

它解决的是跨系统多 agent 协作的问题，比如：

- 如何发现对方能力
- 如何发送任务
- 如何流式拿结果
- 如何处理中断和长任务

所以可以把它理解成：

- MCP：agent 连工具
- A2A：agent 连 agent

## 当前最值得记住的几组边界

### 1. Workflow vs Agent

- `workflow`：路径大致已知
- `agent`：路径由模型在运行中决定

不要把所有东西都叫 agent。

### 2. Tool Calling vs ReAct

- `tool calling`：能力接口
- `ReAct`：控制循环思想

tool calling 是机制，ReAct 是行为模式。

### 3. Planner-Executor vs ReAct

- `ReAct` 更局部、逐步
- `planner-executor` 更全局、先规划

### 4. Agents as Tools vs Handoffs

- `agents as tools`：总控不变
- `handoffs`：控制权转移

### 5. MCP vs A2A

- `MCP`：连接工具与资源
- `A2A`：连接 agent 与 agent

## 2025-2026 的一个明显趋势

最近一年的官方资料里，有几个趋势特别明显。

### 1. 从“大一统超级 agent”转向“简单模式组合”

Anthropic、LangGraph、OpenAI 的资料都在强调：

**不要一开始就堆复杂系统，而要从简单模式开始。**

也就是：

- 先单轮
- 再工具调用
- 再 workflow
- 再需要时上 planner 或多 agent

### 2. 图式编排越来越重要

LangGraph、ADK 这类框架越来越强调：

- graph
- state machine
- explicit edges
- resume / checkpoint

原因是：

**一旦任务变长，显式控制流比隐式 prompt loop 更可控。**

### 3. 多 agent 不再只是“多角色 prompt”

现在更强调这些工程问题：

- 上下文隔离
- 状态同步
- 控制权边界
- 通信协议
- 可观测性

也就是说，多 agent 正从 prompt 技巧变成系统设计问题。

### 4. 协议层正在独立出来

现在开始出现很明确的协议分工：

- MCP
- A2A
- 各类 UI / event stream 协议

这说明 agent 编排正在从“应用内部技巧”走向“生态互操作”。

### 5. 深度 agent 形态开始成熟

像 Deep Agents 这类形态，已经不只是：

- 一个模型 + 一组工具

而是开始内建：

- planning
- todo tracking
- subagents
- file system
- long-term memory

这类系统更像“agent harness”。

## 一个实用的选型方式

如果以后要做系统设计，我会先按下面这个顺序判断。

### 1. 任务路径是否基本已知

如果是：

- 先用 workflow
- 不要急着上自主 agent

### 2. 是否需要外部信息或动作

如果需要：

- 上 tool calling

### 3. 是否需要动态拆解长任务

如果需要：

- 上 planner-executor
- 或 orchestrator-workers

### 4. 是否存在明显专家边界

如果有：

- 考虑 subagents
- 或 router
- 或 handoffs

### 5. 是否涉及高风险动作

如果有：

- 一定加入 human-in-the-loop

### 6. 是否需要跨系统互联

如果需要：

- 工具侧优先考虑 MCP
- agent 间协作考虑 A2A

## 一个建议的学习顺序

我会推荐按下面的顺序学：

1. `tool calling`
2. `ReAct`
3. `prompt chaining`
4. `routing`
5. `parallelization`
6. `planner-executor`
7. `evaluator-optimizer`
8. `agents as tools`
9. `handoffs`
10. `graph / workflow runtime`
11. `MCP`
12. `A2A`

这个顺序的好处是：

- 从简单到复杂
- 从单 agent 到多 agent
- 从应用内控制流到跨系统协议

## 当前这版的收束结论

可以先把 agent 编排理解成下面这句话：

**Agent 编排不是“让模型自己想办法”，而是为模型、工具、状态、子系统之间的协作设计控制流。**

进一步说：

- workflow 解决确定性流程
- tool loop 解决行动能力
- planner 解决复杂任务拆解
- multi-agent 解决职责分工与上下文隔离
- runtime / protocol 解决可恢复执行与跨系统协作

如果后面继续写下一版，我觉得可以继续展开这几个方向：

1. `ReAct` 和 `planner-executor` 的边界
2. `handoff` 和 `subagent` 的工程差异
3. `LangGraph` 里这些模式分别怎么落地
4. `MCP`、`A2A` 和传统工具封装的关系
