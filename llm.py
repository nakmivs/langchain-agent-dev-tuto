import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_qwq import ChatQwen


def get_llm(provider: str, model: str, temperature: float=0.0, reasoning_effort: str=None, **kwargs):
    extra_body = kwargs.pop("extra_body", {}) or {}
    if reasoning_effort:
        extra_body["reasoning_effort"] = reasoning_effort

    if provider == "volcengine":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key="bd3d5056-581d-42e6-8359-7c2b07be9484",
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            extra_body=extra_body or None,
            **kwargs,
        )
    elif provider == "dashscope":
        return ChatQwen(
            base_url=os.getenv("DASHSCOPE_API_BASE"),
            model=model,
            temperature=temperature,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            **kwargs,
        ) 
    else:
        raise ValueError(f"Invalid provider: {provider}")