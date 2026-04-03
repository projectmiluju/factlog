"""NASA C-MAPSS data loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

from .constants import FEATURE_COLUMNS, RAW_COLUMN_NAMES


@dataclass(frozen=True)
class CMAPSSSplit:
    features: np.ndarray
    labels: np.ndarray
    row_count: int
    positive_ratio: float


def _load_txt_matrix(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError("NASA C-MAPSS file not found: {0}".format(path))
    return np.loadtxt(path)


def _rows_to_dicts(rows: np.ndarray) -> List[Dict[str, float]]:
    normalized = np.atleast_2d(rows)
    if normalized.shape[1] != len(RAW_COLUMN_NAMES):
        raise ValueError(
            "Expected {0} columns but found {1}".format(
                len(RAW_COLUMN_NAMES),
                normalized.shape[1],
            )
        )
    output: List[Dict[str, float]] = []
    for row in normalized:
        record = {
            column: float(value)
            for column, value in zip(RAW_COLUMN_NAMES, row.tolist())
        }
        output.append(record)
    return output


def _build_rul_lookup(rows: Sequence[Dict[str, float]], final_rul: Iterable[float] | None) -> Dict[int, int]:
    max_cycle_by_unit: Dict[int, int] = {}
    for row in rows:
        unit = int(row["unit_number"])
        cycle = int(row["time_in_cycles"])
        if unit not in max_cycle_by_unit or cycle > max_cycle_by_unit[unit]:
            max_cycle_by_unit[unit] = cycle

    lookup: Dict[int, int] = {}
    if final_rul is None:
        return max_cycle_by_unit

    for index, remaining_cycles in enumerate(final_rul, start=1):
        lookup[index] = int(max_cycle_by_unit[index] + float(remaining_cycles))
    return lookup


def _build_split(
    rows: Sequence[Dict[str, float]],
    failure_cycle_lookup: Dict[int, int],
    anomaly_threshold_cycles: int,
) -> CMAPSSSplit:
    feature_rows: List[List[float]] = []
    labels: List[int] = []

    for row in rows:
        unit = int(row["unit_number"])
        cycle = int(row["time_in_cycles"])
        failure_cycle = int(failure_cycle_lookup[unit])
        rul = max(failure_cycle - cycle, 0)
        is_anomaly = 1 if rul <= anomaly_threshold_cycles else 0
        feature_rows.append([float(row[column]) for column in FEATURE_COLUMNS])
        labels.append(is_anomaly)

    features = np.asarray(feature_rows, dtype=float)
    label_array = np.asarray(labels, dtype=int)
    positive_ratio = float(label_array.mean()) if label_array.size else 0.0

    return CMAPSSSplit(
        features=features,
        labels=label_array,
        row_count=int(label_array.size),
        positive_ratio=positive_ratio,
    )


def load_cmapss_splits(
    data_dir: Path,
    subset: str,
    anomaly_threshold_cycles: int,
) -> Tuple[CMAPSSSplit, CMAPSSSplit]:
    train_path = data_dir / "train_{0}.txt".format(subset)
    test_path = data_dir / "test_{0}.txt".format(subset)
    rul_path = data_dir / "RUL_{0}.txt".format(subset)

    train_rows = _rows_to_dicts(_load_txt_matrix(train_path))
    test_rows = _rows_to_dicts(_load_txt_matrix(test_path))
    final_rul = np.loadtxt(rul_path)

    train_failure_cycles = _build_rul_lookup(train_rows, final_rul=None)
    test_failure_cycles = _build_rul_lookup(test_rows, final_rul=np.atleast_1d(final_rul))

    train_split = _build_split(train_rows, train_failure_cycles, anomaly_threshold_cycles)
    test_split = _build_split(test_rows, test_failure_cycles, anomaly_threshold_cycles)
    return train_split, test_split
