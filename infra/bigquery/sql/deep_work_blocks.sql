-- Deployed view: deep_work_blocks
-- Synced from BigQuery on 2026-06-11.

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
ORDER BY day DESC, developer
;
