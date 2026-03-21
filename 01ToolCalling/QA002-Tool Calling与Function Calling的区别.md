# QA002：Tool Calling 与 Function Calling 的区别？

## 问题

Tool Calling 和 Function Calling 有什么区别？

## 回答

**本质上是同一件事，只是术语演进了。**

### 历史演变

| 时间 | 事件 |
|------|------|
| 2023 年 6 月 | OpenAI 推出 **Function Calling**，API 使用 `functions` 参数 |
| 2023 年 11 月 | OpenAI 升级为 **Tool Calling**，API 改用 `tools` 参数，`functions` 标记为 deprecated |

### 为什么改名？

改名反映了**抽象层级的提升**：

- **Function** — 语义很具体，就是"调用一个函数"
- **Tool** — 更上层的抽象，"函数"只是工具的一种类型

在 OpenAI 当前的 API 中，每个 tool 有一个 `type` 字段：

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "...",
    "parameters": { ... }
  }
}
```

目前 `type` 几乎都是 `"function"`，但设计上预留了扩展空间。OpenAI Assistants API 已有 `code_interpreter`、`file_search` 等内置工具类型——它们不是函数，但都是"工具"。

### 实际使用

- 日常使用中两个词可以互换理解
- OpenAI API 用 `tools` 参数（`functions` 已废弃）
- LangChain/LangGraph 统一用 `tool` 术语（`.bind_tools()`、`@tool`）
- 其他厂商（Anthropic、Google、阿里等）也采用了 "Tool" 术语

### 一句话总结

> Function Calling 是 Tool Calling 的前身。Tool 是 Function 的超集——每个 Function 都是一种 Tool，但 Tool 不一定是 Function。
