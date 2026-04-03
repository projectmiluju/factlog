"""Schemas for dashboard and validation APIs."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class RecentAnalysisItem(BaseModel):
    analysis_result_id: int
    sensor_record_id: int
    equipment_name: str
    timestamp: str
    anomaly_score: float
    is_anomaly: bool
    explanation_source: str
    action_logged: bool


class MetricItem(BaseModel):
    metric_name: str
    metric_value: float


class ValidationDatasetItem(BaseModel):
    dataset_name: str
    subset: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    metrics: List[MetricItem]
    notes: List[str]


class DashboardSummaryResponse(BaseModel):
    total_analyses: int
    total_actions: int
    anomaly_count: int
    accuracy_label: str
    recent_analyses: List[RecentAnalysisItem]
    validation_datasets: List[ValidationDatasetItem]


class ValidationSummaryResponse(BaseModel):
    datasets: List[ValidationDatasetItem]
