-- Derived view: per-developer completion reliability (observability).
-- Who consistently completes assigned work vs who lags, plus average cycle time
-- and on-time delivery. The raw Jira `resolved` column is NULL on every issue,
-- so completion + cycle time are sourced from story_time's backdated timeline.
-- on_time = a Done issue resolved on/before its sprint end date.
-- Source: devlens_metrics.story_time

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.completion_reliability` AS
SELECT
  persona                                                                AS developer,
  COUNT(*)                                                               AS assigned,
  COUNTIF(status = 'Done')                                               AS completed,
  SAFE_DIVIDE(COUNTIF(status = 'Done'), COUNT(*))                        AS completion_ratio,
  AVG(
    CASE WHEN status = 'Done' AND jira_resolved IS NOT NULL
         THEN TIMESTAMP_DIFF(jira_resolved, jira_created, HOUR) / 24.0
    END
  )                                                                       AS avg_cycle_time_days,
  SAFE_DIVIDE(
    COUNTIF(status = 'Done'
            AND jira_resolved IS NOT NULL
            AND jira_resolved <= TIMESTAMP(DATETIME(sprint_end, TIME '23:59:59'))),
    NULLIF(COUNTIF(status = 'Done'), 0)
  )                                                                       AS on_time_ratio,
  0                                                                       AS churn
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time`
GROUP BY persona
ORDER BY completion_ratio DESC;
