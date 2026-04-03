"""CSV parsing and validation for sensor uploads."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .db import SensorRecordCreate


REQUIRED_CSV_COLUMNS = (
    "equipment_name",
    "equipment_type",
    "source_dataset",
    "timestamp",
    "temperature",
    "vibration",
    "rpm",
    "torque",
    "tool_wear",
)

ALLOWED_DATASETS = {"manual", "nasa_cmapss", "aihub"}
REQUIRED_TEXT_COLUMNS = (
    "equipment_name",
    "equipment_type",
    "source_dataset",
    "timestamp",
)


@dataclass(frozen=True)
class UploadValidationError:
    row_number: int
    column_name: str
    message: str


@dataclass(frozen=True)
class UploadParseResult:
    records: List[SensorRecordCreate]
    errors: List[UploadValidationError]


def _parse_float(value: str, row_number: int, column_name: str) -> float:
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(
            "숫자 형식이 아닙니다."
        ) from error


def parse_sensor_csv(content: bytes) -> UploadParseResult:
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    header = reader.fieldnames or []

    missing_columns = [column for column in REQUIRED_CSV_COLUMNS if column not in header]
    if missing_columns:
        return UploadParseResult(
            records=[],
            errors=[
                UploadValidationError(
                    row_number=0,
                    column_name=",".join(missing_columns),
                    message="필수 컬럼이 누락되었습니다.",
                )
            ],
        )

    records: List[SensorRecordCreate] = []
    errors: List[UploadValidationError] = []

    for row_index, row in enumerate(reader, start=2):
        text_values: Dict[str, str] = {}
        for column in REQUIRED_TEXT_COLUMNS:
            text_values[column] = str(row[column]).strip()
            if not text_values[column]:
                errors.append(
                    UploadValidationError(
                        row_number=row_index,
                        column_name=column,
                        message="필수 값이 비어 있습니다.",
                    )
                )

        if any(error.row_number == row_index for error in errors):
            continue

        source_dataset = text_values["source_dataset"]
        if source_dataset not in ALLOWED_DATASETS:
            errors.append(
                UploadValidationError(
                    row_number=row_index,
                    column_name="source_dataset",
                    message="지원하지 않는 source_dataset 값입니다.",
                )
            )
            continue

        numeric_values: Dict[str, float] = {}
        for column in ("temperature", "vibration", "rpm", "torque", "tool_wear"):
            raw_value = str(row[column]).strip()
            try:
                numeric_values[column] = _parse_float(raw_value, row_index, column)
            except ValueError:
                errors.append(
                    UploadValidationError(
                        row_number=row_index,
                        column_name=column,
                        message="숫자 형식이 아닙니다.",
                    )
                )

        if any(error.row_number == row_index for error in errors):
            continue

        records.append(
            SensorRecordCreate(
                equipment_name=text_values["equipment_name"],
                equipment_type=text_values["equipment_type"],
                source_dataset=source_dataset,
                timestamp=text_values["timestamp"],
                temperature=numeric_values["temperature"],
                vibration=numeric_values["vibration"],
                rpm=numeric_values["rpm"],
                torque=numeric_values["torque"],
                tool_wear=numeric_values["tool_wear"],
            )
        )

    return UploadParseResult(records=records, errors=errors)


def validate_file_metadata(filename: str, content: bytes, max_bytes: int = 1_000_000) -> List[UploadValidationError]:
    errors: List[UploadValidationError] = []
    if not filename.lower().endswith(".csv"):
        errors.append(
            UploadValidationError(
                row_number=0,
                column_name="file",
                message="CSV 파일만 업로드할 수 있습니다.",
            )
        )
    if len(content) > max_bytes:
        errors.append(
            UploadValidationError(
                row_number=0,
                column_name="file",
                message="파일 크기는 1MB 이하여야 합니다.",
            )
        )
    return errors
