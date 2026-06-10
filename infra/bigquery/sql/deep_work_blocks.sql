-- Derived view: meeting hours vs estimated deep-work hours per developer per day.
-- "Deep work" is approximated as 8h workday minus confirmed meeting time (floored at 0).
-- Developer identity resolved from calendar email via developer_identity.
-- start_date_time / end_date_time are RFC 3339 strings from the Fivetran Google Calendar connector.
-- Source: Fivetran google_calendar.event + google_calendar.attendee + devlens_metrics.developer_identity

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.deep_work_blocks` AS
WITH meetings AS (
  SELECT
    COALESCE(di.canonical_name, a.email)                                              AS developer,
    DATE(
      SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%S%Ez', e.start_date_time)
    )                                                                                  AS day,
    SUM(
      TIMESTAMP_DIFF(
        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%S%Ez', e.end_date_time),
        SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%S%Ez', e.start_date_time),
        MINUTE
      )
    )                                                                                  AS meeting_minutes
  FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_CALENDAR}.event` AS e
  JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_CALENDAR}.attendee` AS a ON a.event_id = e.id
  LEFT JOIN `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS di
    ON di.id_type = 'calendar_email' AND di.source_id = a.email
  WHERE e.status = 'confirmed'
    AND e.start_date_time IS NOT NULL
    AND e.end_date_time IS NOT NULL
    AND (e._fivetran_deleted IS FALSE OR e._fivetran_deleted IS NULL)
    AND (a._fivetran_deleted IS FALSE OR a._fivetran_deleted IS NULL)
    AND a.response_status IN ('accepted', 'tentative')
  GROUP BY developer, day
)
SELECT
  day,
  developer,
  ROUND(meeting_minutes / 60.0, 2)                        AS meeting_hours,
  ROUND(GREATEST(0, 480 - meeting_minutes) / 60.0, 2)    AS deep_work_hours
FROM meetings
WHERE day IS NOT NULL
ORDER BY day DESC, developer;
