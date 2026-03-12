from langchain.messages import AIMessageChunk
from rich import print

from src.simple_chat import agent

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "1+1=?, 请详细说明。"}]},
    stream_mode="messages",
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        print(token, metadata)
        # if not isinstance(token, AIMessageChunk):
        #     continue
        # reasoning = token.additional_kwargs.get("reasoning_content", "")
        # if reasoning:
        #     print(f"[思考] {reasoning}", end="", flush=True)
        # if token.content:
        #     print(token.content, end="", flush=True)

print()