"""Shared constants for the FactLog validation pipeline."""

from __future__ import annotations

from pathlib import Path

DEFAULT_SUBSET = "FD001"
DEFAULT_ANOMALY_THRESHOLD = 30

RAW_COLUMN_NAMES = [
    "unit_number",
    "time_in_cycles",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    "sensor_1",
    "sensor_2",
    "sensor_3",
    "sensor_4",
    "sensor_5",
    "sensor_6",
    "sensor_7",
    "sensor_8",
    "sensor_9",
    "sensor_10",
    "sensor_11",
    "sensor_12",
    "sensor_13",
    "sensor_14",
    "sensor_15",
    "sensor_16",
    "sensor_17",
    "sensor_18",
    "sensor_19",
    "sensor_20",
    "sensor_21",
]

# NASA C-MAPSS literature commonly drops near-constant sensors and keeps
# operational settings plus sensors with stronger degradation signals.
FEATURE_COLUMNS = [
    "time_in_cycles",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    "sensor_2",
    "sensor_3",
    "sensor_4",
    "sensor_7",
    "sensor_8",
    "sensor_11",
    "sensor_12",
    "sensor_13",
    "sensor_15",
    "sensor_17",
    "sensor_20",
    "sensor_21",
]

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT_DIR / "data" / "raw" / "nasa-cmapss"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "artifacts" / "validation"
