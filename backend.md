两个页面的内容我已经获取到了，下面给你系统讲解 Deep Agent 的 Backend 体系。

---

## Deep Agent Backend 全景解析

### 一、Backend 是什么？

Backend 是 Deep Agent 的**虚拟文件系统层**。Agent 通过一组统一的工具（`ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`）来操作"文件"，但这些文件实际存储在哪里、怎么存储，完全由 Backend 决定。

```
Agent 看到的世界：
┌─────────────────────────────────┐
│  ls / read_file / write_file    │  ← 统一的工具接口
│  edit_file / glob / grep        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│          Backend 层              │  ← 可插拔，决定数据存在哪
├─────┬──────┬───────┬────────────┤
│State│ Disk │ Store │ Sandbox/   │
│     │      │       │ Composite  │
└─────┴──────┴───────┴────────────┘
```

### 二、六种内置 Backend

#### 1. StateBackend（默认，临时型）

```python
agent = create_deep_agent()  # 默认就是 StateBackend
```

- **存储位置**：LangGraph 的 agent state（内存 + checkpoint）
- **生命周期**：同一个 thread 内持久化，thread 结束即消失
- **特点**：主 Agent 和子 Agent 共享同一个文件空间
- **适合**：临时草稿、中间结果、自动卸载大型工具输出
- **多用户**：天然按 `thread_id` 隔离，**最适合 Web API 场景**

#### 2. FilesystemBackend（本地磁盘）

```python
from deepagents.backends import FilesystemBackend
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True)
)
```

- **存储位置**：你机器上的真实文件系统
- **安全提醒**：文档**明确警告** — 不适合 Web 服务器或 HTTP API
- **适合**：本地开发 CLI、CI/CD 流水线
- `virtual_mode=True` 可以限制路径，防止 `..` 和绝对路径穿越

#### 3. LocalShellBackend（本地磁盘 + Shell 执行）

```python
from deepagents.backends import LocalShellBackend
agent = create_deep_agent(
    backend=LocalShellBackend(root_dir=".", env={"PATH": "/usr/bin:/bin"})
)
```

- 继承 FilesystemBackend，额外提供 `execute` 工具（执行 shell 命令）
- 底层用 `subprocess.run(shell=True)`，**没有任何沙箱隔离**
- **仅适合**个人开发环境，**绝对不能**用于生产
- 支持 `timeout`（默认120s）、`max_output_bytes`（默认100,000）

#### 4. StoreBackend（持久化存储）

```python
from langgraph.store.memory import InMemoryStore
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    backend=(lambda rt: StoreBackend(rt)),
    store=InMemoryStore()  # 生产环境可以用 Postgres/Redis
)
```

- **存储位置**：LangGraph 的 `BaseStore`（可接 Redis、Postgres 等）
- **生命周期**：**跨 thread 持久化**，不同对话都能访问
- **适合**：长期记忆、用户偏好、跨会话的知识积累
- 部署到 LangSmith 时，平台自动提供 Store，无需手动配置

#### 5. CompositeBackend（路由组合型）— 生产环境推荐

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),          # 默认：临时空间
    routes={
        "/memories/": StoreBackend(rt), # /memories/ 路径：持久化
    }
)

agent = create_deep_agent(
    backend=composite_backend,
    store=InMemoryStore()
)
```

- 按**路径前缀**路由到不同 Backend
- 更长的前缀优先匹配（`/memories/projects/` 优先于 `/memories/`）
- `ls`、`glob`、`grep` 会**聚合**所有 Backend 的结果

实际效果：

```
/workspace/plan.md      → StateBackend（临时，thread结束就没了）
/workspace/research.md  → StateBackend（同上）
/memories/agent.md      → StoreBackend（永久保存，跨对话可用）
/memories/prefs.txt     → StoreBackend（同上）
```

#### 6. Sandbox Backend（沙箱型）

```python
agent = create_deep_agent(backend=sandbox)
```

- 在隔离环境中执行代码（Modal、Daytona、Deno 等）
- 提供 `execute` 工具但运行在沙箱里，安全性高
- **适合**：生产环境需要代码执行的场景

---

### 三、Backend 的上下文管理机制

Backend 不仅仅是"存文件"，它和 Harness 的上下文管理紧密配合：

**自动卸载大型内容（Offloading）**

当工具的输入或输出超过 **20,000 tokens** 时（可配置 `tool_token_limit_before_evict`），Deep Agent 会自动：
1. 把内容写入 Backend 的文件系统
2. 在对话历史中只留一个文件路径引用 + 前10行预览
3. Agent 需要时再通过 `read_file` / `grep` 按需读取

**自动摘要（Summarization）**

当上下文达到模型窗口的 **85%** 时：
1. LLM 生成结构化摘要（意图、产物、下一步）替换完整历史
2. 完整的原始对话保存到文件系统作为备份
3. Agent 可以随时通过文件系统搜索回顾细节

---

### 四、自定义 Backend

你可以实现 `BackendProtocol` 接口来对接任何存储：

**S3 示例**：

```python
class S3Backend(BackendProtocol):
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
    
    def ls_info(self, path): ...
    def read(self, file_path, offset=0, limit=2000): ...
    def write(self, file_path, content): ...
    def edit(self, file_path, old_string, new_string, replace_all=False): ...
    def grep_raw(self, pattern, path=None, glob=None): ...
    def glob_info(self, pattern, path="/"): ...
```

**Postgres 示例**：建一张 `files(path, content, created_at, modified_at)` 表，把文件操作映射成 SQL。

你还可以用 **PolicyWrapper** 添加策略钩子，比如禁止写入特定路径：

```python
class GuardedBackend(FilesystemBackend):
    def __init__(self, *, deny_prefixes: list[str], **kwargs):
        super().__init__(**kwargs)
        self.deny_prefixes = deny_prefixes

    def write(self, file_path, content):
        if any(file_path.startswith(p) for p in self.deny_prefixes):
            return WriteResult(error=f"Writes not allowed under {file_path}")
        return super().write(file_path, content)
```

---

### 五、回到你之前的问题

| 你的疑问 | 答案 |
|---|---|
| 每个用户需要创建虚拟空间？ | 不需要，`StateBackend` 按 `thread_id` 自动隔离 |
| 怎么暴露接口？ | 一个 agent 实例 + 不同 `thread_id` 即可服务多用户 |
| 长期记忆怎么存？ | `CompositeBackend` 把 `/memories/` 路由到 `StoreBackend`（Postgres/Redis） |
| 生产环境用哪个？ | **CompositeBackend**（State + Store 组合），**不要**用 FilesystemBackend |

本质上，Backend 就是 Deep Agent 的"大脑外存"——Agent 以为自己在操作文件系统，但实际上你可以把数据放在任何地方。这种抽象让同一套 Agent 代码既能在本地开发时直接读写磁盘，也能在生产环境中安全地服务百万用户。