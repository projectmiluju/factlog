"""Pydantic schemas for the intake API."""

from __future__ import annotations

from typing import List
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SensorRecordInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    equipment_name: str = Field(min_length=1, max_length=100)
    equipment_type: str = Field(min_length=1, max_length=100)
    source_dataset: Literal["manual", "nasa_cmapss", "aihub"]
    timestamp: str = Field(min_length=1, max_length=50)
    temperature: float
    vibration: float
    rpm: float
    torque: float
    tool_wear: float


class ManualIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensor_record: SensorRecordInput


class ManualIntakeResponse(BaseModel):
    record_id: int
    status: str


class CsvUploadResponse(BaseModel):
    status: str
    imported_count: int
    record_ids: List[int]


class ValidationErrorItem(BaseModel):
    row_number: int
    column_name: str
    message: str


class CsvUploadErrorResponse(BaseModel):
    status: str
    errors: List[ValidationErrorItem]
