"""Connector domain model (GitHub / Jira / Calendar sync status)."""

from pydantic import BaseModel


class Connector(BaseModel):
    id: str                     # github | jira | calendar
    status: str                 # connected | syncing | error | unknown
    last_sync_at: str | None = None
    row_count: int | None = None
