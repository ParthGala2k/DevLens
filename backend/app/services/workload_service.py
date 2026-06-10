"""Developer observability: load + completion reliability (over BigQuery)."""

import logging

from app.integrations.bigquery_client import bq_client

log = logging.getLogger(__name__)


class WorkloadService:
    def load(self) -> list[dict]:
        return bq_client.query_view("developer_load")

    def reliability(self) -> list[dict]:
        return bq_client.query_view("completion_reliability")

    def least_loaded(self, candidates: list[str] | None = None) -> str | None:
        all_load = self.load()
        if candidates:
            all_load = [r for r in all_load if r.get("developer") in candidates]
        if not all_load:
            return None
        return min(all_load, key=lambda r: r.get("load_score", 999)).get("developer")


workload_service = WorkloadService()
