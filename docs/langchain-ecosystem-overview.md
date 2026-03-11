# LangChain 生态系统：框架、运行时与工具套件

> 来源：[Frameworks, runtimes, and harnesses](https://docs.langchain.com/oss/python/concepts/products)

LangChain 维护了三类开源工具，帮助开发者构建 AI Agent 应用。它们分别面向不同的开发需求和复杂度层级。

---

## 一、三大类别概述

| | 框架（Framework） | 运行时（Runtime） | 工具套件（Harness） |
|---|---|---|---|
| **代表** | LangChain | LangGraph | Deep Agents SDK |
| **抽象层级** | 高层抽象 | 底层控制 | 最高层，开箱即用 |
| **核心价值** | 抽象 + 集成 | 持久执行 + 流式 + 人机协作 + 持久化 | 预置工具 + 提示词 + 子 Agent |
| **同类产品** | Vercel AI SDK、CrewAI、OpenAI Agents SDK、Google ADK、LlamaIndex | Temporal、Inngest | Claude Agent SDK、Manus |

---

## 二、各自核心能力

### 2.1 LangChain —— 快速上手的标准化框架

- 提供模型、工具、Agent 循环的**标准抽象**
- 丰富的第三方集成（各种 LLM、向量数据库、外部服务等）
- 中间件机制，灵活扩展
- 基于 LangGraph 构建，但使用 LangChain 不需要了解 LangGraph

### 2.2 LangGraph —— 精细控制的底层引擎

| 能力 | 说明 |
|------|------|
| **持久执行** | Agent 可在故障后恢复，支持长时间运行，从断点续传 |
| **流式传输** | 支持工作流和响应的实时流式处理 |
| **人机协作（HITL）** | 可在运行中检查、修改 Agent 状态，融入人工审核 |
| **状态持久化** | 线程级和跨线程的状态管理 |
| **底层编排** | 直接控制 Agent 的执行流程，无高层抽象包裹 |

### 2.3 Deep Agents SDK —— 自带电池的高级套件

| 能力 | 说明 |
|------|------|
| **规划能力** | 内置 to-do 列表，自动分解和跟踪多个任务 |
| **子 Agent 委派** | 拆分任务给子 Agent，保持上下文清晰 |
| **文件系统操作** | 内置文件读写，支持可插拔存储后端 |
| **Token 管理** | 自动摘要对话历史，清理大型工具输出，控制上下文长度 |

---

## 三、使用场景对比（重点）

### 选 LangChain 的场景

- **快速原型开发**：想尽快跑通一个 Agent demo
- **团队标准化**：统一团队的 LLM 开发方式和编码规范
- **简单 Agent 应用**：不需要复杂编排的场景，如问答机器人、简单 RAG 应用
- **多模型/多工具集成**：需要对接多种 LLM 或外部服务

### 选 LangGraph 的场景

- **需要精细控制执行流**：确定性步骤和 Agent 步骤混合的工作流
- **长时间运行的有状态任务**：跨会话保持状态的客服系统、持续监控系统
- **持久执行需求**：任务可能中断，需要从断点恢复
- **复杂工作流编排**：多分支、条件判断、循环等复杂逻辑
- **生产环境部署**：需要稳健的基础设施支撑

### 选 Deep Agents SDK 的场景

- **高度自主的 Agent**：需要 Agent 自行规划、分解、执行复杂任务
- **复杂多步骤任务**：代码生成、研究分析、数据处理等需要多步推理的场景
- **长周期运行的 Agent**：任务持续时间长，需要自动管理上下文和 Token
- **需要子 Agent 协作**：任务需要拆分给多个专业子 Agent 分别处理

---

## 四、功能对比表

| 功能 | LangChain | LangGraph | Deep Agents SDK |
|------|-----------|-----------|-----------------|
| 短期记忆 | 内置短期记忆 | 短期记忆 | StateBackend（临时） |
| 长期记忆 | 内置长期记忆 | 长期记忆 | 长期记忆 |
| 技能（Skills） | 多 Agent 技能 | — | Skills |
| 子 Agent | 多 Agent 子代理 | Subgraphs | Subagents |
| 人机协作 | 人机协作中间件 | Interrupts | interrupt_on 参数 |
| 流式传输 | Agent Streaming | Streaming | Streaming |

---

## 五、三者关系

三者不是互斥的，而是**层层递进**的关系：

```
LangGraph（底层运行时）
    └── LangChain（中层框架，基于 LangGraph 构建）
    └── Deep Agents SDK（高层套件，基于 LangGraph 构建）
```

- **LangChain** 是 LangGraph 之上的高层抽象，隐藏了底层复杂性
- **Deep Agents SDK** 同样基于 LangGraph，但加入了规划、文件系统、子 Agent 等高级能力
- 可以根据项目复杂度选择合适的层级切入，也可以混合使用

---

## 六、选型总结

| 需求 | 推荐 |
|------|------|
| 想快速开始 | LangChain |
| 想精细控制 | LangGraph |
| 想让 Agent 自主完成复杂任务 | Deep Agents SDK |

根据项目的复杂度和控制需求，选择合适的层级。简单项目从 LangChain 入手；需要精细编排时用 LangGraph；面对高度自主的复杂任务时用 Deep Agents SDK。
