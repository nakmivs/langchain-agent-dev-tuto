import os
import sys

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, ToolMessage, ToolMessageChunk
from langchain_core.tools import tool
from langchain_qwq import ChatQwen
from dotenv import load_dotenv

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"{city} is sunny, 26C."


def build_agent():
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("Please set DASHSCOPE_API_KEY before running this script.")

    model = ChatQwen(
        base_url=os.getenv("DASHSCOPE_API_BASE"),
        model="qwen3-max",
        enable_thinking=True,
        temperature=0.0,
        api_key=api_key,
    )

    return create_agent(
        model=model,
        tools=[get_weather],
        system_prompt=(
            "You are a helpful assistant. Think carefully, use tools when needed, "
            "and answer clearly."
        ),
    )


def stream_agent_response(user_input: str) -> None:
    agent = build_agent()

    printed_reasoning = False
    printed_tool_output = False
    printed_final_answer = False

    for message_chunk, _metadata in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="messages",
    ):
        reasoning = ""
        if hasattr(message_chunk, "additional_kwargs"):
            reasoning = message_chunk.additional_kwargs.get("reasoning_content", "")

        if reasoning:
            if not printed_reasoning:
                print("\n=== Reasoning ===")
                printed_reasoning = True
            print(reasoning, end="", flush=True)

        content = getattr(message_chunk, "content", "")
        if not isinstance(content, str) or not content:
            continue

        if isinstance(message_chunk, (ToolMessage, ToolMessageChunk)):
            if not printed_tool_output:
                print("\n\n=== Tool Output ===")
                printed_tool_output = True
            print(content, end="", flush=True)
            continue

        if isinstance(message_chunk, AIMessageChunk):
            if not printed_final_answer:
                print("\n\n=== Final Answer ===")
                printed_final_answer = True
            print(content, end="", flush=True)

    print()


def main() -> None:
    user_input = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "帮我查一下上海天气，然后解释一下今天为什么适合出门。"
    )
    stream_agent_response(user_input)


if __name__ == "__main__":
    main()
