-- Derived view: per-developer, per-sprint completion reliability (observability).
-- Who consistently completes what's assigned vs who lags.
-- Source: Fivetran-synced Jira issues + (optionally) GitHub PR merge data.
--
-- TODO: replace placeholder column/table names; refine on-time + churn definitions.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.completion_reliability` AS
SELECT
  i.assignee                                          AS developer,
  i.sprint                                            AS sprint,
  COUNT(*)                                            AS assigned,
  COUNTIF(i.resolution IS NOT NULL)                   AS completed,
  SAFE_DIVIDE(COUNTIF(i.resolution IS NOT NULL), COUNT(*)) AS completion_ratio,
  AVG(TIMESTAMP_DIFF(i.resolved_at, i.created_at, HOUR) / 24.0) AS avg_cycle_time_days,
  SAFE_DIVIDE(COUNTIF(i.resolved_at <= i.due_date), COUNT(*))   AS on_time_ratio,
  -- TODO: churn = reopened / re-estimated count
  0                                                   AS churn
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i
GROUP BY developer, sprint;
