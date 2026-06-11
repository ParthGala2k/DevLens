-- Deployed view: pr_review_lag
-- Synced from BigQuery on 2026-06-11.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.pr_review_lag` AS
SELECT
  st.pr_number                                                          AS pr_number,
  i.title                                                               AS title,
  st.persona                                                            AS author,
  st.pr_opened                                                          AS opened_at,
  TIMESTAMP_DIFF(TIMESTAMP '2025-06-11 09:00:00-07:00', st.pr_opened, HOUR) / 24.0
                                                                        AS days_open
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time` AS st
LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.issue` AS i
  ON i.number = st.pr_number AND i.pull_request = TRUE
WHERE st.pr_number IS NOT NULL
  AND st.pr_merged IS NULL          -- still open / awaiting review
ORDER BY days_open DESC
;
