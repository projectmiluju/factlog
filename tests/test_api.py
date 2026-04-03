from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from factlog_ml.api import create_app


def _seed_sensor_record(client: TestClient) -> int:
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
    return int(response.json()["record_id"])


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


def test_analysis_endpoint_returns_score_and_fallback_explanation(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)
    record_id = _seed_sensor_record(client)

    response = client.post("/api/analysis", json={"sensor_record_id": record_id})

    assert response.status_code == 201
    payload = response.json()
    assert payload["sensor_record_id"] == record_id
    assert "explanation_text" in payload
    assert payload["explanation_source"] in {"fallback", "openai"}


def test_analysis_endpoint_returns_empty_similar_cases_when_no_history(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)
    record_id = _seed_sensor_record(client)

    response = client.post("/api/analysis", json={"sensor_record_id": record_id})

    assert response.status_code == 201
    assert response.json()["similar_cases"] == []


def test_similar_cases_endpoint_returns_ranked_cases(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)
    first_id = _seed_sensor_record(client)
    client.post(
        "/api/sensor-records",
        json={
            "sensor_record": {
                "equipment_name": "MILL-02",
                "equipment_type": "milling_machine",
                "source_dataset": "manual",
                "timestamp": "2026-04-03T10:05:00Z",
                "temperature": 302.0,
                "vibration": 0.15,
                "rpm": 1490.0,
                "torque": 36.0,
                "tool_wear": 13.0,
            }
        },
    )
    second_id = 2

    client.post("/api/analysis", json={"sensor_record_id": second_id})
    analysis_response = client.post("/api/analysis", json={"sensor_record_id": first_id})

    similar_cases_response = client.get(
        "/api/similar-cases/{0}".format(analysis_response.json()["analysis_result_id"])
    )

    assert similar_cases_response.status_code == 200
    assert len(similar_cases_response.json()["similar_cases"]) >= 1


def test_analysis_detail_endpoint_preserves_explanation_source(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)
    record_id = _seed_sensor_record(client)

    create_response = client.post("/api/analysis", json={"sensor_record_id": record_id})
    analysis_result_id = create_response.json()["analysis_result_id"]

    detail_response = client.get(f"/api/analysis/{analysis_result_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["explanation_source"] == create_response.json()["explanation_source"]


def test_similar_cases_endpoint_preserves_similarity_score(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)
    first_id = _seed_sensor_record(client)
    second_response = client.post(
        "/api/sensor-records",
        json={
            "sensor_record": {
                "equipment_name": "MILL-02",
                "equipment_type": "milling_machine",
                "source_dataset": "manual",
                "timestamp": "2026-04-03T10:05:00Z",
                "temperature": 302.0,
                "vibration": 0.15,
                "rpm": 1490.0,
                "torque": 36.0,
                "tool_wear": 13.0,
            }
        },
    )
    second_id = second_response.json()["record_id"]

    client.post("/api/analysis", json={"sensor_record_id": second_id})
    create_response = client.post("/api/analysis", json={"sensor_record_id": first_id})
    created_similar_case = create_response.json()["similar_cases"][0]

    similar_cases_response = client.get(
        "/api/similar-cases/{0}".format(create_response.json()["analysis_result_id"])
    )

    assert similar_cases_response.status_code == 200
    assert similar_cases_response.json()["similar_cases"][0]["similarity_score"] == created_similar_case["similarity_score"]


def test_analysis_endpoint_returns_404_for_missing_sensor_record(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.post("/api/analysis", json={"sensor_record_id": 999})

    assert response.status_code == 404


def test_analysis_detail_endpoint_returns_404_for_missing_analysis_result(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.get("/api/analysis/999")

    assert response.status_code == 404


def test_similar_cases_endpoint_returns_404_for_missing_analysis_result(tmp_path: Path) -> None:
    app = create_app(tmp_path / "factlog.db")
    client = TestClient(app)

    response = client.get("/api/similar-cases/999")

    assert response.status_code == 404
