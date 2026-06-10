-- Derived view: per-developer load score (observability).
-- Composite of open assigned Jira issues + story points in flight + open GitHub PRs.
-- Developer identity resolved via developer_identity mapping view.
-- Source: Fivetran jira.issue + jira.issue_field_history + github.issue + github.pull_request + github.user

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_load` AS
WITH story_points AS (
  SELECT
    issue_id,
    CAST(value AS FLOAT64) AS points
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue_field_history`
  WHERE field_id = 'customfield_10016'
    AND is_active = TRUE
    AND value IS NOT NULL
),
open_issues AS (
  SELECT
    COALESCE(di.canonical_name, i.assignee)  AS developer,
    COUNT(*)                                  AS open_issues,
    IFNULL(SUM(sp.points), 0)               AS story_points_in_flight
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i
  LEFT JOIN story_points AS sp ON sp.issue_id = i.id
  LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS di
    ON di.id_type = 'jira_user_id' AND di.source_id = i.assignee
  WHERE i.resolution IS NULL
    AND (i._fivetran_deleted IS FALSE OR i._fivetran_deleted IS NULL)
    AND i.assignee IS NOT NULL
  GROUP BY developer
),
open_prs AS (
  SELECT
    COALESCE(di.canonical_name, u.login)     AS developer,
    COUNT(*)                                  AS prs_open
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.issue` AS i
  JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.pull_request` AS pr ON pr.issue_id = i.id
  LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.user` AS u ON u.id = i.user_id
  LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS di
    ON di.id_type = 'github_login' AND di.source_id = u.login
  WHERE i.state = 'open'
    AND i.pull_request = TRUE
    AND u.login IS NOT NULL
  GROUP BY developer
)
SELECT
  COALESCE(oi.developer, op.developer)   AS developer,
  IFNULL(oi.open_issues, 0)             AS open_issues,
  IFNULL(oi.story_points_in_flight, 0)  AS story_points_in_flight,
  IFNULL(op.prs_open, 0)               AS prs_awaiting_review,
  IFNULL(oi.open_issues, 0)
    + IFNULL(oi.story_points_in_flight, 0) * 0.5
    + IFNULL(op.prs_open, 0)            AS load_score
FROM open_issues AS oi
FULL OUTER JOIN open_prs AS op ON op.developer = oi.developer;
