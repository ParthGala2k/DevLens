"""Connector domain model (GitHub / Jira / Slack / Calendar / PagerDuty sync status)."""

from pydantic import BaseModel


class Connector(BaseModel):
    id: str                     # github | jira | slack | calendar | pagerduty
    status: str                 # connected | syncing | error | unknown
    last_sync_at: str | None = None
    row_count: int | None = None
