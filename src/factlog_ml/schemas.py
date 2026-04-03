"""Typed validation result schemas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DatasetAvailability:
    dataset_name: str
    available: bool
    note: str


@dataclass(frozen=True)
class ValidationSummary:
    dataset_name: str
    subset: str
    anomaly_threshold_cycles: int
    feature_columns: List[str]
    train_rows: int
    test_rows: int
    positive_ratio_train: float
    positive_ratio_test: float
    metrics: Dict[str, float]
    model_name: str
    model_version: str
    artifact_path: str
    notes: List[str] = field(default_factory=list)
    auxiliary_datasets: List[DatasetAvailability] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)
