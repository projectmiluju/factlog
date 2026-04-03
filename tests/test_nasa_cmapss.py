from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

pytest.importorskip("numpy", reason="numpy is required for NASA C-MAPSS parsing")
import numpy as np

from factlog_ml.constants import FEATURE_COLUMNS
from factlog_ml.nasa_cmapss import load_cmapss_splits


def _write_rows(path: Path, rows: List[List[float]]) -> None:
    path.write_text(
        "\n".join(" ".join(str(value) for value in row) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_load_cmapss_splits_builds_binary_labels(tmp_path: Path) -> None:
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

    train_split, test_split = load_cmapss_splits(
        data_dir=tmp_path,
        subset="FD001",
        anomaly_threshold_cycles=1,
    )

    assert train_split.features.shape == (6, len(FEATURE_COLUMNS))
    assert test_split.features.shape == (4, len(FEATURE_COLUMNS))
    assert np.array_equal(train_split.labels, np.array([0, 1, 1, 0, 1, 1]))
    assert np.array_equal(test_split.labels, np.array([0, 1, 0, 0]))


def test_load_cmapss_splits_raises_when_required_files_are_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_cmapss_splits(
            data_dir=tmp_path,
            subset="FD999",
            anomaly_threshold_cycles=30,
        )


def test_load_cmapss_splits_rejects_unexpected_column_count(tmp_path: Path) -> None:
    invalid_rows = [
        [1, 1, 0.1, 0.2, 0.3, 1.0],
    ]
    _write_rows(tmp_path / "train_FD001.txt", invalid_rows)
    _write_rows(tmp_path / "test_FD001.txt", invalid_rows)
    (tmp_path / "RUL_FD001.txt").write_text("1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected 26 columns"):
        load_cmapss_splits(
            data_dir=tmp_path,
            subset="FD001",
            anomaly_threshold_cycles=30,
        )
