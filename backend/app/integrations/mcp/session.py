"""Generic MCP HTTP client (Streamable HTTP transport, JSON-RPC 2.0).

Sends requests to an MCP server endpoint and parses both plain-JSON and
text/event-stream responses (MCP spec §3.1).
"""

import json
import logging
from dataclasses import dataclass, field

import httpx

log = logging.getLogger(__name__)


@dataclass
class McpSession:
    url: str
    headers: dict = field(default_factory=dict)
    timeout: float = 30.0
    _session_id: str | None = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)
    _req_id: int = field(default=0, init=False)

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _build_headers(self) -> dict:
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **self.headers,
        }
        if self._session_id:
            h["Mcp-Session-Id"] = self._session_id
        return h

    async def _post(self, method: str, params: dict | None = None) -> dict:
        body = {"jsonrpc": "2.0", "id": self._next_id(), "method": method}
        if params is not None:
            body["params"] = params

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.url, json=body, headers=self._build_headers())

        if sid := resp.headers.get("Mcp-Session-Id"):
            self._session_id = sid

        ct = resp.headers.get("content-type", "")

        if resp.status_code == 401:
            raise PermissionError(f"MCP auth failed: {resp.text}")
        if resp.status_code >= 400:
            raise RuntimeError(f"MCP error {resp.status_code}: {resp.text}")

        if "text/event-stream" in ct:
            return self._parse_sse(resp.text)

        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"MCP error: {data['error']}")
        return data.get("result") or {}

    @staticmethod
    def _parse_sse(text: str) -> dict:
        for line in text.splitlines():
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                data = json.loads(payload)
                if "error" in data:
                    raise RuntimeError(f"MCP SSE error: {data['error']}")
                if "result" in data:
                    return data["result"]
            except json.JSONDecodeError:
                continue
        return {}

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self._post("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "devlens", "version": "0.1.0"},
        })
        self._initialized = True

    async def list_tools(self) -> list[dict]:
        await self.initialize()
        result = await self._post("tools/list", {})
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: dict) -> dict:
        await self.initialize()
        result = await self._post("tools/call", {"name": name, "arguments": arguments})
        if isinstance(result, dict) and "content" in result:
            parts = result["content"]
            if isinstance(parts, list) and parts:
                first = parts[0]
                if isinstance(first, dict) and first.get("type") == "text":
                    try:
                        return json.loads(first["text"])
                    except (json.JSONDecodeError, KeyError):
                        return {"text": first.get("text", "")}
        return result if isinstance(result, dict) else {"result": result}
