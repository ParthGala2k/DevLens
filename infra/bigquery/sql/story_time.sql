-- Authoritative "story time" override for the demo.
--
-- WHY THIS EXISTS: GitHub server-stamps PR/issue/comment timestamps and Jira
-- server-stamps `created`/`resolved` at creation, so every PR (21) and Jira
-- issue (27) synced by Fivetran is dated "today" and Jira `resolved` is NULL on
-- all of them. Only git commit dates and the Jira sprint records carry real
-- historical dates. This view supplies the intended backdated timeline so the
-- derived metric views read a realistic May–Jun 2025 sprint history. It is the
-- single source of truth that downstream views COALESCE over the raw columns;
-- it survives Fivetran re-syncs because it never touches the raw tables.
--
-- ATTRIBUTION: Jira `assignee` is empty in the synced data; persona lives in the
-- `_Persona: Name` description tag. PRs map 1:1 to Jira keys via the `[SLS-XX]`
-- title prefix. So we key everything on the SLS number and attribute by persona
-- here, which also fixes (a) only-Riya-mapped on the Jira side and (b) every PR
-- showing a single GitHub author (itsRenuka22).
--
-- TIMELINE / NARRATIVE BEATS encoded below:
--   Sprint 1 = May 1–14, Sprint 2 = May 15–28, Sprint 3 = May 29–Jun 12 (2025).
--   * Riya is on-call: incidents May 20–21 and May 26 delay her reviews.
--   * SLS-41 (James) review slips to May 22 behind Riya's May 20–21 incident.
--   * SLS-43 (Arjun, OAuth) stuck In Review; SLS-46 (Arjun) carries into S3,
--     blocked on Riya — both stay open with long review lag.
--   * Priya's cycle times run long (Tue/Wed meeting overload).
--   * James is junior but reliable; cycle time improves S1 → S3.
-- All timestamps are America/Los_Angeles (PDT, -07:00).

