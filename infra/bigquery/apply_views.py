"""Apply BigQuery metric views from infra/bigquery/sql/*.sql.

Reads each .sql file, substitutes ${VAR} placeholders from environment,
then executes via the BigQuery client.

Usage:
    python infra/bigquery/apply_views.py
    python infra/bigquery/apply_views.py pr_review_lag developer_load  # specific views only
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

VARS = {
    "BIGQUERY_PROJECT":          os.environ.get("BIGQUERY_PROJECT", "dev-blindspot-agent"),
    "BIGQUERY_DATASET_METRICS":  os.environ.get("BIGQUERY_DATASET_METRICS", "devlens_metrics"),
    "BIGQUERY_DATASET_GITHUB":   os.environ.get("BIGQUERY_DATASET_GITHUB", "github"),
    "BIGQUERY_DATASET_JIRA":     os.environ.get("BIGQUERY_DATASET_JIRA", "jira"),
    "BIGQUERY_DATASET_CALENDAR": os.environ.get("BIGQUERY_DATASET_CALENDAR", "calendar"),
}

sql_dir = Path(__file__).parent / "sql"
filter_names = set(sys.argv[1:])  # optional: only apply named views

try:
    from google.cloud import bigquery
    client = bigquery.Client(project=VARS["BIGQUERY_PROJECT"])
except Exception as e:
    print(f"ERROR: could not initialise BigQuery client: {e}")
    sys.exit(1)

ok = failed = 0
for sql_file in sorted(sql_dir.glob("*.sql")):
    view_name = sql_file.stem
    if filter_names and view_name not in filter_names:
        continue

    sql = sql_file.read_text()
    for k, v in VARS.items():
        sql = sql.replace(f"${{{k}}}", v)

    print(f"  applying {view_name}...", end=" ", flush=True)
    try:
        client.query(sql).result()
        print("OK")
        ok += 1
    except Exception as e:
        print(f"FAILED\n    {e}")
        failed += 1

print(f"\n{ok} view(s) applied, {failed} failed.")
if failed:
    sys.exit(1)
