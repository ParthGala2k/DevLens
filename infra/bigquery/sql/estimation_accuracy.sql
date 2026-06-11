-- Derived view: estimation accuracy per developer per sprint.
-- estimated_points = story points the developer took into the sprint.
-- completed_points = points for issues that reached "Done".
-- accuracy_ratio   = completed / estimated (1.0 = delivered everything committed).
-- Sourced from story_time so sprint membership, persona, points and status are
-- consistent with every other view (incl. the SLS-46 OAuth carryover into S3).
-- Source: devlens_metrics.story_time

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.estimation_accuracy` AS
SELECT
  sprint,
  persona                                                          AS developer,
  SUM(points)                                                      AS estimated_points,
  SUM(IF(status = 'Done', points, 0))                             AS completed_points,
  SAFE_DIVIDE(SUM(IF(status = 'Done', points, 0)), NULLIF(SUM(points), 0))
                                                                   AS accuracy_ratio
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time`
GROUP BY sprint, developer
ORDER BY sprint, developer;
