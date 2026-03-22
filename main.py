from email.policy import strict
from pydantic import BaseModel
from rich import print
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.tools import tool

from llm import get_llm

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

agent = create_agent(
    model=get_llm(provider="dashscope", model="qwen3.5-max"),
    tools=[search],
    response_format=ProviderStrategy(ContactInfo)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
})

# result["structured_response"]
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
print(result["structured_response"])
