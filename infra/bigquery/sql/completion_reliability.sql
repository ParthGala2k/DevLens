-- Deployed view: completion_reliability
-- Synced from BigQuery on 2026-06-11.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.completion_reliability` AS
SELECT
  persona                                                                AS developer,
  COUNT(*)                                                               AS assigned,
  COUNTIF(status = 'Done')                                               AS completed,
  SAFE_DIVIDE(COUNTIF(status = 'Done'), COUNT(*))                        AS completion_ratio,
  AVG(
    CASE WHEN status = 'Done' AND ${BIGQUERY_DATASET_JIRA}_resolved IS NOT NULL
         THEN TIMESTAMP_DIFF(${BIGQUERY_DATASET_JIRA}_resolved, ${BIGQUERY_DATASET_JIRA}_created, HOUR) / 24.0
    END
  )                                                                       AS avg_cycle_time_days,
  SAFE_DIVIDE(
    COUNTIF(status = 'Done'
            AND ${BIGQUERY_DATASET_JIRA}_resolved IS NOT NULL
            AND ${BIGQUERY_DATASET_JIRA}_resolved <= TIMESTAMP(DATETIME(sprint_end, TIME '23:59:59'))),
    NULLIF(COUNTIF(status = 'Done'), 0)
  )                                                                       AS on_time_ratio,
  0                                                                       AS churn
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time`
GROUP BY persona
ORDER BY completion_ratio DESC
;
