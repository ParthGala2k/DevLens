"""Proactive alert generation + persistence.

Combines rule-based scans (thresholds on metrics) with agent synthesis to produce
human-readable alerts, persists them to Firestore `alerts`, and publishes new ones to the
event bus "alerts" channel. Driven by jobs/alert_scanner.py.
"""


class AlertsService:
    """TODO: scan(), list(), create(alert) -> persist + publish."""
