-- Deployed view: developer_load
-- Synced from BigQuery on 2026-06-11.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_load` AS
SELECT
  persona                                                       AS developer,
  COUNTIF(status != 'Done')                                     AS open_issues,
  IFNULL(SUM(IF(status != 'Done', points, 0)), 0)              AS story_points_in_flight,
  COUNTIF(pr_number IS NOT NULL AND pr_merged IS NULL)         AS prs_awaiting_review,
  COUNTIF(status != 'Done')
    + IFNULL(SUM(IF(status != 'Done', points, 0)), 0) * 0.5
    + COUNTIF(pr_number IS NOT NULL AND pr_merged IS NULL)     AS load_score
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time`
GROUP BY persona
ORDER BY load_score DESC
;
