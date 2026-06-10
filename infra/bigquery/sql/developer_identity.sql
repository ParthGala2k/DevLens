-- Canonical developer identity mapping across GitHub, Jira, and Calendar.
-- Maps source-specific IDs to the four canonical team member names.
-- Add new rows here as team membership changes; views JOIN against this.

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.developer_identity` AS
SELECT 'github_login'  AS id_type, 'itsRenuka22'                                    AS source_id, 'Riya'  AS canonical_name UNION ALL
SELECT 'github_login',              'MrunalKotkar',                                                'Arjun'                   UNION ALL
SELECT 'github_login',              'devpateltech007',                                             'James'                   UNION ALL
SELECT 'jira_user_id',              '712020:18a79bec-2247-45d7-9ebd-b6cc8cde57b3',               'Riya'                    UNION ALL
SELECT 'calendar_email',            'devaug2002@gmail.com',                                        'James'                   UNION ALL
SELECT 'calendar_email',            'corporate@rtsgp.com',                                         'Priya'                   ;
