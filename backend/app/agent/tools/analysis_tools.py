"""ADK helper tools for analysis over fetched rows (pure computation, no I/O)."""


def rank_review_bottlenecks(pr_rows: list[dict]) -> list[dict]:
    """Rank PRs by days open descending — identifies the worst review bottlenecks."""
    return sorted(pr_rows, key=lambda r: r.get("days_open", 0), reverse=True)


def compute_estimation_skew(accuracy_rows: list[dict]) -> list[dict]:
    """Return developers sorted by average estimation skew (|accuracy_ratio - 1|)."""
    by_dev: dict[str, list[float]] = {}
    for r in accuracy_rows:
        dev = r.get("developer", "unknown")
        by_dev.setdefault(dev, []).append(abs(r.get("accuracy_ratio", 1.0) - 1.0))
    return sorted(
        [{"developer": d, "avg_skew": sum(v) / len(v)} for d, v in by_dev.items()],
        key=lambda x: x["avg_skew"],
        reverse=True,
    )


def detect_meeting_overload(deep_work_rows: list[dict], threshold_hours: float = 20.0) -> list[dict]:
    """Return developers whose weekly meeting hours exceed the threshold."""
    by_dev: dict[str, float] = {}
    for r in deep_work_rows:
        dev = r.get("developer", "unknown")
        by_dev[dev] = by_dev.get(dev, 0.0) + r.get("meeting_hours", 0.0)
    return [
        {"developer": d, "total_meeting_hours": h}
        for d, h in by_dev.items()
        if h >= threshold_hours
    ]


TOOLS = [rank_review_bottlenecks, compute_estimation_skew, detect_meeting_overload]
