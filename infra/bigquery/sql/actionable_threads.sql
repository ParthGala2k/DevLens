-- Derived view: discussion threads that look like undone work (bridge input).
-- Surfaces recent Slack messages / Jira comments that may imply a task or bug, for the agent to
-- classify and (if actionable) draft into a GitLab issue proposal.
-- Source: Fivetran-synced Slack + Jira.
--
-- TODO: replace placeholder column/table names; this is a coarse pre-filter — the agent does the
--       real actionable/not classification. Optionally pair with VECTOR_SEARCH for dedup.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.actionable_threads` AS
SELECT
  'slack'                                  AS source,
  m.channel_id                             AS thread_id,
  m.permalink                              AS permalink,
  m.text                                   AS text,
  m.ts                                     AS created_at
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_SLACK}.message` AS m
WHERE m.ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND (
    LOWER(m.text) LIKE '%we should%'
    OR LOWER(m.text) LIKE '%bug%'
    OR LOWER(m.text) LIKE '%todo%'
    OR LOWER(m.text) LIKE '%can someone%'
  )

UNION ALL

SELECT
  'jira'                                   AS source,
  c.issue_key                              AS thread_id,
  c.permalink                              AS permalink,
  c.body                                   AS text,
  c.created_at                             AS created_at
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.comment` AS c
WHERE c.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY);
