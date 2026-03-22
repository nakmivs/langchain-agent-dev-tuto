"""研究工具模块。

提供研究智能体所需的搜索与内容处理工具，
使用 Tavily 进行 URL 发现并抓取完整网页内容。
"""

import httpx
from langchain_core.tools import InjectedToolArg, tool
from markdownify import markdownify
from tavily import TavilyClient
from typing_extensions import Annotated, Literal
import os
from dotenv import load_dotenv
load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """抓取网页内容并转换为 Markdown 格式。

    Args:
        url: 目标网页 URL
        timeout: 请求超时时间（秒）

    Returns:
        Markdown 格式的网页内容
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return markdownify(response.text)
    except Exception as e:
        return f"抓取 {url} 内容时出错：{str(e)}"


@tool(parse_docstring=True)
def tavily_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 1,
    topic: Annotated[
        Literal["general", "news", "finance"], InjectedToolArg
    ] = "general",
) -> str:
    """根据给定查询在网络上搜索信息。

    使用 Tavily 发现相关 URL，然后抓取并返回完整网页内容（Markdown 格式）。

    Args:
        query: 要执行的搜索查询
        max_results: 返回的最大结果数（默认：1）
        topic: 主题过滤 - 'general'（综合）、'news'（新闻）或 'finance'（财经）（默认：'general'）

    Returns:
        包含完整网页内容的格式化搜索结果
    """
    search_results = tavily_client.search(
        query,
        max_results=max_results,
        topic=topic,
    )

    result_texts = []
    for result in search_results.get("results", []):
        url = result["url"]
        title = result["title"]

        content = fetch_webpage_content(url)

        result_text = f"""## {title}
**URL:** {url}

{content}

---
"""
        result_texts.append(result_text)

    response = f"""🔍 为 '{query}' 找到 {len(result_texts)} 条结果：

{chr(10).join(result_texts)}"""

    return response


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """用于对研究进展进行战略性反思和决策的工具。

    每次搜索后使用此工具来分析结果并系统性地规划下一步行动。
    这会在研究工作流中创建一个有意的停顿，以确保高质量的决策。

    使用时机：
    - 收到搜索结果后：我找到了哪些关键信息？
    - 决定下一步之前：我是否有足够的信息来提供全面的回答？
    - 评估研究空白时：我还缺少哪些具体信息？
    - 结束研究之前：我现在能给出完整的回答吗？

    反思应涵盖：
    1. 当前发现分析 - 我收集到了哪些具体信息？
    2. 空白评估 - 还缺少哪些关键信息？
    3. 质量评估 - 我是否有足够的证据/示例来给出好的回答？
    4. 策略决策 - 应该继续搜索还是给出回答？

    Args:
        reflection: 对研究进展、发现、空白和下一步计划的详细反思

    Returns:
        确认反思已记录，用于后续决策
    """
    return f"反思已记录：{reflection}"
