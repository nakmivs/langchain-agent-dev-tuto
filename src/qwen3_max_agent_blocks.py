import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, ToolMessage, ToolMessageChunk
from langchain_core.tools import tool
from langchain_qwq import ChatQwen

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


def iter_content_blocks(message_chunk) -> list[dict]:
    blocks = getattr(message_chunk, "content_blocks", None)
    if blocks:
        return blocks

    content = getattr(message_chunk, "content", None)
    if isinstance(content, str) and content:
        return [{"type": "text", "text": content}]

    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict) and "type" in block]

    return []


def print_tool_output(message_chunk, printed_tool_output: bool) -> bool:
    content = getattr(message_chunk, "content", "")
    if not isinstance(content, str) or not content:
        return printed_tool_output

    if not printed_tool_output:
        print("\n=== Tool Output ===")
    print(content, end="", flush=True)
    return True


def stream_agent_response(user_input: str) -> None:
    agent = build_agent()

    printed_reasoning = False
    printed_tool_output = False
    printed_final_answer = False

    for message_chunk, _metadata in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="messages",
    ):
        # if isinstance(message_chunk, (ToolMessage, ToolMessageChunk)):
        #     printed_tool_output = print_tool_output(message_chunk, printed_tool_output)
        #     continue

        # if not isinstance(message_chunk, AIMessageChunk):
        #     continue

        # for block in iter_content_blocks(message_chunk):
        for block in message_chunk.content_blocks:
            block_type = block.get("type")

            if block_type == "reasoning":
                reasoning = block.get("reasoning", "")
                if reasoning:
                    if not printed_reasoning:
                        print("\n=== Reasoning ===")
                        printed_reasoning = True
                    print(reasoning, end="", flush=True)

            elif block_type == "text":
                text = block.get("text", "")
                if text:
                    if not printed_final_answer:
                        print("\n\n=== Final Answer ===")
                        printed_final_answer = True
                    print(text, end="", flush=True)

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
