-- Deployed view: actionable_threads
-- Synced from BigQuery on 2026-06-11.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.actionable_threads` AS
SELECT
  '${BIGQUERY_DATASET_JIRA}'                                                                   AS source,
  i.key                                                                    AS thread_id,
  CONCAT('https://sjsu-team-devlens.atlassian.net/browse/', i.key)        AS permalink,
  c.body                                                                   AS text,
  c.created                                                                AS created_at
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.comment` AS c
JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i ON i.id = c.issue_id
WHERE c.created >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND (
    LOWER(c.body) LIKE '%we should%'
    OR LOWER(c.body) LIKE '%bug%'
    OR LOWER(c.body) LIKE '%todo%'
    OR LOWER(c.body) LIKE '%can someone%'
    OR LOWER(c.body) LIKE '%need to%'
    OR LOWER(c.body) LIKE '%should be%'
    OR LOWER(c.body) LIKE '%missing%'
    OR LOWER(c.body) LIKE '%broken%'
    OR LOWER(c.body) LIKE '%fix%'
    OR LOWER(c.body) LIKE '%issue%'
  )
;
