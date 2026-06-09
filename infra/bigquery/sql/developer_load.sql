-- Derived view: per-developer load score (observability).
-- Composite of open assigned issues + story points in flight + MRs awaiting their review +
-- on-call status + meeting hours. Powers the Workload Heatmap and the bridge's assignee suggestion.
--
-- TODO: replace placeholder column/table names; tune the load_score weighting.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.developer_load` AS
WITH open_issues AS (
  SELECT assignee AS developer, COUNT(*) AS open_issues,
         SUM(story_points) AS story_points_in_flight
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_JIRA}.issue`
  WHERE resolution IS NULL
  GROUP BY developer
),
review_queue AS (
  SELECT requested_reviewer AS developer, COUNT(*) AS prs_awaiting_review
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_GITHUB}.pull_request`
  WHERE state = 'open'
  GROUP BY developer
)
SELECT
  COALESCE(oi.developer, rq.developer) AS developer,
  IFNULL(oi.open_issues, 0)            AS open_issues,
  IFNULL(oi.story_points_in_flight, 0) AS story_points_in_flight,
  IFNULL(rq.prs_awaiting_review, 0)    AS prs_awaiting_review,
  -- TODO: join on-call (pagerduty) + meeting_hours (calendar)
  FALSE                                AS on_call,
  0.0                                  AS meeting_hours,
  -- Simple composite; tune weights later.
  IFNULL(oi.open_issues, 0)
    + IFNULL(oi.story_points_in_flight, 0)
    + IFNULL(rq.prs_awaiting_review, 0) AS load_score
FROM open_issues oi
FULL OUTER JOIN review_queue rq USING (developer);
