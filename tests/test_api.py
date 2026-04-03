from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from factlog_ml.api import create_app


def test_manual_sensor_record_endpoint_saves_payload(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.post(
        "/api/sensor-records",
        json={
            "sensor_record": {
                "equipment_name": "MILL-01",
                "equipment_type": "milling_machine",
                "source_dataset": "manual",
                "timestamp": "2026-04-03T10:00:00Z",
                "temperature": 301.5,
                "vibration": 0.14,
                "rpm": 1500.0,
                "torque": 35.0,
                "tool_wear": 12.0,
            }
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "saved"


def test_csv_upload_endpoint_returns_row_level_errors(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.post(
        "/api/uploads/csv",
        files={
            "file": (
                "sensor.csv",
                (
                    "equipment_name,equipment_type,source_dataset,timestamp,temperature,vibration,rpm,torque,tool_wear\n"
                    "MILL-01,milling_machine,manual,2026-04-03T10:00:00Z,invalid,0.14,1500,35,12\n"
                ),
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["column_name"] == "temperature"


def test_csv_upload_endpoint_imports_records(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.post(
        "/api/uploads/csv",
        files={
            "file": (
                "sensor.csv",
                (
                    "equipment_name,equipment_type,source_dataset,timestamp,temperature,vibration,rpm,torque,tool_wear\n"
                    "MILL-01,milling_machine,manual,2026-04-03T10:00:00Z,301.5,0.14,1500,35,12\n"
                    "MILL-01,milling_machine,manual,2026-04-03T10:05:00Z,302.0,0.15,1510,34,13\n"
                ),
                "text/csv",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["imported_count"] == 2


def test_manual_sensor_record_endpoint_rejects_invalid_source_dataset(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.post(
        "/api/sensor-records",
        json={
            "sensor_record": {
                "equipment_name": "MILL-01",
                "equipment_type": "milling_machine",
                "source_dataset": "unsupported",
                "timestamp": "2026-04-03T10:00:00Z",
                "temperature": 301.5,
                "vibration": 0.14,
                "rpm": 1500.0,
                "torque": 35.0,
                "tool_wear": 12.0,
            }
        },
    )

    assert response.status_code == 422


def test_csv_upload_endpoint_rejects_oversized_file(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.post(
        "/api/uploads/csv",
        files={
            "file": (
                "sensor.csv",
                b"0" * 1_000_001,
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["column_name"] == "file"
