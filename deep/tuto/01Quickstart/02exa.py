from langchain.agents import create_agent
from langchain.messages import HumanMessage
from tools import internet_search
from llm import get_llm
from rich import print
from langfuse_tracing import langfuse_handler
# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

model = get_llm("dashscope", "qwen3.5-flash")

agent = create_agent(
    model=model,
    system_prompt=research_instructions,
    tools=[internet_search],
).with_config(
    {
        "callbacks": [langfuse_handler]
    }
)

response = agent.invoke(
    {
        "messages": [HumanMessage(content="今天成都的天气？")]
    }
)
print(response)

