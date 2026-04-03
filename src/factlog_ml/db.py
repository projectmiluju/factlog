"""SQLite persistence layer for FactLog."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Union


DEFAULT_DB_PATH = Path("factlog.db")


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        source_dataset TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sensor_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        temperature REAL NOT NULL,
        vibration REAL NOT NULL,
        rpm REAL NOT NULL,
        torque REAL NOT NULL,
        tool_wear REAL NOT NULL,
        raw_payload TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted_at TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analysis_result (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_record_id INTEGER NOT NULL,
        anomaly_score REAL,
        is_anomaly INTEGER,
        model_version TEXT,
        explanation_text TEXT,
        similar_case_ids TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted_at TEXT,
        FOREIGN KEY (sensor_record_id) REFERENCES sensor_record (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS action_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_result_id INTEGER NOT NULL,
        action_taken TEXT NOT NULL,
        operator_name TEXT NOT NULL,
        result_note TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted_at TEXT,
        FOREIGN KEY (analysis_result_id) REFERENCES analysis_result (id)
    )
    """,
)


@dataclass(frozen=True)
class EquipmentRecord:
    id: int
    name: str
    type: str
    source_dataset: str


@dataclass(frozen=True)
class SensorRecordCreate:
    equipment_name: str
    equipment_type: str
    source_dataset: str
    timestamp: str
    temperature: float
    vibration: float
    rpm: float
    torque: float
    tool_wear: float

    def raw_payload(self) -> Dict[str, object]:
        return {
            "temperature": self.temperature,
            "vibration": self.vibration,
            "rpm": self.rpm,
            "torque": self.torque,
            "tool_wear": self.tool_wear,
        }


class Database:
    def __init__(self, db_path: Union[Path, str] = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            for statement in SCHEMA_STATEMENTS:
                connection.execute(statement)
            connection.commit()


class SensorRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def upsert_equipment(self, name: str, equipment_type: str, source_dataset: str) -> EquipmentRecord:
        with self.database.connect() as connection:
            existing = connection.execute(
                """
                SELECT id, name, type, source_dataset
                FROM equipment
                WHERE name = ?
                """,
                (name,),
            ).fetchone()
            if existing is not None:
                return EquipmentRecord(
                    id=int(existing["id"]),
                    name=str(existing["name"]),
                    type=str(existing["type"]),
                    source_dataset=str(existing["source_dataset"]),
                )

            cursor = connection.execute(
                """
                INSERT INTO equipment (name, type, source_dataset)
                VALUES (?, ?, ?)
                """,
                (name, equipment_type, source_dataset),
            )
            connection.commit()
            return EquipmentRecord(
                id=int(cursor.lastrowid),
                name=name,
                type=equipment_type,
                source_dataset=source_dataset,
            )

    def create_sensor_record(self, sensor_record: SensorRecordCreate) -> int:
        equipment = self.upsert_equipment(
            name=sensor_record.equipment_name,
            equipment_type=sensor_record.equipment_type,
            source_dataset=sensor_record.source_dataset,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO sensor_record (
                    equipment_id,
                    timestamp,
                    temperature,
                    vibration,
                    rpm,
                    torque,
                    tool_wear,
                    raw_payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    equipment.id,
                    sensor_record.timestamp,
                    sensor_record.temperature,
                    sensor_record.vibration,
                    sensor_record.rpm,
                    sensor_record.torque,
                    sensor_record.tool_wear,
                    json.dumps(sensor_record.raw_payload(), ensure_ascii=False),
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def create_sensor_records(self, sensor_records: Iterable[SensorRecordCreate]) -> List[int]:
        created_ids: List[int] = []
        for sensor_record in sensor_records:
            created_ids.append(self.create_sensor_record(sensor_record))
        return created_ids

    def list_sensor_records(self) -> List[sqlite3.Row]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    sensor_record.id,
                    equipment.name AS equipment_name,
                    equipment.type AS equipment_type,
                    equipment.source_dataset AS source_dataset,
                    sensor_record.timestamp,
                    sensor_record.temperature,
                    sensor_record.vibration,
                    sensor_record.rpm,
                    sensor_record.torque,
                    sensor_record.tool_wear,
                    sensor_record.deleted_at
                FROM sensor_record
                INNER JOIN equipment ON equipment.id = sensor_record.equipment_id
                ORDER BY sensor_record.id ASC
                """
            ).fetchall()
            return rows

    def soft_delete_sensor_record(self, sensor_record_id: int) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE sensor_record
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (sensor_record_id,),
            )
            connection.commit()
