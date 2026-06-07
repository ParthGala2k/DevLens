"""Sprint-health metrics over BigQuery (PR review lag, deep work, estimation accuracy).

Wraps BigQueryClient and the derived views in infra/bigquery/sql/. Returns domain models
(app/domain/metric.py). Used by dashboard routes and the agent's BigQuery tools.
"""


class MetricsService:
    """TODO: pr_review_lag(), deep_work(), estimation_accuracy(), oncall_noise()."""
