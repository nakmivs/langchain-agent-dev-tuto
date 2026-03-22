# 提示词工程学习笔记

> 来源：`src/dps/deep_research/prompts.py` — 深度研究 Agent 的提示词模板

---

## 1. 闭环验证：Plan → Execute → Verify

### 核心思想

把工作流设计成一个闭环：先把原始需求存下来，执行完毕后回头对照需求进行验证。这样可以有效防止 Agent 在多步骤执行过程中偏离主题。

### 原文示例

```
1. Plan: Create a todo list with write_todos to break down the research into focused tasks
2. Save the request: Use write_file() to save the user's research question to /research_request.md
3. Research: Delegate research tasks to sub-agents using the task() tool
4. Synthesize: Review all sub-agent findings and consolidate citations
5. Write Report: Write a comprehensive final report to /final_report.md
6. Verify: Read /research_request.md and confirm you've addressed all aspects
```

### 适用场景

- 任何多步骤任务的 Agent 系统
- 需要确保输出完整性的场景（报告生成、代码重构、需求分析等）
- 可以泛化为：任务开始时创建 checkpoint，结束时回溯验证

---

## 2. 场景化输出模板

### 核心思想

不给一个笼统的输出格式要求，而是按任务类型提供不同的结构模板。Agent 在生成输出时可根据任务类型自动选择最合适的结构，大幅提升输出质量和一致性。

### 原文示例

```
For comparisons:         引言 → A 概述 → B 概述 → 详细对比 → 结论
For lists/rankings:      直接列出条目及详情（无需引言）
For summaries/overviews: 主题概述 → 核心概念 1/2/3 → 结论
```

### 适用场景

- 报告生成系统（根据查询意图选择模板）
- 客服/FAQ Agent（不同问题类型使用不同回答结构）
- 任何输出格式需要因任务而异的场景

---

## 3. 角色心智模型

### 核心思想

不仅告诉 Agent "做什么"，还告诉它"像谁一样思考"。通过赋予 Agent 一个具体的角色认知，引导其行为模式和决策方式。关键是加入约束（如"时间有限"），防止 Agent 进入无限完美主义循环。

### 原文示例

```
Think like a human researcher with limited time. Follow these steps:
1. Read the question carefully
2. Start with broader searches
3. After each search, pause and assess
4. Execute narrower searches as you gather information
5. Stop when you can answer confidently - Don't keep searching for perfection
```

### 适用场景

- 研究型 Agent：模拟研究员的信息检索策略（宽 → 窄）
- 编码 Agent：模拟资深工程师的 debug 思路
- 任何需要引导 Agent 遵循特定思维路径的场景

---

## 4. 硬性约束防循环

### 核心思想

Agent 系统最常见的问题之一是无限循环（不断调用工具但不输出结果）。通过设定**数量上限**（最多 N 次调用）和**语义停止条件**（搜索结果趋同）双重约束来防止这一问题。

### 原文示例

```
Tool Call Budgets (Prevent excessive searching):
- Simple queries: Use 2-3 search tool calls maximum
- Complex queries: Use up to 5 search tool calls maximum
- Always stop: After 5 search tool calls if you cannot find the right sources

Stop Immediately When:
- You can answer the user's question comprehensively
- You have 3+ relevant examples/sources for the question
- Your last 2 searches returned similar information
```

### 适用场景

- 任何使用工具调用的 Agent（搜索、API 调用、代码执行等）
- 成本敏感的生产环境（防止 Token 消耗失控）
- 设计要点：按查询复杂度分级设定预算，而非一刀切

---

## 5. 强制反思机制（ReAct 模式）

### 核心思想

每次工具调用后，强制 Agent 使用 `think_tool` 进行反思，形成 "行动 → 反思 → 决策" 的循环。这是 ReAct（Reasoning + Acting）模式的典型应用。反思问题的设计覆盖四个维度：已知、未知、充分性、下一步。

### 原文示例

```
After each search tool call, use think_tool to analyze the results:
- What key information did I find?        ← 已知
- What's missing?                          ← 未知
- Do I have enough to answer the question? ← 充分性判断
- Should I search more or provide my answer? ← 下一步决策
```

### 适用场景

- 多轮工具调用的 Agent（搜索 Agent、数据分析 Agent）
- 需要避免盲目执行的场景
- 实现方式：提供一个专用的 `think_tool`，或在提示词中要求 Agent 在每次调用后输出结构化的反思内容

---

## 6. 成本导向的子 Agent 调度

### 核心思想

多 Agent 系统中，更多 Agent 不一定更好。默认使用单个子 Agent 进行综合研究，仅在任务**显式要求比较**或**维度天然分离**时才并行。这是对 Token 成本和系统复杂度的平衡。

### 原文示例

```
DEFAULT: Start with 1 sub-agent for most queries

Key Principles:
- Bias towards single sub-agent: One comprehensive research task is more 
  token-efficient than multiple narrow ones
- Avoid premature decomposition: Don't break "research X" into "research X 
  overview", "research X techniques", "research X applications"
- Parallelize only for clear comparisons: Use multiple sub-agents when comparing 
  distinct entities or geographically separated data
```

### 适用场景

- 多 Agent 编排系统（研究、分析、代码生成等）
- 需要控制 API 调用成本的生产环境
- 设计要点：提供明确的示例说明何时该并行、何时不该并行

---

## 7. 结构化标签组织指令

### 核心思想

使用 XML 风格的标签（如 `<Task>`、`<Instructions>`、`<Hard Limits>`）来分隔提示词中的不同指令区域。相比纯 Markdown 层级，这种方式能让 LLM 更清晰地识别指令边界，减少不同区域指令之间的混淆。

### 原文示例

```
<Task>
Your job is to use tools to gather information...
</Task>

<Instructions>
Think like a human researcher with limited time...
</Instructions>

<Hard Limits>
Tool Call Budgets (Prevent excessive searching):...
</Hard Limits>

<Show Your Thinking>
After each search tool call, use think_tool to analyze...
</Show Your Thinking>

<Final Response Format>
When providing your findings back to the orchestrator:...
</Final Response Format>
```

### 适用场景

- 长提示词中包含多种不同类型指令（角色、工具、约束、输出格式等）
- 需要在同一提示词中区分"必须遵守"和"建议遵循"的内容
- Anthropic 和 OpenAI 均推荐此方式来组织复杂提示词

---

## 总结速查表

| 设计模式 | 一句话概括 | 关键词 |
|---|---|---|
| 闭环验证 | 先存需求，最后回头验证 | checkpoint, verify |
| 场景化模板 | 不同任务类型用不同输出结构 | conditional template |
| 角色心智模型 | 告诉 Agent "像谁一样思考" | persona, mental model |
| 硬性约束防循环 | 数量上限 + 语义停止条件 | budget, stop condition |
| 强制反思 | 每步 action 后必须 think | ReAct, reflection |
| 成本导向调度 | 默认单 Agent，显式比较才并行 | cost-aware, parallelism |
| 结构化标签 | XML 标签分隔指令区域 | XML tags, separation |
