"""FastAPI application for sensor intake."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from .api_schemas import (
    CsvUploadErrorResponse,
    CsvUploadResponse,
    ManualIntakeRequest,
    ManualIntakeResponse,
    ValidationErrorItem,
)
from .db import DEFAULT_DB_PATH, Database, SensorRecordCreate, SensorRepository
from .uploads import parse_sensor_csv, validate_file_metadata


def create_app(db_path: Union[Path, str] = DEFAULT_DB_PATH) -> FastAPI:
    database = Database(db_path=db_path)
    database.initialize()
    repository = SensorRepository(database=database)

    app = FastAPI(title="FactLog API", version="0.1.0")
    app.state.repository = repository

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/sensor-records", response_model=ManualIntakeResponse, status_code=status.HTTP_201_CREATED)
    def create_manual_sensor_record(payload: ManualIntakeRequest) -> ManualIntakeResponse:
        record = payload.sensor_record
        record_id = repository.create_sensor_record(
            SensorRecordCreate(
                equipment_name=record.equipment_name,
                equipment_type=record.equipment_type,
                source_dataset=record.source_dataset,
                timestamp=record.timestamp,
                temperature=record.temperature,
                vibration=record.vibration,
                rpm=record.rpm,
                torque=record.torque,
                tool_wear=record.tool_wear,
            )
        )
        return ManualIntakeResponse(record_id=record_id, status="saved")

    @app.post(
        "/api/uploads/csv",
        response_model=CsvUploadResponse,
        responses={422: {"model": CsvUploadErrorResponse}},
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_csv(file: UploadFile = File(...)) -> CsvUploadResponse:
        content = await file.read()
        metadata_errors = validate_file_metadata(filename=file.filename or "", content=content)
        if metadata_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[ValidationErrorItem(**error.__dict__).model_dump() for error in metadata_errors],
            )

        parse_result = parse_sensor_csv(content)
        if parse_result.errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[ValidationErrorItem(**error.__dict__).model_dump() for error in parse_result.errors],
            )

        record_ids = repository.create_sensor_records(parse_result.records)
        return CsvUploadResponse(
            status="imported",
            imported_count=len(record_ids),
            record_ids=record_ids,
        )

    return app


app = create_app()
