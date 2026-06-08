-- Derived view: merge-request review lag.
-- Which GitLab MRs are stuck, how long they've waited, and who the bottleneck reviewer is.
-- Source: Fivetran-synced GitLab tables (merge_request, approval, note).
--
-- TODO: replace placeholder column/table names with the actual Fivetran GitLab schema.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.mr_review_lag` AS
SELECT
  mr.iid               AS mr_iid,
  mr.title             AS title,
  mr.author            AS author,
  mr.created_at        AS opened_at,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), mr.created_at, HOUR) / 24.0 AS days_open,
  -- TODO: first_review_at, assigned_reviewer, is_blocked
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITLAB}.merge_request` AS mr
WHERE mr.state = 'opened';
