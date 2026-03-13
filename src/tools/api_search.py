import json
import os
from typing import Literal

import aiohttp
from langchain_core.tools import tool

_TIMEOUT = aiohttp.ClientTimeout(total=30)


@tool
async def api_search(
    method: Literal["GET", "POST"],
    path: str,
    params: dict | None = None,
    body: dict | None = None,
) -> str:
    """Call an external API endpoint.

    Args:
        method: HTTP method, either GET or POST.
        path: Relative path appended to the base URL, e.g. "/users" or "/search".
        params: Optional query parameters sent as URL query string.
        body: Optional JSON body for POST requests.
    """
    base_url = os.getenv("API_BASE_URL", "").rstrip("/")
    if not base_url:
        return "Error: API_BASE_URL environment variable is not set."

    token = os.getenv("API_BEARER_TOKEN", "")
    headers: dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{base_url}/{path.lstrip('/')}"

    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=params) as resp:
                    return await _parse_response(resp)
            else:
                async with session.post(
                    url, headers=headers, params=params, json=body
                ) as resp:
                    return await _parse_response(resp)
    except aiohttp.ClientError as exc:
        return f"Request failed: {exc}"
    except TimeoutError:
        return f"Request timed out after {_TIMEOUT.total}s"


async def _parse_response(resp: aiohttp.ClientResponse) -> str:
    if resp.status >= 400:
        text = await resp.text()
        return f"HTTP {resp.status}: {text[:500]}"

    content_type = resp.content_type or ""
    if "json" in content_type:
        data = await resp.json()
        return json.dumps(data, ensure_ascii=False, indent=2)

    return await resp.text()
