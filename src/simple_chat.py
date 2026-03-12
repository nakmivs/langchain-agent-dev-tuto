from langchain.agents import create_agent
from src.llm import get_llm



agent = create_agent(
    model=get_llm(),
    system_prompt="You are a helpful assistant.",
)
# print(agent.invoke({"messages": [{"role": "user", "content": "Hello, how are you?"}]}))