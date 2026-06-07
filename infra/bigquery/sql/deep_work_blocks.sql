-- Derived view: deep work vs meeting fragmentation per day of week.
-- Source: Fivetran-synced Google Calendar events.
--
-- TODO: replace placeholder column/table names with the actual Fivetran Calendar schema.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.deep_work_blocks` AS
SELECT
  DATE(e.start_time)                                   AS day,
  FORMAT_DATE('%A', DATE(e.start_time))                AS weekday,
  COUNT(*)                                             AS meeting_count,
  SUM(TIMESTAMP_DIFF(e.end_time, e.start_time, MINUTE)) AS meeting_minutes
  -- TODO: compute longest uninterrupted free block as the "deep work" signal
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_CALENDAR}.event` AS e
GROUP BY day, weekday;
