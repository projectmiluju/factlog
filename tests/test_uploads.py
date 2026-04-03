from __future__ import annotations

from factlog_ml.uploads import parse_sensor_csv, validate_file_metadata


def test_parse_sensor_csv_reports_missing_required_columns() -> None:
    content = b"equipment_name,timestamp,temperature\nMILL-01,2026-04-03T10:00:00Z,301.5\n"

    result = parse_sensor_csv(content)

    assert result.records == []
    assert result.errors[0].column_name == "equipment_type,source_dataset,vibration,rpm,torque,tool_wear"


def test_parse_sensor_csv_reports_non_numeric_values() -> None:
    content = (
        "equipment_name,equipment_type,source_dataset,timestamp,temperature,vibration,rpm,torque,tool_wear\n"
        "MILL-01,milling_machine,manual,2026-04-03T10:00:00Z,abc,0.14,1500,35,12\n"
    ).encode("utf-8")

    result = parse_sensor_csv(content)

    assert result.records == []
    assert result.errors[0].row_number == 2
    assert result.errors[0].column_name == "temperature"


def test_validate_file_metadata_rejects_non_csv() -> None:
    errors = validate_file_metadata(filename="sensor.json", content=b"{}")

    assert errors[0].column_name == "file"


def test_validate_file_metadata_rejects_oversized_file() -> None:
    errors = validate_file_metadata(
        filename="sensor.csv",
        content=b"0" * 1_000_001,
    )

    assert errors[0].message == "파일 크기는 1MB 이하여야 합니다."


def test_parse_sensor_csv_rejects_invalid_source_dataset() -> None:
    content = (
        "equipment_name,equipment_type,source_dataset,timestamp,temperature,vibration,rpm,torque,tool_wear\n"
        "MILL-01,milling_machine,unsupported,2026-04-03T10:00:00Z,301.5,0.14,1500,35,12\n"
    ).encode("utf-8")

    result = parse_sensor_csv(content)

    assert result.records == []
    assert result.errors[0].column_name == "source_dataset"


def test_parse_sensor_csv_rejects_empty_required_string_fields() -> None:
    content = (
        "equipment_name,equipment_type,source_dataset,timestamp,temperature,vibration,rpm,torque,tool_wear\n"
        ",milling_machine,manual,2026-04-03T10:00:00Z,301.5,0.14,1500,35,12\n"
    ).encode("utf-8")

    result = parse_sensor_csv(content)

    assert result.records == []
    assert result.errors[0].column_name == "equipment_name"
