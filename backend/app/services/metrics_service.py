"""Sprint-health metrics over BigQuery (PR review lag, deep work, estimation accuracy)."""

import logging

from app.integrations.bigquery_client import bq_client

log = logging.getLogger(__name__)


class MetricsService:
    def pr_review_lag(self) -> list[dict]:
        return bq_client.query_view("pr_review_lag")

    def deep_work(self) -> list[dict]:
        return bq_client.query_view("deep_work_blocks")

    def estimation_accuracy(self) -> list[dict]:
        return bq_client.query_view("estimation_accuracy")


metrics_service = MetricsService()
