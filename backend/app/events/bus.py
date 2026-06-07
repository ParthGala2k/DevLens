"""In-process async pub/sub event bus.

Backs the three SSE streams (chat, alerts, mcp_log). Producers (agent runner, alert scanner,
MCP activity tap) publish to a named channel; SSE endpoints subscribe and fan events out to
connected clients.

This is a minimal working implementation using per-subscriber asyncio queues; for multi-instance
deployments swap for Pub/Sub or Redis behind the same interface.
"""

import asyncio
from collections import defaultdict
from typing import Any, AsyncIterator


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)

    async def publish(self, channel: str, event: Any) -> None:
        for q in list(self._subscribers.get(channel, ())):
            await q.put(event)

    async def subscribe(self, channel: str) -> AsyncIterator[Any]:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers[channel].add(q)
        try:
            while True:
                yield await q.get()
        finally:
            self._subscribers[channel].discard(q)


# Process-wide singleton (fine for a single Cloud Run instance / the demo).
bus = EventBus()
