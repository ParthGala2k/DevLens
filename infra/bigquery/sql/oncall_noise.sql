-- Derived view: on-call noise per service per week.
-- Source: Fivetran-synced PagerDuty incidents.
--
-- TODO: replace placeholder column/table names with the actual Fivetran PagerDuty schema.

CREATE OR REPLACE VIEW `${BIGQUERY_DATASET_METRICS}.oncall_noise` AS
SELECT
  inc.service_name                          AS service,
  DATE_TRUNC(DATE(inc.created_at), WEEK)    AS week,
  COUNT(*)                                  AS incident_count
FROM `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_PAGERDUTY}.incident` AS inc
GROUP BY service, week;
