"""Developer observability: load + completion reliability (over BigQuery).

- load(): per-dev load score from `developer_load` view — open assigned issues + story points in
  flight + MRs awaiting their review + on-call status + meeting hours. Powers the Workload Heatmap
  and the bridge's assignee suggestion.
- reliability(): per-dev, per-sprint completion metrics from `completion_reliability` view —
  assigned-vs-completed ratio, cycle time, on-time %, churn. Powers the Reliability Table.
- least_loaded(candidates): helper used by BridgeService to balance new work.
"""


class WorkloadService:
    """TODO: load(), reliability(), least_loaded(candidates)."""
