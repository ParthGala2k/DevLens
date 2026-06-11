-- Derived view: per-developer load score (observability).
-- Composite of open (not-Done) assigned Jira issues + story points in flight +
-- open PRs awaiting review. Attribution + timeline come from story_time, which
-- keys on the SLS number and the `_Persona` tag (Jira assignee is empty and the
-- raw GitHub author is a single account, so we override both there).
-- Source: devlens_metrics.story_time

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_load` AS
SELECT
  persona                                                       AS developer,
  COUNTIF(status != 'Done')                                     AS open_issues,
  IFNULL(SUM(IF(status != 'Done', points, 0)), 0)              AS story_points_in_flight,
  COUNTIF(pr_number IS NOT NULL AND pr_merged IS NULL)         AS prs_awaiting_review,
  COUNTIF(status != 'Done')
    + IFNULL(SUM(IF(status != 'Done', points, 0)), 0) * 0.5
    + COUNTIF(pr_number IS NOT NULL AND pr_merged IS NULL)     AS load_score
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time`
GROUP BY persona
ORDER BY load_score DESC;
