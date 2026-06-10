-- Derived view: estimation accuracy per developer per sprint.
-- Developer is extracted from the _Persona: Name (Role)_ tag in the Jira description.
-- Sprint is inferred from the issue key range (SLS-28–36 = Sprint 1, etc.).
-- estimated_points = total story points assigned to the developer in that sprint.
-- completed_points = story points for issues in "Done" status (status 10005).
-- accuracy_ratio   = completed / estimated (1.0 = perfect, <1 = under-delivered).
-- Source: Fivetran jira.issue + jira.issue_field_history

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.estimation_accuracy` AS
WITH story_points AS (
  SELECT
    issue_id,
    CAST(value AS FLOAT64) AS points
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue_field_history`
  WHERE field_id = 'customfield_10016'
    AND is_active = TRUE
    AND value IS NOT NULL
),
issues_enriched AS (
  SELECT
    i.key,
    i.id,
    i.status,
    -- Developer from description persona tag, not the (empty) Jira assignee field
    REGEXP_EXTRACT(i.description, r'_Persona:\s+(\w+)')               AS developer,
    sp.points                                                           AS estimate,
    -- Sprint inferred from issue key number
    CASE
      WHEN CAST(REGEXP_EXTRACT(i.key, r'SLS-(\d+)') AS INT64) BETWEEN 28 AND 36
        THEN 'SLS Sprint 1'
      WHEN CAST(REGEXP_EXTRACT(i.key, r'SLS-(\d+)') AS INT64) BETWEEN 37 AND 46
        THEN 'SLS Sprint 2'
      ELSE 'SLS Sprint 3'
    END                                                                 AS sprint
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue` AS i
  JOIN story_points AS sp ON sp.issue_id = i.id
  WHERE (i._fivetran_deleted IS FALSE OR i._fivetran_deleted IS NULL)
)
SELECT
  sprint,
  developer,
  SUM(estimate)                                                         AS estimated_points,
  SUM(CASE WHEN status = 10005 THEN estimate ELSE 0 END)               AS completed_points,
  SAFE_DIVIDE(
    SUM(CASE WHEN status = 10005 THEN estimate ELSE 0 END),
    NULLIF(SUM(estimate), 0)
  )                                                                     AS accuracy_ratio
FROM issues_enriched
WHERE developer IS NOT NULL
GROUP BY sprint, developer
ORDER BY sprint, developer;
