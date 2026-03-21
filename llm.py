from langchain_openai import ChatOpenAI

def get_llm(model_name: str="doubao-seed-2-0-pro-260215", temperature: float=0.0, reasoning_effort: str=None, **kwargs):
    extra_body = kwargs.pop("extra_body", {}) or {}
    if reasoning_effort:
        extra_body["reasoning_effort"] = reasoning_effort
    return ChatOpenAI(
        model=model_name, 
        temperature=temperature,
        api_key="bd3d5056-581d-42e6-8359-7c2b07be9484",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        extra_body=extra_body or None,
        **kwargs,
    )