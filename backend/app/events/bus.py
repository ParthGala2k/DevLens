"""In-process event bus — fans out to SSE channels (chat, alerts, bridge, mcp_log).

One bus instance per process; SSE route handlers subscribe and yield events to clients.
The ring buffer lets initial render show recent events without needing Firestore.
"""

import asyncio
from collections import defaultdict
from typing import Any, AsyncIterator


class EventBus:
    def __init__(self, ring_size: int = 50) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._ring: dict[str, list[dict]] = defaultdict(list)
        self._ring_size = ring_size

    async def publish(self, channel: str, event: Any) -> None:
        buf = self._ring[channel]
        buf.append(event)
        if len(buf) > self._ring_size:
            buf.pop(0)
        for q in list(self._queues[channel]):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass

    def recent(self, channel: str, n: int = 50) -> list:
        return list(self._ring[channel][-n:])

    async def subscribe(self, channel: str) -> AsyncIterator[Any]:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._queues[channel].append(q)
        try:
            while True:
                yield await q.get()
        finally:
            if q in self._queues[channel]:
                self._queues[channel].remove(q)


# Process-wide singleton (fine for a single Cloud Run instance / the demo).
bus = EventBus()
