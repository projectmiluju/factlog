"""Pydantic schemas for action log APIs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ActionLogRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_result_id: int = Field(gt=0)
    action_taken: str = Field(min_length=1, max_length=500)
    operator_name: str = Field(min_length=1, max_length=100)
    result_note: str = Field(min_length=1, max_length=1000)


class ActionLogResponse(BaseModel):
    action_log_id: int
    analysis_result_id: int
    status: str
