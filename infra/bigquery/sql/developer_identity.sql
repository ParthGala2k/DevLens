-- Deployed view: developer_identity
-- Synced from BigQuery on 2026-06-11.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS
SELECT '${BIGQUERY_DATASET_GITHUB}_login'  AS id_type, 'itsRenuka22'                                    AS source_id, 'Riya'  AS canonical_name UNION ALL
SELECT '${BIGQUERY_DATASET_GITHUB}_login',              'MrunalKotkar',                                                'Arjun'                   UNION ALL
SELECT '${BIGQUERY_DATASET_GITHUB}_login',              'devpateltech007',                                             'James'                   UNION ALL
SELECT '${BIGQUERY_DATASET_JIRA}_user_id',              '712020:18a79bec-2247-45d7-9ebd-b6cc8cde57b3',               'Riya'                    UNION ALL
SELECT 'calendar_email',            'devaug2002@gmail.com',                                        'James'                   UNION ALL
SELECT 'calendar_email',            'corporate@rtsgp.com',                                         'Priya'
;
