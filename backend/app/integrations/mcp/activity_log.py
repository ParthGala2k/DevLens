"""MCP activity tap — the single point that makes every MCP call judge-visible.

Wrap any MCP call with `tap()` as a context manager. Works for BOTH servers
(Fivetran sync + GitHub action). Publishes structured events to the event bus
"mcp_log" channel and keeps a small ring buffer for initial render.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from app.events.bus import bus

log = logging.getLogger(__name__)

_RING: list[dict] = []
_RING_SIZE = 100


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _push(event: dict) -> None:
    _RING.append(event)
    if len(_RING) > _RING_SIZE:
        _RING.pop(0)


def recent_calls(n: int = 50) -> list[dict]:
    return list(_RING[-n:])


@asynccontextmanager
async def tap(action: str, server: str, connector: str | None = None, payload: dict | None = None):
    """Async context manager that emits start + success/error MCP events.

    Args:
        action: MCP tool name (e.g. "sync_connector", "create_issue").
        server: "fivetran" or "github".
        connector: optional data source name (github/jira/slack/calendar/pagerduty).
        payload: optional extra context to include in the start event.
    """
    start_event = {
        "server": server,
        "connector": connector,
        "action": action,
        "status": "start",
        "ts": _now(),
        "payload": payload or {},
    }
    _push(start_event)
    try:
        asyncio.get_event_loop().create_task(bus.publish("mcp_log", start_event))
    except RuntimeError:
        pass

    try:
        yield
        done_event = {
            "server": server,
            "connector": connector,
            "action": action,
            "status": "success",
            "ts": _now(),
            "payload": {},
        }
    except Exception as exc:
        done_event = {
            "server": server,
            "connector": connector,
            "action": action,
            "status": "error",
            "ts": _now(),
            "payload": {"error": str(exc)},
        }
        _push(done_event)
        try:
            asyncio.get_event_loop().create_task(bus.publish("mcp_log", done_event))
        except RuntimeError:
            pass
        raise

    _push(done_event)
    try:
        asyncio.get_event_loop().create_task(bus.publish("mcp_log", done_event))
    except RuntimeError:
        pass
