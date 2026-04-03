from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

pytest.importorskip("sklearn", reason="scikit-learn is required for validation")
from factlog_ml.validate import run_validation

def _write_rows(path: Path, rows: List[List[float]]) -> None:
    path.write_text(
        "\n".join(" ".join(str(value) for value in row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _build_fixture_dataset(tmp_path: Path) -> None:
    train_rows = [
        [1, 1, 0.1, 0.2, 0.3] + [float(index) for index in range(1, 22)],
        [1, 2, 0.1, 0.2, 0.3] + [float(index + 1) for index in range(1, 22)],
        [1, 3, 0.1, 0.2, 0.3] + [float(index + 2) for index in range(1, 22)],
        [2, 1, 0.5, 0.4, 0.3] + [float(index + 3) for index in range(1, 22)],
        [2, 2, 0.5, 0.4, 0.3] + [float(index + 4) for index in range(1, 22)],
        [2, 3, 0.5, 0.4, 0.3] + [float(index + 5) for index in range(1, 22)],
    ]
    test_rows = [
        [1, 1, 0.1, 0.2, 0.3] + [float(index + 6) for index in range(1, 22)],
        [1, 2, 0.1, 0.2, 0.3] + [float(index + 7) for index in range(1, 22)],
        [2, 1, 0.5, 0.4, 0.3] + [float(index + 8) for index in range(1, 22)],
        [2, 2, 0.5, 0.4, 0.3] + [float(index + 9) for index in range(1, 22)],
    ]
    _write_rows(tmp_path / "train_FD001.txt", train_rows)
    _write_rows(tmp_path / "test_FD001.txt", test_rows)
    (tmp_path / "RUL_FD001.txt").write_text("1\n2\n", encoding="utf-8")


def test_run_validation_writes_summary_json(tmp_path: Path) -> None:
    _build_fixture_dataset(tmp_path)
    output_dir = tmp_path / "artifacts"

    summary = run_validation(
        data_dir=tmp_path,
        subset="FD001",
        anomaly_threshold_cycles=1,
        output_dir=output_dir,
        aihub_available=False,
        aihub_note="fixture only",
    )

    artifact_path = output_dir / "nasa_fd001_summary.json"
    assert artifact_path.exists()

    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["dataset_name"] == "NASA C-MAPSS"
    assert payload["subset"] == "FD001"
    assert payload["metrics"]["accuracy"] >= 0.0
    assert summary.artifact_path == str(artifact_path)


def test_run_validation_creates_output_directory_and_keeps_aihub_note(tmp_path: Path) -> None:
    _build_fixture_dataset(tmp_path)
    output_dir = tmp_path / "nested" / "artifacts"

    summary = run_validation(
        data_dir=tmp_path,
        subset="FD001",
        anomaly_threshold_cycles=1,
        output_dir=output_dir,
        aihub_available=False,
        aihub_note="보조 검증 대기",
    )

    assert output_dir.exists()
    assert summary.auxiliary_datasets[0].note == "보조 검증 대기"
