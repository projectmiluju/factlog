"""Public validation orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .constants import (
    DEFAULT_ANOMALY_THRESHOLD,
    DEFAULT_DATA_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SUBSET,
    FEATURE_COLUMNS,
)
from .nasa_cmapss import load_cmapss_splits
from .schemas import DatasetAvailability, ValidationSummary


def run_validation(
    data_dir: Path = DEFAULT_DATA_DIR,
    subset: str = DEFAULT_SUBSET,
    anomaly_threshold_cycles: int = DEFAULT_ANOMALY_THRESHOLD,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    aihub_available: bool = False,
    aihub_note: Optional[str] = None,
) -> ValidationSummary:
    from .pipeline import train_and_evaluate

    train_split, test_split = load_cmapss_splits(
        data_dir=data_dir,
        subset=subset,
        anomaly_threshold_cycles=anomaly_threshold_cycles,
    )
    evaluation = train_and_evaluate(train_split=train_split, test_split=test_split)

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / "nasa_{0}_summary.json".format(subset.lower())

    summary = ValidationSummary(
        dataset_name="NASA C-MAPSS",
        subset=subset,
        anomaly_threshold_cycles=anomaly_threshold_cycles,
        feature_columns=list(FEATURE_COLUMNS),
        train_rows=train_split.row_count,
        test_rows=test_split.row_count,
        positive_ratio_train=round(train_split.positive_ratio, 4),
        positive_ratio_test=round(test_split.positive_ratio, 4),
        metrics=evaluation.metrics,
        model_name=evaluation.model_name,
        model_version=evaluation.model_version,
        artifact_path=str(artifact_path),
        notes=[
            "라벨 규칙은 RUL <= anomaly_threshold_cycles 를 이상 상태로 본다.",
            "MVP 시연 데이터셋은 NASA C-MAPSS이며 AI허브는 보조 검증 대상으로 분리한다.",
        ],
        auxiliary_datasets=[
            DatasetAvailability(
                dataset_name="AIHub 제조 데이터",
                available=aihub_available,
                note=aihub_note or "아직 로컬에 적재되지 않아 보조 검증만 계획된 상태다.",
            )
        ],
    )

    artifact_path.write_text(
        json.dumps(summary.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary
