"""Thin BigQuery client wrapper.

Owns the google-cloud-bigquery client and exposes a small query() helper that returns rows as
dicts. Higher layers (MetricsService) build queries against the derived views; this module just
executes them.
"""

# from google.cloud import bigquery
# from app.config import settings


class BigQueryClient:
    """TODO: __init__ creates bigquery.Client(project=settings.bigquery_project);
    query(sql, params) -> list[dict]."""
