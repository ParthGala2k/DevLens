"""Smoke test for the event bus (the one foundational piece implemented in the skeleton)."""

import asyncio

import pytest

from app.events.bus import EventBus


@pytest.mark.asyncio
async def test_publish_reaches_subscriber():
    eb = EventBus()
    received = []

    async def consume():
        async for event in eb.subscribe("mcp_log"):
            received.append(event)
            break

    task = asyncio.create_task(consume())
    await asyncio.sleep(0)  # let the subscriber register
    await eb.publish("mcp_log", {"action": "sync_connector", "status": "success"})
    await asyncio.wait_for(task, timeout=1)

    assert received == [{"action": "sync_connector", "status": "success"}]
