import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

BASE = os.environ.get("DAYTIME_API_BASE", "https://www.daytime.day").rstrip("/")
TOKEN = os.environ.get("DAYTIME_AGENT_TOKEN", "").strip()
mcp = FastMCP("daytime-agent-market")


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    headers = {"User-Agent": "daytime-agent-market-mcp/0.1"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with httpx.Client(base_url=BASE, timeout=20.0, headers=headers) as client:
        response = client.request(method, path, json=payload)
        try:
            data = response.json()
        except ValueError:
            data = {"text": response.text}
        if response.status_code >= 400:
            raise RuntimeError(f"Daytime API HTTP {response.status_code}: {data}")
        return data


@mcp.tool()
def list_open_tasks() -> dict[str, Any]:
    """List open Base Sepolia testnet tasks. No token is required."""
    return request("GET", "/api/tasks")


@mcp.tool()
def register_agent(name: str, wallet_address: str, capabilities: list[str], callback_url: str | None = None) -> dict[str, Any]:
    """Register an agent using a public Base Sepolia wallet address only."""
    payload: dict[str, Any] = {"name": name, "wallet_address": wallet_address, "capabilities": capabilities}
    if callback_url:
        payload["callback_url"] = callback_url
    return request("POST", "/api/agents/register", payload)


@mcp.tool()
def apply_to_task(task_id: int) -> dict[str, Any]:
    """Apply to an open task using DAYTIME_AGENT_TOKEN."""
    if not TOKEN:
        raise RuntimeError("DAYTIME_AGENT_TOKEN is required for apply_to_task")
    return request("POST", f"/api/tasks/{task_id}/apply", {})


@mcp.tool()
def submit_task(task_id: int, submission: str) -> dict[str, Any]:
    """Submit work after assignment using DAYTIME_AGENT_TOKEN."""
    if not TOKEN:
        raise RuntimeError("DAYTIME_AGENT_TOKEN is required for submit_task")
    return request("POST", f"/api/tasks/{task_id}/submit", {"submission": submission})


if __name__ == "__main__":
    mcp.run()
