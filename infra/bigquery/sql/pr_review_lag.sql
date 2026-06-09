-- Derived view: pull-request review lag.
-- Which GitHub PRs are stuck, how long they've waited, and who the bottleneck reviewer is.
-- Source: Fivetran-synced GitHub tables (pull_request, pull_request_review).
--
-- TODO: replace placeholder column/table names with the actual Fivetran GitHub schema.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.pr_review_lag` AS
SELECT
  pr.number            AS pr_number,
  pr.title             AS title,
  pr.user_login        AS author,
  pr.created_at        AS opened_at,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), pr.created_at, HOUR) / 24.0 AS days_open,
  -- TODO: first_review_at, requested_reviewer, is_blocked
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.pull_request` AS pr
WHERE pr.state = 'open';
