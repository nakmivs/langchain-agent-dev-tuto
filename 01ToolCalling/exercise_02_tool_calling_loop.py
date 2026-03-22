"""
============================================================
练习 2（进阶）：实现完整的 Tool Calling 循环
============================================================

【题目描述】
使用 LangChain 实现一个能够调用工具的完整循环：
  用户提问 → LLM 判断是否需要工具 → 调用工具 → 将结果反馈给 LLM → 生成最终回答

场景：天气查询助手，具备以下 2 个工具：
  1. get_weather — 查询指定城市的当前天气（返回模拟数据即可）
  2. get_forecast — 查询指定城市未来几天的天气预报（返回模拟数据即可）

【要求】
1. 使用 @tool 装饰器定义 2 个工具，注意 description 质量（练习 1 的经验）
2. 使用 bind_tools 将工具绑定到 LLM
3. 实现完整的 Tool Calling 循环：
   - LLM 返回 tool_calls → 执行对应工具 → 将 ToolMessage 反馈给 LLM → LLM 继续推理
   - LLM 未返回 tool_calls → 直接输出最终回答
   - 支持一次对话中多轮/多个工具调用
4. 在 main 中用至少 3 个测试用例验证：
   - 需要调用工具的问题（如"北京今天天气怎么样？"）
   - 不需要调用工具的问题（如"你好，你是谁？"）
   - 需要调用多个工具的问题（如"北京今天天气如何？顺便看看未来3天的预报"）

【学习目的】
- 掌握 @tool 装饰器的用法，理解它与手写 JSON Schema 的对应关系
- 理解 bind_tools 的作用——让 LLM 知道有哪些工具可用
- 实现 ReAct 循环的核心逻辑：推理 → 行动 → 观察 → 再推理
- 正确处理"调用工具"和"不调用工具"两种分支
- 理解 ToolMessage 的结构和 tool_call_id 的配对机制
============================================================
"""
from pydantic import BaseModel, Field
from rich import print
from langchain.tools import tool
from langchain.messages import HumanMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
import asyncio

from llm import get_llm


class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class WeatherTool(BaseModel):
    """查询城市天气"""
    city: str = Field(description="城市名称")

class Forecast(BaseModel):
    """查询天气预报"""
    city: str = Field(description="城市名称")
    date_num: int = Field(default=1, ge=1, le=7,description="未来几天。默认为1，最小为1，最大为7")

@tool(args_schema=WeatherTool)
async def get_weather(city: str) -> str:
    """查询城市天气"""
    return f"城市{city}的天气是晴天，气温26度，东风3级。"

@tool(args_schema=Forecast)
async def get_forecast(city: str, date_num: int=1) -> str:
    """获取未来几天的天气"""
    return f"{city} 未来{date_num}天多云转晴。"

tools_book = {
    "get_weather": get_weather,
    "get_forecast": get_forecast
}


# model = get_llm(provider="dashscope", model="qwen3.5-flash")

# model_with_tools = model.bind_tools([get_weather])

# response = model_with_tools.invoke([HumanMessage(content="北京今天天气怎么样？")])


async def llm_call(state: MessageState) -> MessageState:
    model = get_llm(provider="dashscope", model="qwen3.5-flash")
    model_with_tools = model.bind_tools([get_weather, get_forecast])
    response = await model_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}

async def tool_node(state: MessageState) -> MessageState:
    messages = state["messages"]
    last_message = messages[-1]
    tool_messages = []
    tasks = []
    for tool_call in last_message.tool_calls:
        tasks.append(tools_book[tool_call["name"]].ainvoke(input=tool_call["args"]))
    results = await asyncio.gather(*tasks)
    for (tc, result) in zip(last_message.tool_calls, results):
        tool_messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
    return {"messages": tool_messages}

async def tool_router(state: MessageState) -> str:
    last_message = state["messages"][-1]
    # 下面之所以用getattr，AIMessage 抽象后的 tool_calls 不一定总是稳定存在或为列表
    tool_calls = getattr(last_message, "tool_calls", []) or []
    if tool_calls:
        return "tool_node"
    return "end"



graph_builder = StateGraph(state_schema=MessageState)

graph_builder.add_node("llm_call", llm_call)
graph_builder.add_node("tool_node", tool_node)

graph_builder.add_conditional_edges(
    "llm_call",
    tool_router,
    {
        "tool_node": "tool_node",
        "end": END
    }
)
graph_builder.add_edge("tool_node", "llm_call")
graph_builder.add_edge(START, "llm_call")


agent = graph_builder.compile()


if __name__ == "__main__":
    async def main():
        response = await agent.ainvoke({
            "messages": [HumanMessage(content="今天成都未来3天气咋样?")]
        })
        print(response)

    asyncio.run(main())