import asyncio
from langgraph_sdk import get_client

BASE_URL = "http://127.0.0.1:2024"
GRAPH_ID = "simplechat"


async def main():
    client = get_client(url=BASE_URL)

    # 1. 创建一个 thread
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    print("thread_id =", thread_id)

    # 2. 第一次运行
    run1 = await client.runs.create(
        thread_id=thread_id,
        assistant_id=GRAPH_ID,
        input={
            "messages": [
                {"role": "user", "content": "你好，我叫 nakmi，请记住我的名字。"}
            ]
        },
    )
    await client.runs.join(thread_id, run1["run_id"])
    state1 = await client.threads.get_state(thread_id)
    print("state after run1 =", state1["values"])

    # 3. 第二次运行，复用同一个 thread_id
    run2 = await client.runs.create(
        thread_id=thread_id,
        assistant_id=GRAPH_ID,
        input={
            "messages": [
                {"role": "user", "content": "我刚刚告诉过你我叫什么？"}
            ]
        },
    )
    await client.runs.join(thread_id, run2["run_id"])
    state2 = await client.threads.get_state(thread_id)
    print("state after run2 =", state2["values"])

    # 4. 可选：看看 checkpoint 元数据
    print("checkpoint =", state2.get("checkpoint"))


if __name__ == "__main__":
    asyncio.run(main())