-- Deployed view: estimation_accuracy
-- Synced from BigQuery on 2026-06-11.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.estimation_accuracy` AS
SELECT
  sprint,
  persona                                                          AS developer,
  SUM(points)                                                      AS estimated_points,
  SUM(IF(status = 'Done', points, 0))                             AS completed_points,
  SAFE_DIVIDE(SUM(IF(status = 'Done', points, 0)), NULLIF(SUM(points), 0))
                                                                   AS accuracy_ratio
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time`
GROUP BY sprint, developer
ORDER BY sprint, developer
;
