"""Developer observability domain models. Mirror shared/contracts/workload.json."""

from pydantic import BaseModel


class DeveloperLoad(BaseModel):
    developer: str
    open_issues: int = 0
    story_points_in_flight: float = 0.0
    prs_awaiting_review: int = 0
    on_call: bool = False
    meeting_hours: float = 0.0
    load_score: float = 0.0


class DeveloperReliability(BaseModel):
    developer: str
    sprint: str
    assigned: int = 0
    completed: int = 0
    completion_ratio: float = 0.0
    avg_cycle_time_days: float = 0.0
    on_time_ratio: float = 0.0
    churn: int = 0
