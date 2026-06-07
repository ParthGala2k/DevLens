-- Derived view: ticket estimation accuracy per sprint.
-- How often tickets are over/underestimated (estimate vs actual time spent).
-- Source: Fivetran-synced Jira issues + changelog/worklog.
--
-- TODO: replace placeholder column/table names with the actual Fivetran Jira schema.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.estimation_accuracy` AS
SELECT
  i.sprint           AS sprint,
  i.issue_key        AS issue_key,
  i.story_points     AS estimate,
  i.time_spent_hours AS actual_hours,
  SAFE_DIVIDE(i.time_spent_hours, NULLIF(i.story_points, 0)) AS ratio
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i
WHERE i.resolution IS NOT NULL;
