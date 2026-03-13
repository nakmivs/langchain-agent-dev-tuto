"""Quick test script for the api_search tool.

Usage:
    uv run python src/tools/test_api_search.py
"""

import asyncio
import json
import os
import sys
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, "src")
from tools.api_search import api_search


def print_request_info(method: str, path: str, params: dict | None, body: dict | None):
    base_url = os.getenv("API_BASE_URL", "").rstrip("/")
    token = os.getenv("API_BEARER_TOKEN", "")

    url = f"{base_url}/{path.lstrip('/')}"
    full_url = f"{url}?{urlencode(params)}" if params else url

    print(f"Method:        {method}")
    print(f"Base URL:      {base_url}")
    print(f"Path:          {path}")
    print(f"Full URL:      {full_url}")
    print(f"Query Params:  {json.dumps(params, ensure_ascii=False) if params else 'None'}")
    print(f"Body:          {json.dumps(body, ensure_ascii=False, indent=2) if body else 'None'}")
    print(f"Bearer Token:  {token[:20]}...{token[-10:]}" if token else "Bearer Token:  (empty)")
    print("-" * 60)


async def main():
    method = "POST"
    path = "/government/monitor/economic/getByCondition"
    params = None
    body = {
        "indexTitle": "规上工业产值",
        "indexYear": 2025,
    }

    print("=" * 60)
    print("  请求信息")
    print("=" * 60)
    print_request_info(method, path, params, body)

    print("  响应结果")
    print("=" * 60)
    result = await api_search.ainvoke(
        {"method": method, "path": path, "params": params, "body": body}
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
