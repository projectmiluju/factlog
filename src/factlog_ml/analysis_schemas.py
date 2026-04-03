"""Pydantic schemas for analysis APIs."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensor_record_id: int = Field(gt=0)


class SimilarCaseItem(BaseModel):
    analysis_result_id: int
    sensor_record_id: int
    equipment_name: str
    timestamp: str
    anomaly_score: float
    similarity_score: float


class AnalysisResponse(BaseModel):
    analysis_result_id: int
    sensor_record_id: int
    anomaly_score: float
    is_anomaly: bool
    explanation_text: str
    explanation_source: str
    similar_cases: List[SimilarCaseItem]


class AnalysisDetailResponse(AnalysisResponse):
    model_version: str


class SimilarCasesResponse(BaseModel):
    analysis_result_id: int
    similar_cases: List[SimilarCaseItem]
