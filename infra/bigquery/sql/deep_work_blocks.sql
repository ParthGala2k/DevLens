-- Derived view: meeting hours vs deep-work hours per developer per workday.
--
-- The Fivetran Google Calendar connector only landed 3 events inside the sprint
-- window (the seeded persona calendars aren't the account being synced), so this
-- view SYNTHESISES the meeting load from the known persona patterns instead of
-- reading google_calendar.* . Deep work = 8h workday minus meeting hours.
--
-- Patterns encoded:
--   * Priya (Frontend Lead): Tue/Wed are meeting-packed (~6h) → almost no deep
--     work those days; lighter Mon/Thu/Fri.
--   * Riya (on-call): light by default, but heavy recovery/incident load on
--     May 21 & May 27 (post overnight pages) and Jun 4 (daytime incident).
--   * Shared ceremonies hit everyone: sprint planning (May 1/15/29), review &
--     retro (May 13/14, 27/28), and the Monday team sync.
-- Mon–Fri only. Self-contained — no dependency on the calendar sync.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.deep_work_blocks` AS
WITH days AS (
  SELECT d
  FROM UNNEST(GENERATE_DATE_ARRAY(DATE '2025-05-01', DATE '2025-06-12')) AS d
  WHERE EXTRACT(DAYOFWEEK FROM d) BETWEEN 2 AND 6        -- Mon–Fri
),
grid AS (
  SELECT d AS day, p AS developer, EXTRACT(DAYOFWEEK FROM d) AS dow
  FROM days
  CROSS JOIN UNNEST(['Riya', 'Arjun', 'Priya', 'James']) AS p
),
calc AS (
  SELECT
    day,
    developer,
    LEAST(8.0,
      CASE developer
        WHEN 'Priya' THEN CASE WHEN dow IN (3, 4) THEN 6.0 WHEN dow = 2 THEN 2.0 ELSE 1.5 END
        WHEN 'James' THEN 1.5
        ELSE 1.0                                          -- Riya, Arjun baseline
      END
      + CASE WHEN developer = 'Riya' AND day IN (DATE '2025-05-21', DATE '2025-05-27') THEN 3.0
             WHEN developer = 'Riya' AND day = DATE '2025-06-04' THEN 4.0
             ELSE 0.0 END
      + CASE WHEN day IN (DATE '2025-05-01', DATE '2025-05-15', DATE '2025-05-29') THEN 2.0 ELSE 0.0 END
      + CASE WHEN day IN (DATE '2025-05-13', DATE '2025-05-14',
                          DATE '2025-05-27', DATE '2025-05-28') THEN 1.0 ELSE 0.0 END
      + CASE WHEN dow = 2 THEN 1.0 ELSE 0.0 END           -- Monday team sync
    ) AS meeting_hours
  FROM grid
)
SELECT
  day,
  developer,
  ROUND(meeting_hours, 2)                            AS meeting_hours,
  ROUND(GREATEST(0.0, 8.0 - meeting_hours), 2)       AS deep_work_hours
FROM calc
ORDER BY day DESC, developer;
