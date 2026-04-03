from __future__ import annotations

from pathlib import Path

from factlog_ml.db import Database, SensorRecordCreate, SensorRepository


def test_sensor_repository_creates_and_soft_deletes_records(tmp_path: Path) -> None:
    database = Database(tmp_path / "factlog.db")
    database.initialize()
    repository = SensorRepository(database)

    record_id = repository.create_sensor_record(
        SensorRecordCreate(
            equipment_name="MILL-01",
            equipment_type="milling_machine",
            source_dataset="manual",
            timestamp="2026-04-03T10:00:00Z",
            temperature=301.5,
            vibration=0.14,
            rpm=1500.0,
            torque=35.0,
            tool_wear=12.0,
        )
    )

    rows = repository.list_sensor_records()
    assert rows[0]["id"] == record_id
    assert rows[0]["equipment_name"] == "MILL-01"
    assert rows[0]["deleted_at"] is None

    repository.soft_delete_sensor_record(record_id)
    deleted_rows = repository.list_sensor_records()
    assert deleted_rows[0]["deleted_at"] is not None


def test_sensor_repository_reuses_equipment_for_same_name(tmp_path: Path) -> None:
    database = Database(tmp_path / "factlog.db")
    database.initialize()
    repository = SensorRepository(database)

    repository.create_sensor_record(
        SensorRecordCreate(
            equipment_name="MILL-01",
            equipment_type="milling_machine",
            source_dataset="manual",
            timestamp="2026-04-03T10:00:00Z",
            temperature=301.5,
            vibration=0.14,
            rpm=1500.0,
            torque=35.0,
            tool_wear=12.0,
        )
    )
    repository.create_sensor_record(
        SensorRecordCreate(
            equipment_name="MILL-01",
            equipment_type="milling_machine",
            source_dataset="manual",
            timestamp="2026-04-03T10:05:00Z",
            temperature=302.0,
            vibration=0.15,
            rpm=1510.0,
            torque=34.0,
            tool_wear=13.0,
        )
    )

    with database.connect() as connection:
        equipment_count = connection.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]

    assert equipment_count == 1
