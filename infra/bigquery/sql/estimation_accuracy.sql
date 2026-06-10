-- Derived view: ticket estimation accuracy.
-- Story points (customfield_10016) vs actual time spent per resolved issue.
-- time_spent is stored in seconds by Jira; converted to hours here.
-- Developer identity resolved from Jira assignee via developer_identity.
-- Source: Fivetran jira.issue + jira.issue_field_history + devlens_metrics.developer_identity

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.estimation_accuracy` AS
WITH story_points AS (
  SELECT
    issue_id,
    CAST(value AS FLOAT64) AS points
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue_field_history`
  WHERE field_id = 'customfield_10016'
    AND is_active = TRUE
    AND value IS NOT NULL
)
SELECT
  i.key                                                          AS issue_key,
  COALESCE(di.canonical_name, i.assignee)                       AS developer,
  sp.points                                                      AS estimate,
  SAFE_DIVIDE(i.time_spent, 3600.0)                             AS actual_hours,
  SAFE_DIVIDE(
    SAFE_DIVIDE(i.time_spent, 3600.0),
    NULLIF(sp.points, 0)
  )                                                              AS ratio
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i
JOIN story_points AS sp ON sp.issue_id = i.id
LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS di
  ON di.id_type = 'jira_user_id' AND di.source_id = i.assignee
WHERE i.resolution IS NOT NULL
  AND (i._fivetran_deleted IS FALSE OR i._fivetran_deleted IS NULL);
