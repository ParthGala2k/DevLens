"""Metric domain models for the Sprint Health Dashboard."""

from pydantic import BaseModel


class PrReviewLagRow(BaseModel):
    pr_number: int
    title: str
    author: str
    opened_at: str
    days_open: float


class DeepWorkDay(BaseModel):
    date: str
    developer: str
    deep_work_hours: float
    meeting_hours: float


class EstimationAccuracyRow(BaseModel):
    sprint: str
    developer: str
    estimated_points: float
    completed_points: float
    accuracy_ratio: float
