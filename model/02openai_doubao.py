from langchain.messages import HumanMessage
from rich import print
from settings import settings
from patched_openai import PatchedChatOpenAI


model = PatchedChatOpenAI(
    model="doubao-seed-2-0-lite-260215",
    api_key=settings.volcengine_api_key,
    base_url=settings.volcengine_api_base,
    use_responses_api=True,
    output_version="responses/v1",
    reasoning={"effort": "high"},
)


question = HumanMessage(content="我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性")


def iter_content_blocks(chunk) -> list[dict]:
    blocks = getattr(chunk, "content_blocks", None)
    if blocks:
        return blocks

    content = getattr(chunk, "content", None)
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict) and "type" in block]
    if isinstance(content, str) and content:
        return [{"type": "text", "text": content}]
    return []


async def stream():
    printed_reasoning = False
    printed_answer = False

    async for chunk in model.astream([question]):
        print(chunk)
        # for block in iter_content_blocks(chunk):
            # block_type = block.get("type")

            # if block_type == "reasoning":
            #     reasoning = block.get("reasoning", "")
            #     if reasoning:
            #         if not printed_reasoning:
            #             print("\n[bold yellow]=== Reasoning ===[/bold yellow]")
            #             printed_reasoning = True
            #         print(reasoning, end="")

            # elif block_type == "text":
            #     text = block.get("text", "")
            #     if text:
            #         if not printed_answer:
            #             print("\n\n[bold green]=== Final Answer ===[/bold green]")
            #             printed_answer = True
            #         print(text, end="")

    print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(stream())