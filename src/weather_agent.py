# pip install -qU deepagents
from deepagents import create_deep_agent
from src.llm import get_llm

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model=get_llm(),
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# # Run the agent
# agent.invoke(
#     {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
# )