"""Alert domain model. Mirror shared/contracts/alert.json."""

from pydantic import BaseModel


class Alert(BaseModel):
    id: str
    severity: str           # info | warning | critical
    title: str
    detail: str
    source: str             # github | jira | slack | calendar | pagerduty | cross
    evidence: list[dict] = []
    created_at: str
