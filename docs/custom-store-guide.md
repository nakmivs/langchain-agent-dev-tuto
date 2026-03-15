# 自定义 Postgres Store 指南

## 背景

在 LangGraph 的 Self-host standalone server 部署模式下，记忆（memory）和持久化**不需要写在 agent 创建代码中**，而是由服务器基础设施自动管理。

服务器默认提供两类内置记忆：

| 类型 | 说明 | 配置来源 |
|------|------|----------|
| **Checkpointer**（短期记忆） | 对话状态持久化，按 thread 隔离 | `DATABASE_URI` 环境变量，自动连接 Postgres |
| **Store**（长期记忆） | 跨会话持久化，支持语义搜索 | `DATABASE_URI` 环境变量，自动连接 Postgres |

如果默认的 Postgres Store 不能满足需求（如需要启用语义搜索、自定义 embedding 模型、自定义索引字段等），可以通过自定义 Store 来替代。

## 自定义 Store 的步骤

### 步骤一：创建 store 定义文件

在项目中新建文件（如 `src/store.py`），定义一个 **async context manager** 函数，yield 出定制的 store 实例：

```python
# src/store.py
import os
import contextlib
from langchain.embeddings import init_embeddings
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.store.base import IndexConfig


@contextlib.asynccontextmanager
async def generate_store():
    """自定义 Postgres Store，启用语义搜索。"""
    embeddings = init_embeddings("openai:text-embedding-3-small")

    async with AsyncPostgresStore.from_conn_string(
        # 服务器通过 DATABASE_URI 环境变量注入连接字符串
        conn_string=os.environ["DATABASE_URI"],
        index=IndexConfig(
            dims=1536,            # embedding 维度，取决于所选模型
            embed=embeddings,     # embedding 函数
            fields=["$"],         # 要索引的 JSON 字段，"$" 表示整个文档
        ),
    ) as store:
        await store.setup()
        yield store
```

关键配置说明：

- **`IndexConfig`** 是启用语义搜索的核心配置：
  - `dims`：embedding 向量维度（`text-embedding-3-small` 为 1536）
  - `embed`：用什么 embedding 模型来向量化
  - `fields`：哪些字段参与语义搜索，`["$"]` 表示整个 value
- **`AsyncPostgresStore`** 是异步版本，standalone server 要求使用异步
- 连接字符串通过 `DATABASE_URI` 环境变量获取，和服务器共用同一个 Postgres

### 步骤二：在 langgraph.json 中配置

在 `langgraph.json` 中添加 `store` 字段，指向步骤一中定义的函数：

```json
{
    "dependencies": ["."],
    "graphs": {
        "chat_agent": "./src/simple_chat.py:agent",
        "weather_agent": "./src/weather_agent.py:agent"
    },
    "env": ".env",
    "python_version": "3.13",
    "image_distro": "wolfi",
    "store": {
        "path": "./src/store.py:generate_store"
    }
}
```

`"path"` 的格式是 `文件路径:函数名`，和 `graphs` 中的格式一致。

### 步骤三：在 agent 中使用 store

Agent 代码**不需要**手动创建或传入 store。服务器会自动把 store 注入到 graph 节点的 `store` 参数中：

```python
from langgraph.store.base import BaseStore


async def my_node(state, *, store: BaseStore):
    # 写入记忆
    await store.aput(
        namespace=("memories", "user_123"),
        key="preference",
        value={"food": "pizza", "color": "blue"}
    )

    # 语义搜索记忆（因为配置了 IndexConfig）
    results = await store.asearch(
        namespace=("memories", "user_123"),
        query="用户喜欢什么食物",
        limit=5
    )
    return state
```

## 注意事项

1. **自定义 store 会完全替代内置 store**。语义搜索、TTL 清理等功能取决于你的实现。

2. **需要 pgvector 扩展**：如果使用语义搜索，Postgres 数据库需要安装 `pgvector` 扩展。可以在 `docker-compose` 中使用 `pgvector/pgvector:pg16` 镜像代替普通 `postgres:16`。

3. **embedding 依赖**：根据所选的 embedding 提供商，需要在 `pyproject.toml` 中添加对应的包（如 `langchain-openai`）。

4. **本地测试**：配好后运行 `langgraph dev --no-browser` 即可本地测试，日志中会显示 `Using custom store. Skipping store TTL sweeper.`。

## 与现有 `src/dps/memory/post.py` 做法的对比

| | 现有做法（`post.py`） | 自定义 store 的做法 |
|---|---|---|
| Store 创建 | 代码中手动 `PostgresStore.from_conn_string()` | `langgraph.json` 指向 async context manager |
| 连接管理 | 手动 `__enter__()` / `__exit__()` | 服务器自动管理生命周期 |
| 注入方式 | 手动传给 `create_deep_agent(store=store)` | 服务器自动注入到节点的 `store` 参数 |
| 语义搜索 | 未配置 | 通过 `IndexConfig` 配置 |

## 参考文档

- [Self-host standalone servers](https://docs.langchain.com/langsmith/deploy-standalone-server)
- [How to use a custom store](https://docs.langchain.com/langsmith/custom-store)
- [How to use a custom checkpointer](https://docs.langchain.com/langsmith/custom-checkpointer)
- [Application structure](https://docs.langchain.com/langsmith/application-structure)
