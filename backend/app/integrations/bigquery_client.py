"""Thin BigQuery client wrapper with graceful degradation.

Returns empty lists when the project/views aren't available yet (pre-Fivetran setup).
All derived views live in settings.bigquery_dataset_metrics.
"""

import logging

log = logging.getLogger(__name__)

try:
    from google.cloud import bigquery as _bq
    _HAS_BQ = True
except ImportError:
    _HAS_BQ = False


class BigQueryClient:
    def __init__(self) -> None:
        self._client = None

    def _get(self):
        if not _HAS_BQ:
            raise RuntimeError("google-cloud-bigquery not installed")
        if self._client is None:
            from app.config import settings
            self._client = _bq.Client(project=settings.bigquery_project)
        return self._client

    def query(self, sql: str) -> list[dict]:
        try:
            client = self._get()
            return [dict(row) for row in client.query(sql).result()]
        except Exception as exc:
            log.warning("BigQuery query failed: %s", exc)
            return []

    def query_view(self, view: str, limit: int = 500) -> list[dict]:
        from app.config import settings
        project = settings.bigquery_project
        dataset = settings.bigquery_dataset_metrics
        return self.query(f"SELECT * FROM `{project}.{dataset}.{view}` LIMIT {limit}")

    def raw_query(self, dataset_attr: str, table: str, limit: int = 500) -> list[dict]:
        """Query a raw Fivetran-synced table (not a derived view)."""
        from app.config import settings
        project = settings.bigquery_project
        dataset = getattr(settings, dataset_attr, "")
        return self.query(f"SELECT * FROM `{project}.{dataset}.{table}` LIMIT {limit}")


bq_client = BigQueryClient()
