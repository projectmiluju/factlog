"""FastAPI application for sensor intake and analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Union

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .analysis import MODEL_VERSION, build_analysis
from .action_schemas import ActionLogRequest, ActionLogResponse
from .analysis_schemas import AnalysisDetailResponse, AnalysisRequest, AnalysisResponse, SimilarCaseItem, SimilarCasesResponse
from .api_schemas import (
    CsvUploadErrorResponse,
    CsvUploadResponse,
    ManualIntakeRequest,
    ManualIntakeResponse,
    ValidationErrorItem,
)
from .dashboard_schemas import DashboardSummaryResponse, MetricItem, RecentAnalysisItem, ValidationDatasetItem, ValidationSummaryResponse
from .db import (
    ActionLogCreate,
    ActionRepository,
    AnalysisRepository,
    AnalysisResultCreate,
    DEFAULT_DB_PATH,
    Database,
    SensorRecordCreate,
    SensorRepository,
)
from .uploads import parse_sensor_csv, validate_file_metadata


def _load_similar_cases_payload(raw_payload: object) -> list[SimilarCaseItem]:
    if not raw_payload:
        return []

    similar_cases = json.loads(str(raw_payload))
    return [
        SimilarCaseItem(
            analysis_result_id=int(case["analysis_result_id"]),
            sensor_record_id=int(case["sensor_record_id"]),
            equipment_name=str(case["equipment_name"]),
            timestamp=str(case["timestamp"]),
            anomaly_score=float(case["anomaly_score"]),
            similarity_score=float(case["similarity_score"]),
        )
        for case in similar_cases
    ]


def create_app(db_path: Union[Path, str] = DEFAULT_DB_PATH) -> FastAPI:
    database = Database(db_path=db_path)
    database.initialize()
    repository = SensorRepository(database=database)
    analysis_repository = AnalysisRepository(database=database)
    action_repository = ActionRepository(database=database)

    app = FastAPI(title="FactLog API", version="0.1.0")
    app.state.repository = repository
    app.state.analysis_repository = analysis_repository
    app.state.action_repository = action_repository
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4173", "http://127.0.0.1:4173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    @app.post("/api/analysis", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
    def create_analysis(payload: AnalysisRequest) -> AnalysisResponse:
        sensor_record = repository.get_sensor_record(payload.sensor_record_id)
        if sensor_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="sensor_record를 찾을 수 없습니다.")

        previous_cases = analysis_repository.list_previous_analysis_cases(payload.sensor_record_id)
        computation = build_analysis(dict(sensor_record), [dict(case) for case in previous_cases])
        analysis_result_id = analysis_repository.create_analysis_result(
            AnalysisResultCreate(
                sensor_record_id=payload.sensor_record_id,
                anomaly_score=computation.anomaly_score,
                is_anomaly=computation.is_anomaly,
                model_version=MODEL_VERSION,
                explanation_text=computation.fallback_explanation,
                explanation_source=computation.explanation_source,
                similar_cases_payload=[
                    {
                        "analysis_result_id": case.analysis_result_id,
                        "sensor_record_id": case.sensor_record_id,
                        "equipment_name": case.equipment_name,
                        "timestamp": case.timestamp,
                        "anomaly_score": case.anomaly_score,
                        "similarity_score": case.similarity_score,
                    }
                    for case in computation.similar_cases
                ],
            )
        )
        return AnalysisResponse(
            analysis_result_id=analysis_result_id,
            sensor_record_id=payload.sensor_record_id,
            anomaly_score=computation.anomaly_score,
            is_anomaly=computation.is_anomaly,
            explanation_text=computation.fallback_explanation,
            explanation_source=computation.explanation_source,
            similar_cases=[
                SimilarCaseItem(
                    analysis_result_id=case.analysis_result_id,
                    sensor_record_id=case.sensor_record_id,
                    equipment_name=case.equipment_name,
                    timestamp=case.timestamp,
                    anomaly_score=case.anomaly_score,
                    similarity_score=case.similarity_score,
                )
                for case in computation.similar_cases
            ],
        )

    @app.get("/api/analysis/{analysis_result_id}", response_model=AnalysisDetailResponse)
    def get_analysis_result(analysis_result_id: int) -> AnalysisDetailResponse:
        result = analysis_repository.get_analysis_result(analysis_result_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="analysis_result를 찾을 수 없습니다.")

        return AnalysisDetailResponse(
            analysis_result_id=int(result["id"]),
            sensor_record_id=int(result["sensor_record_id"]),
            anomaly_score=float(result["anomaly_score"]),
            is_anomaly=bool(result["is_anomaly"]),
            explanation_text=str(result["explanation_text"]),
            explanation_source=str(result["explanation_source"] or "fallback"),
            model_version=str(result["model_version"]),
            similar_cases=_load_similar_cases_payload(result["similar_cases_payload"]),
        )

    @app.get("/api/similar-cases/{analysis_result_id}", response_model=SimilarCasesResponse)
    def get_similar_cases(analysis_result_id: int) -> SimilarCasesResponse:
        result = analysis_repository.get_analysis_result(analysis_result_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="analysis_result를 찾을 수 없습니다.")

        return SimilarCasesResponse(
            analysis_result_id=analysis_result_id,
            similar_cases=_load_similar_cases_payload(result["similar_cases_payload"]),
        )

    @app.get("/api/analysis")
    def list_analysis(page: int = 1, page_size: int = 20) -> Dict[str, object]:
        recent_items = analysis_repository.list_analysis_results(limit=page_size, page=page)
        return {
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "analysis_result_id": int(item["analysis_result_id"]),
                    "sensor_record_id": int(item["sensor_record_id"]),
                    "equipment_name": str(item["equipment_name"]),
                    "timestamp": str(item["timestamp"]),
                    "anomaly_score": float(item["anomaly_score"]),
                    "is_anomaly": bool(item["is_anomaly"]),
                    "explanation_source": str(item["explanation_source"] or "fallback"),
                    "action_logged": bool(item["action_logged"]),
                }
                for item in recent_items
            ],
        }

    @app.post("/api/actions", response_model=ActionLogResponse, status_code=status.HTTP_201_CREATED)
    def create_action_log(payload: ActionLogRequest) -> ActionLogResponse:
        result = analysis_repository.get_analysis_result(payload.analysis_result_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="analysis_result를 찾을 수 없습니다.")

        action_log_id = action_repository.create_action_log(
            ActionLogCreate(
                analysis_result_id=payload.analysis_result_id,
                action_taken=payload.action_taken,
                operator_name=payload.operator_name,
                result_note=payload.result_note,
            )
        )
        return ActionLogResponse(
            action_log_id=action_log_id,
            analysis_result_id=payload.analysis_result_id,
            status="saved",
        )

    @app.get("/api/validation/summary", response_model=ValidationSummaryResponse)
    def get_validation_summary() -> ValidationSummaryResponse:
        summary_path = Path("artifacts/validation/nasa_fd001_summary.json")
        if not summary_path.exists():
            return ValidationSummaryResponse(datasets=[])

        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        datasets = [
            ValidationDatasetItem(
                dataset_name=str(payload["dataset_name"]),
                subset=str(payload.get("subset")) if payload.get("subset") else None,
                model_name=str(payload.get("model_name")) if payload.get("model_name") else None,
                model_version=str(payload.get("model_version")) if payload.get("model_version") else None,
                metrics=[
                    MetricItem(metric_name=str(metric_name), metric_value=float(metric_value))
                    for metric_name, metric_value in dict(payload.get("metrics", {})).items()
                ],
                notes=[str(note) for note in payload.get("notes", [])],
            )
        ]
        return ValidationSummaryResponse(datasets=datasets)

    @app.get("/api/dashboard/summary", response_model=DashboardSummaryResponse)
    def get_dashboard_summary() -> DashboardSummaryResponse:
        recent_items = analysis_repository.list_analysis_results(limit=20, page=1)
        validation_summary = get_validation_summary()

        accuracy_label = "-"
        if validation_summary.datasets and validation_summary.datasets[0].metrics:
            metrics = {metric.metric_name: metric.metric_value for metric in validation_summary.datasets[0].metrics}
            if "accuracy" in metrics:
                accuracy_label = "{0:.2%}".format(metrics["accuracy"])

        return DashboardSummaryResponse(
            total_analyses=analysis_repository.count_analysis_results(),
            total_actions=action_repository.count_action_logs(),
            anomaly_count=analysis_repository.count_anomalies(),
            accuracy_label=accuracy_label,
            recent_analyses=[
                RecentAnalysisItem(
                    analysis_result_id=int(item["analysis_result_id"]),
                    sensor_record_id=int(item["sensor_record_id"]),
                    equipment_name=str(item["equipment_name"]),
                    timestamp=str(item["timestamp"]),
                    anomaly_score=float(item["anomaly_score"]),
                    is_anomaly=bool(item["is_anomaly"]),
                    explanation_source=str(item["explanation_source"] or "fallback"),
                    action_logged=bool(item["action_logged"]),
                )
                for item in recent_items
            ],
            validation_datasets=validation_summary.datasets,
        )

    return app


app = create_app()
