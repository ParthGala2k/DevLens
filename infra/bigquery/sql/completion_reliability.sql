-- Derived view: per-developer completion reliability (observability).
-- Who consistently completes assigned work vs who lags.
-- Developer identity resolved from Jira assignee (user ID) via developer_identity.
-- Source: Fivetran jira.issue + devlens_metrics.developer_identity

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.completion_reliability` AS
SELECT
  COALESCE(di.canonical_name, i.assignee)                                         AS developer,
  COUNT(*)                                                                          AS assigned,
  COUNTIF(i.resolution IS NOT NULL)                                                AS completed,
  SAFE_DIVIDE(COUNTIF(i.resolution IS NOT NULL), COUNT(*))                         AS completion_ratio,
  AVG(
    CASE WHEN i.resolved IS NOT NULL
         THEN TIMESTAMP_DIFF(i.resolved, i.created, HOUR) / 24.0
    END
  )                                                                                 AS avg_cycle_time_days,
  SAFE_DIVIDE(
    COUNTIF(i.resolved IS NOT NULL
            AND i.due_date IS NOT NULL
            AND i.resolved <= TIMESTAMP(i.due_date)),
    COUNTIF(i.due_date IS NOT NULL)
  )                                                                                 AS on_time_ratio,
  0                                                                                 AS churn
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i
LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS di
  ON di.id_type = 'jira_user_id' AND di.source_id = i.assignee
WHERE i.assignee IS NOT NULL
  AND (i._fivetran_deleted IS FALSE OR i._fivetran_deleted IS NULL)
GROUP BY developer;
