# LangGraph 前端 SDK：useStream React Hook

> 来源：[Frontend — Deep Agents Streaming](https://docs.langchain.com/oss/python/deepagents/streaming/frontend)

`useStream` 是 `@langchain/langgraph-sdk/react` 提供的 React Hook，用于在前端实时流式接收 LangGraph Agent Server 的响应，并内置了对 Deep Agent（多子 Agent 架构）的完整支持。

---

## 一、定位与作用

`useStream` 在整个技术栈中处于**前端接入层**，连接 React UI 和后端的 LangGraph Agent Server：

```
React 前端应用
    └── useStream Hook（@langchain/langgraph-sdk/react）
            └── HTTP/SSE 流式连接
                    └── LangGraph Agent Server（如 localhost:2024）
```

| 层级 | 技术 | 职责 |
|------|------|------|
| 后端 | LangGraph (Python) | 构建和运行 Agent，处理 LLM 调用、工具执行、子 Agent 编排 |
| SDK | @langchain/langgraph-sdk | 提供 `useStream` Hook，封装流式通信协议 |
| 前端 | React 应用 | 展示对话消息、子 Agent 运行状态、工具调用过程 |

它**不是**用来构建 Agent 的工具，而是用来**在前端 UI 中展示 Agent 运行过程和结果**的。

---

## 二、安装与基本用法

### 安装

```bash
npm install @langchain/langgraph-sdk
```

### 最简示例

```tsx
import { useStream } from "@langchain/langgraph-sdk/react";

function AgentChat() {
  const stream = useStream({
    assistantId: "my-agent",
    apiUrl: "http://localhost:2024",
  });

  const handleSubmit = (message: string) => {
    stream.submit(
      { messages: [{ content: message, type: "human" }] },
      { streamSubgraphs: true }
    );
  };

  return (
    <div>
      {stream.messages.map((msg, idx) => (
        <div key={msg.id ?? idx}>
          {msg.type}: {msg.content}
        </div>
      ))}
      {stream.isLoading && <div>加载中...</div>}
    </div>
  );
}
```

关键参数：

| 参数 | 说明 |
|------|------|
| `assistantId` | Agent 的 ID，对应后端部署的 Agent 名称 |
| `apiUrl` | LangGraph Server 地址 |
| `filterSubagentMessages` | 设为 `true` 时，子 Agent 消息从主消息流中分离 |
| `streamSubgraphs` | 提交时设为 `true`，启用子 Agent 流式传输 |

---

## 三、核心能力

### 3.1 子 Agent 生命周期追踪

自动管理每个子 Agent 的状态：`pending` → `running` → `complete` / `error`。

通过 `stream.subagents`（Map 结构）和 `stream.activeSubagents`（数组）访问所有子 Agent 的实时状态。

### 3.2 消息过滤

启用 `filterSubagentMessages: true` 后：

- `stream.messages` 只包含主对话消息，UI 保持清晰
- 子 Agent 的消息通过 `stream.subagents.get(id).messages` 单独访问

### 3.3 Tool Call 可见性

每个子 Agent 暴露 `toolCalls` 属性，可以展示它在执行过程中调用了哪些工具、传了什么参数、返回了什么结果。

### 3.4 状态恢复

页面刷新后，`useStream` 可以从 Thread 历史中重建子 Agent 状态。已完成的子 Agent 会恢复为最终状态和结果，用户看到完整的对话历史。

---

## 四、SubagentStream 接口

每个子 Agent 在 `stream.subagents` Map 中的数据结构：

```tsx
interface SubagentStream {
  // 身份
  id: string;                    // Tool Call ID
  toolCall: {
    subagent_type: string;       // 子 Agent 类型，如 "researcher"
    description: string;         // 任务描述
  };

  // 生命周期
  status: "pending" | "running" | "complete" | "error";
  startedAt: Date | null;
  completedAt: Date | null;
  isLoading: boolean;

  // 内容
  messages: Message[];           // 子 Agent 的消息流
  values: Record<string, any>;   // 子 Agent 的状态
  result: string | null;         // 最终结果
  error: string | null;          // 错误信息

  // 工具调用
  toolCalls: ToolCallWithResult[];

  // 层级
  depth: number;                 // 嵌套深度（顶层为 0）
  parentId: string | null;       // 父级子 Agent ID
}
```

### 访问子 Agent 的方法

| 方法 | 说明 |
|------|------|
| `stream.subagents` | 所有子 Agent 的 Map，以 Tool Call ID 为 key |
| `stream.activeSubagents` | 当前正在运行的子 Agent 数组 |
| `stream.getSubagent(id)` | 按 Tool Call ID 获取单个子 Agent |
| `stream.getSubagentsByMessage(msgId)` | 获取某条 AI 消息触发的所有子 Agent |
| `stream.getSubagentsByType(type)` | 按类型筛选子 Agent |

---

## 五、常见 UI 模式

### 5.1 子 Agent 卡片

展示每个子 Agent 的类型、描述、状态和流式内容：

```tsx
function SubagentCard({ subagent }: { subagent: SubagentStream }) {
  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <StatusIcon status={subagent.status} />
        <span className="font-medium">{subagent.toolCall.subagent_type}</span>
        <span className="text-sm text-gray-500">
          {subagent.toolCall.description}
        </span>
      </div>

      {subagent.status === "complete" && subagent.result && (
        <div className="mt-2 p-2 bg-green-50 rounded text-sm">
          {subagent.result}
        </div>
      )}

      {subagent.status === "error" && subagent.error && (
        <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
          {subagent.error}
        </div>
      )}
    </div>
  );
}
```

### 5.2 进度条

用完成数/总数展示整体进度：

```tsx
function SubagentPipeline({ subagents }: { subagents: SubagentStream[] }) {
  const completed = subagents.filter(
    (s) => s.status === "complete" || s.status === "error"
  ).length;

  return (
    <div>
      <span>子 Agent ({completed}/{subagents.length})</span>
      <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 transition-all duration-300"
          style={{ width: `${(completed / subagents.length) * 100}%` }}
        />
      </div>
    </div>
  );
}
```

### 5.3 Tool Call 展示

展示子 Agent 执行了哪些工具调用及其结果：

```tsx
{subagent.toolCalls.map((tc) => (
  <div key={tc.call.id} className="p-2 bg-gray-50 rounded text-sm">
    <span className="font-mono text-xs">{tc.call.name}</span>
    <pre className="text-xs text-gray-600 mt-1">
      {JSON.stringify(tc.call.args, null, 2)}
    </pre>
    {tc.result !== undefined && (
      <div className="mt-1 pt-1 border-t text-xs">
        {typeof tc.result === "string"
          ? tc.result.slice(0, 200)
          : JSON.stringify(tc.result, null, 2)}
      </div>
    )}
  </div>
))}
```

---

## 六、Thread 持久化

通过持久化 Thread ID，支持页面刷新后恢复完整对话（包括子 Agent 状态）。

```tsx
function PersistentChat() {
  const [threadId, setThreadId] = useState<string | null>(() => {
    return new URLSearchParams(window.location.search).get("threadId");
  });

  const updateThreadId = useCallback((id: string) => {
    setThreadId(id);
    const url = new URL(window.location.href);
    url.searchParams.set("threadId", id);
    window.history.replaceState({}, "", url.toString());
  }, []);

  const stream = useStream({
    assistantId: "my-agent",
    apiUrl: "http://localhost:2024",
    filterSubagentMessages: true,
    threadId,
    onThreadId: updateThreadId,
    reconnectOnMount: true, // 页面刷新后自动恢复流
  });

  // ...渲染逻辑
}
```

关键点：

- `threadId` 存在 URL 参数中，刷新后可读取
- `onThreadId` 回调在新建 Thread 时触发，更新 URL
- `reconnectOnMount: true` 让页面刷新后自动恢复流式连接
- 已完成的子 Agent 从 Thread 历史中重建，保留最终状态和结果

---

## 七、与现有生态的关系

| 组件 | 角色 | 关系 |
|------|------|------|
| LangGraph (Python) | Agent 运行时 | 后端，构建和运行 Agent |
| LangGraph Server | 部署服务 | 托管 Agent，提供 HTTP API |
| @langchain/langgraph-sdk | 前端 SDK | 连接 Server，封装流式协议 |
| useStream Hook | React 集成 | SDK 的 React 封装，提供 Hook API |
| Deep Agents SDK | 高级 Agent 框架 | 提供子 Agent 编排能力，useStream 对其有原生支持 |
| Agent Chat UI | 预构建 UI | LangGraph 官方提供的现成聊天界面，内部使用 useStream |

**使用时机**：当你需要为 Agent 构建自定义 Web 界面时使用。如果只是后端开发和测试 Agent，暂时不需要它。官方也提供了现成的 [Agent Chat UI](https://docs.langchain.com/oss/python/langchain/ui)，可以直接使用而不需要自己写前端。
