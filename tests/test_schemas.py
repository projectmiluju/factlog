from __future__ import annotations

from factlog_ml.schemas import DatasetAvailability, ValidationSummary


def test_validation_summary_to_dict_serializes_nested_datasets() -> None:
    summary = ValidationSummary(
        dataset_name="NASA C-MAPSS",
        subset="FD001",
        anomaly_threshold_cycles=30,
        feature_columns=["time_in_cycles", "sensor_11"],
        train_rows=100,
        test_rows=40,
        positive_ratio_train=0.2,
        positive_ratio_test=0.25,
        metrics={"accuracy": 0.91},
        model_name="LogisticRegression",
        model_version="v1",
        artifact_path="artifacts/validation/nasa_fd001_summary.json",
        notes=["fixture"],
        auxiliary_datasets=[
            DatasetAvailability(
                dataset_name="AIHub 제조 데이터",
                available=False,
                note="not loaded",
            )
        ],
    )

    payload = summary.to_dict()

    assert payload["dataset_name"] == "NASA C-MAPSS"
    assert payload["metrics"]["accuracy"] == 0.91
    assert payload["auxiliary_datasets"][0]["dataset_name"] == "AIHub 제조 데이터"