CREATE OR REPLACE VIEW `${BIGQUERY_PROJECT}.${BIGQUERY_DATASET_METRICS}.story_time` AS
SELECT * FROM UNNEST([
  STRUCT(
    'SLS-28' AS key, 1 AS pr_number, 'Arjun' AS persona, 'Sprint 1' AS sprint,
    DATE '2025-05-14' AS sprint_end, 3.0 AS points, 'Done' AS status,
    TIMESTAMP '2025-05-01 10:00:00-07:00' AS jira_created,
    TIMESTAMP '2025-05-05 11:30:00-07:00' AS jira_resolved,
    TIMESTAMP '2025-05-02 14:00:00-07:00' AS pr_opened,
    TIMESTAMP '2025-05-05 11:00:00-07:00' AS pr_merged),

  -- ── Sprint 1 (SLS-28–36 / PR 1–9) — all Done ──────────────────────────────
  STRUCT('SLS-29', 2, 'Riya',  'Sprint 1', DATE '2025-05-14', 5.0, 'Done',
    TIMESTAMP '2025-05-01 10:00:00-07:00', TIMESTAMP '2025-05-07 10:30:00-07:00',
    TIMESTAMP '2025-05-05 16:00:00-07:00', TIMESTAMP '2025-05-07 10:00:00-07:00'),
  STRUCT('SLS-30', 3, 'Priya', 'Sprint 1', DATE '2025-05-14', 3.0, 'Done',
    TIMESTAMP '2025-05-01 11:00:00-07:00', TIMESTAMP '2025-05-09 15:30:00-07:00',
    TIMESTAMP '2025-05-06 09:00:00-07:00', TIMESTAMP '2025-05-09 15:00:00-07:00'),
  STRUCT('SLS-31', 4, 'Priya', 'Sprint 1', DATE '2025-05-14', 3.0, 'Done',
    TIMESTAMP '2025-05-02 10:00:00-07:00', TIMESTAMP '2025-05-12 14:30:00-07:00',
    TIMESTAMP '2025-05-08 10:00:00-07:00', TIMESTAMP '2025-05-12 14:00:00-07:00'),
  STRUCT('SLS-32', 5, 'James', 'Sprint 1', DATE '2025-05-14', 2.0, 'Done',
    TIMESTAMP '2025-05-02 11:00:00-07:00', TIMESTAMP '2025-05-12 16:30:00-07:00',
    TIMESTAMP '2025-05-06 13:00:00-07:00', TIMESTAMP '2025-05-12 16:00:00-07:00'),
  STRUCT('SLS-33', 6, 'James', 'Sprint 1', DATE '2025-05-14', 2.0, 'Done',
    TIMESTAMP '2025-05-05 10:00:00-07:00', TIMESTAMP '2025-05-13 11:30:00-07:00',
    TIMESTAMP '2025-05-08 14:00:00-07:00', TIMESTAMP '2025-05-13 11:00:00-07:00'),
  STRUCT('SLS-34', 7, 'Arjun', 'Sprint 1', DATE '2025-05-14', 3.0, 'Done',
    TIMESTAMP '2025-05-05 11:00:00-07:00', TIMESTAMP '2025-05-09 16:30:00-07:00',
    TIMESTAMP '2025-05-07 10:00:00-07:00', TIMESTAMP '2025-05-09 16:00:00-07:00'),
  STRUCT('SLS-35', 8, 'Arjun', 'Sprint 1', DATE '2025-05-14', 2.0, 'Done',
    TIMESTAMP '2025-05-06 10:00:00-07:00', TIMESTAMP '2025-05-12 10:30:00-07:00',
    TIMESTAMP '2025-05-09 11:00:00-07:00', TIMESTAMP '2025-05-12 10:00:00-07:00'),
  STRUCT('SLS-36', 9, 'Riya',  'Sprint 1', DATE '2025-05-14', 5.0, 'Done',
    TIMESTAMP '2025-05-06 10:00:00-07:00', TIMESTAMP '2025-05-13 09:30:00-07:00',
    TIMESTAMP '2025-05-09 15:00:00-07:00', TIMESTAMP '2025-05-13 09:00:00-07:00'),

  -- ── Sprint 2 (SLS-37–45 / PR 10–18) — Done except SLS-43 (Arjun, In Review)
  STRUCT('SLS-37', 10, 'Riya',  'Sprint 2', DATE '2025-05-28', 5.0, 'Done',
    TIMESTAMP '2025-05-15 10:00:00-07:00', TIMESTAMP '2025-05-19 10:30:00-07:00',
    TIMESTAMP '2025-05-16 14:00:00-07:00', TIMESTAMP '2025-05-19 10:00:00-07:00'),
  STRUCT('SLS-38', 11, 'Priya', 'Sprint 2', DATE '2025-05-28', 5.0, 'Done',
    TIMESTAMP '2025-05-15 11:00:00-07:00', TIMESTAMP '2025-05-23 14:30:00-07:00',
    TIMESTAMP '2025-05-19 09:00:00-07:00', TIMESTAMP '2025-05-23 14:00:00-07:00'),
  STRUCT('SLS-39', 12, 'James', 'Sprint 2', DATE '2025-05-28', 3.0, 'Done',
    TIMESTAMP '2025-05-15 11:00:00-07:00', TIMESTAMP '2025-05-22 16:30:00-07:00',
    TIMESTAMP '2025-05-19 13:00:00-07:00', TIMESTAMP '2025-05-22 16:00:00-07:00'),
  STRUCT('SLS-40', 13, 'Riya',  'Sprint 2', DATE '2025-05-28', 8.0, 'Done',
    TIMESTAMP '2025-05-16 10:00:00-07:00', TIMESTAMP '2025-05-23 11:30:00-07:00',
    TIMESTAMP '2025-05-20 15:00:00-07:00', TIMESTAMP '2025-05-23 11:00:00-07:00'),
  -- SLS-41: opened May 19, but reviewer Riya was on-call (incident May 20–21),
  -- so it only merges May 22 → ~3-day review lag (matches the calendar story).
  STRUCT('SLS-41', 14, 'James', 'Sprint 2', DATE '2025-05-28', 3.0, 'Done',
    TIMESTAMP '2025-05-16 11:00:00-07:00', TIMESTAMP '2025-05-22 10:30:00-07:00',
    TIMESTAMP '2025-05-19 11:00:00-07:00', TIMESTAMP '2025-05-22 10:00:00-07:00'),
  STRUCT('SLS-42', 15, 'Arjun', 'Sprint 2', DATE '2025-05-28', 3.0, 'Done',
    TIMESTAMP '2025-05-19 10:00:00-07:00', TIMESTAMP '2025-05-23 15:30:00-07:00',
    TIMESTAMP '2025-05-21 10:00:00-07:00', TIMESTAMP '2025-05-23 15:00:00-07:00'),
  -- SLS-43: OAuth, stuck In Review, PR still open (awaiting Riya).
  STRUCT('SLS-43', 16, 'Arjun', 'Sprint 2', DATE '2025-05-28', 3.0, 'In Review',
    TIMESTAMP '2025-05-20 10:00:00-07:00', CAST(NULL AS TIMESTAMP),
    TIMESTAMP '2025-05-26 14:00:00-07:00', CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-44', 17, 'Priya', 'Sprint 2', DATE '2025-05-28', 3.0, 'Done',
    TIMESTAMP '2025-05-20 11:00:00-07:00', TIMESTAMP '2025-05-27 14:30:00-07:00',
    TIMESTAMP '2025-05-23 10:00:00-07:00', TIMESTAMP '2025-05-27 14:00:00-07:00'),
  STRUCT('SLS-45', 18, 'James', 'Sprint 2', DATE '2025-05-28', 2.0, 'Done',
    TIMESTAMP '2025-05-21 10:00:00-07:00', TIMESTAMP '2025-05-27 11:30:00-07:00',
    TIMESTAMP '2025-05-23 13:00:00-07:00', TIMESTAMP '2025-05-27 11:00:00-07:00'),

  -- ── Sprint 3 (SLS-46–54 / PR 19–21) — active sprint, work in flight ────────
  -- SLS-46: OAuth carryover from S2, still In Progress, blocked on Riya's review.
  STRUCT('SLS-46', 19, 'Arjun', 'Sprint 3', DATE '2025-06-12', 3.0, 'In Progress',
    TIMESTAMP '2025-05-22 10:00:00-07:00', CAST(NULL AS TIMESTAMP),
    TIMESTAMP '2025-05-30 14:00:00-07:00', CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-47', 20, 'Riya',  'Sprint 3', DATE '2025-06-12', 8.0, 'In Progress',
    TIMESTAMP '2025-05-29 10:00:00-07:00', CAST(NULL AS TIMESTAMP),
    TIMESTAMP '2025-06-03 14:00:00-07:00', CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-48', 21, 'Priya', 'Sprint 3', DATE '2025-06-12', 5.0, 'In Progress',
    TIMESTAMP '2025-05-29 11:00:00-07:00', CAST(NULL AS TIMESTAMP),
    TIMESTAMP '2025-06-04 10:00:00-07:00', CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-49', CAST(NULL AS INT64), 'Riya',  'Sprint 3', DATE '2025-06-12', 5.0, 'To Do',
    TIMESTAMP '2025-05-29 10:00:00-07:00', CAST(NULL AS TIMESTAMP),
    CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-50', CAST(NULL AS INT64), 'James', 'Sprint 3', DATE '2025-06-12', 3.0, 'To Do',
    TIMESTAMP '2025-05-29 11:00:00-07:00', CAST(NULL AS TIMESTAMP),
    CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-51', CAST(NULL AS INT64), 'Arjun', 'Sprint 3', DATE '2025-06-12', 5.0, 'To Do',
    TIMESTAMP '2025-05-29 12:00:00-07:00', CAST(NULL AS TIMESTAMP),
    CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-52', CAST(NULL AS INT64), 'Priya', 'Sprint 3', DATE '2025-06-12', 5.0, 'To Do',
    TIMESTAMP '2025-05-30 10:00:00-07:00', CAST(NULL AS TIMESTAMP),
    CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-53', CAST(NULL AS INT64), 'James', 'Sprint 3', DATE '2025-06-12', 3.0, 'To Do',
    TIMESTAMP '2025-05-30 11:00:00-07:00', CAST(NULL AS TIMESTAMP),
    CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP)),
  STRUCT('SLS-54', CAST(NULL AS INT64), 'Arjun', 'Sprint 3', DATE '2025-06-12', 3.0, 'To Do',
    TIMESTAMP '2025-05-30 12:00:00-07:00', CAST(NULL AS TIMESTAMP),
    CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP))
]);
