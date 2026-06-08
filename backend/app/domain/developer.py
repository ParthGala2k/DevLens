"""Developer observability domain models. Mirror shared/contracts/workload.json."""

# from pydantic import BaseModel
#
# class DeveloperLoad(BaseModel):
#     developer: str
#     open_issues: int
#     story_points_in_flight: float
#     mrs_awaiting_review: int
#     on_call: bool
#     meeting_hours: float
#     load_score: float           # composite, for the heatmap
#
# class DeveloperReliability(BaseModel):
#     developer: str
#     sprint: str
#     assigned: int
#     completed: int
#     completion_ratio: float
#     avg_cycle_time_days: float
#     on_time_ratio: float
#     churn: int
