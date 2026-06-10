-- Derived view: discussion threads that look like undone work (bridge input).
-- Surfaces recent Jira comments that may imply a task or bug, for the agent to
-- classify and (if actionable) draft into a GitHub issue proposal.
-- Slack source is added once the Slack connector is active.
-- Source: Fivetran jira.comment + jira.issue

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.actionable_threads` AS
SELECT
  'jira'                                                                   AS source,
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
  );
