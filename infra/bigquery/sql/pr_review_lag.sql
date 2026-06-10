-- Derived view: pull-request review lag.
-- Which GitHub PRs are open, how long they've waited, and who authored them.
-- Author is resolved to a canonical team name via developer_identity.
-- Source: Fivetran github.issue + github.pull_request + github.user + devlens_metrics.developer_identity

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.pr_review_lag` AS
SELECT
  i.number                                                          AS pr_number,
  i.title                                                           AS title,
  COALESCE(di.canonical_name, u.login)                             AS author,
  i.created_at                                                      AS opened_at,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), i.created_at, HOUR) / 24.0   AS days_open
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.issue` AS i
JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.pull_request` AS pr ON pr.issue_id = i.id
LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.user` AS u ON u.id = i.user_id
LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS di
  ON di.id_type = 'github_login' AND di.source_id = u.login
WHERE i.state = 'open'
  AND i.pull_request = TRUE;
