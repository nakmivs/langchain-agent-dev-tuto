from langchain_openai import ChatOpenAI

def get_llm(model_name: str="doubao-seed-2-0-pro-260215", temperature: float=0.0, **kwargs):
    return ChatOpenAI(
        model=model_name, 
        temperature=temperature,
        api_key="bd3d5056-581d-42e6-8359-7c2b07be9484",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        **kwargs,
    )