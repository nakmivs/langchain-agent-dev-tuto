# QA003：ToolMessage 的结构，以及返回值用 JSON 时需要解释 key 吗？

## 问题

ToolMessage 的结构是什么样的？content 中放 JSON 是否更好？如果放 JSON，需要解释每个 key 吗？不解释的话模型可能理解不清数据。

## 回答

### 消息类型全景

一次 Tool Calling 对话中的 4 种消息角色：

1. **SystemMessage** (`role: "system"`) — 系统提示词
2. **HumanMessage** (`role: "user"`) — 用户输入
3. **AIMessage** (`role: "assistant"`) — LLM 回复，可能含 `tool_calls`
4. **ToolMessage** (`role: "tool"`) — 工具执行结果

### AIMessage 带 tool_calls 的结构

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\": \"北京\"}"
      }
    }
  ]
}
```

关键点：
- `content` 通常为 `null`（选择调用工具而非直接回答）
- `tool_calls` 是数组（可并行调用多个工具）
- 每个 tool_call 有唯一 `id`，用于与 ToolMessage 配对
- `arguments` 是 JSON **字符串**，需要 `json.loads()` 解析

### ToolMessage 的结构

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "当前北京天气：晴，气温25°C，东风3级"
}
```

| 字段 | 含义 |
|------|------|
| `role` | 固定为 `"tool"` |
| `tool_call_id` | 必须与 AIMessage 中对应 tool_call 的 `id` 一致 |
| `content` | 工具执行结果，为字符串（JSON 对象需序列化为字符串） |

### content 放 JSON 还是纯文本？

**放 JSON 更好**，结构化数据更精确、更紧凑、token 消耗更少。

### key 需要解释吗？

**取决于 key 的可读性：**

- **自解释的 key 不需要额外解释**：`user_name`、`balance`、`account_type` 这类常见英文词汇，LLM 训练数据中见过大量 JSON，一看就懂
- **缩写或业务术语需要解释**：`acct_tp`、`DDA`、`txn_cd` 这些 LLM 大概率理解不了

### 最佳实践：在工具 description 中预告返回格式

```json
{
  "name": "get_account_balance",
  "description": "查询用户银行账户余额。返回 JSON，字段包括：acct_tp(账户类型，DDA=活期/SA=定期)、avl_bal(可用余额，单位元)",
  "parameters": { ... }
}
```

LLM 在发起调用之前就已经读到 description，所以返回结果时它已经知道每个 key 的含义。

### 实际建议

| 原则 | 说明 |
|------|------|
| key 用清晰的英文命名 | `balance` 不要写 `bal`，`account_type` 不要写 `tp` |
| 值要有上下文 | 金额在 description 中说明单位，状态用有意义的枚举（`active` 而非 `1`）|
| 复杂结构在 description 中预告 | 字段多或含业务术语时，在工具定义中说明返回格式 |
| 不需要每个 key 都解释 | 只要是常见英文词汇，LLM 基本都能正确理解 |
