"""Analysis scoring, explanation generation, and similar-case lookup."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - import failure handled by fallback
    OpenAI = None  # type: ignore[assignment]


MODEL_VERSION = "rule-based-baseline-v1"
OPENAI_MODEL = "gpt-4.1-mini"
ANOMALY_SCORE_SCALE = 2.3


@dataclass(frozen=True)
class SimilarCase:
    analysis_result_id: int
    sensor_record_id: int
    equipment_name: str
    timestamp: str
    anomaly_score: float
    similarity_score: float


@dataclass(frozen=True)
class AnalysisComputation:
    anomaly_score: float
    is_anomaly: bool
    fallback_explanation: str
    explanation_source: str
    similar_cases: List[SimilarCase]


def _normalize(value: float, baseline: float, spread: float) -> float:
    if spread <= 0:
        return 0.0
    return abs(value - baseline) / spread


def compute_anomaly_score(sensor_record: Dict[str, object]) -> float:
    temperature_score = _normalize(float(sensor_record["temperature"]), 300.0, 7.5)
    vibration_score = _normalize(float(sensor_record["vibration"]), 0.12, 0.08)
    rpm_score = _normalize(float(sensor_record["rpm"]), 1500.0, 250.0)
    torque_score = _normalize(float(sensor_record["torque"]), 35.0, 12.0)
    tool_wear_score = _normalize(float(sensor_record["tool_wear"]), 15.0, 10.0)

    weighted_score = (
        temperature_score * 0.25
        + vibration_score * 0.25
        + rpm_score * 0.15
        + torque_score * 0.2
        + tool_wear_score * 0.15
    )
    return round(min(weighted_score / ANOMALY_SCORE_SCALE, 1.0), 4)


def build_fallback_explanation(sensor_record: Dict[str, object], anomaly_score: float) -> str:
    reasons: List[str] = []
    temperature = float(sensor_record["temperature"])
    vibration = float(sensor_record["vibration"])
    rpm = float(sensor_record["rpm"])
    torque = float(sensor_record["torque"])
    tool_wear = float(sensor_record["tool_wear"])

    if temperature > 305.0:
        reasons.append("온도가 기준 범위(300±5)를 초과했습니다")
    if vibration > 0.18:
        reasons.append("진동값이 기준치(0.18)를 넘었습니다")
    if tool_wear > 22.0:
        reasons.append("공구 마모도가 높은 편입니다")
    torque_ratio = torque / rpm if rpm else 0.0
    if torque_ratio > 0.03:
        reasons.append("회전수 대비 토크 비율이 비정상적으로 높습니다")

    if not reasons:
        reasons.append("주요 센서값이 기준선과 유의미하게 벌어지지 않았습니다")

    prefix = "이상 가능성이 높습니다." if anomaly_score >= 0.55 else "즉시 이상으로 보기 어렵습니다."
    return "{0} 근거: {1}.".format(prefix, "; ".join(reasons))


def generate_explanation(sensor_record: Dict[str, object], anomaly_score: float, fallback_text: str) -> tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return fallback_text, "fallback"

    prompt = (
        "당신은 제조 설비 이상 감지 보조 시스템이다. "
        "현장 작업자가 이해할 수 있는 한국어 2문장으로만 설명하라. "
        "센서값과 기준 비교를 포함하고, 과장하지 마라.\n"
        "입력 센서: {0}\n"
        "이상 점수: {1}"
    ).format(sensor_record, anomaly_score)

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )
        explanation = getattr(response, "output_text", "").strip()
        if not explanation:
            return fallback_text, "fallback"
        return explanation, "openai"
    except Exception:
        return fallback_text, "fallback"


def compute_similarity(current_record: Dict[str, object], candidate_record: Dict[str, object]) -> float:
    current_vector = [
        float(current_record["temperature"]),
        float(current_record["vibration"]),
        float(current_record["rpm"]),
        float(current_record["torque"]),
        float(current_record["tool_wear"]),
    ]
    candidate_vector = [
        float(candidate_record["temperature"]),
        float(candidate_record["vibration"]),
        float(candidate_record["rpm"]),
        float(candidate_record["torque"]),
        float(candidate_record["tool_wear"]),
    ]
    distance = math.sqrt(sum((left - right) ** 2 for left, right in zip(current_vector, candidate_vector)))
    return round(1.0 / (1.0 + distance), 4)


def build_analysis(
    sensor_record: Dict[str, object],
    previous_cases: List[Dict[str, object]],
) -> AnalysisComputation:
    anomaly_score = compute_anomaly_score(sensor_record)
    is_anomaly = anomaly_score >= 0.55
    fallback_text = build_fallback_explanation(sensor_record, anomaly_score)
    explanation_text, explanation_source = generate_explanation(sensor_record, anomaly_score, fallback_text)

    similar_cases: List[SimilarCase] = []
    for candidate in previous_cases:
        similarity_score = compute_similarity(sensor_record, candidate)
        similar_cases.append(
            SimilarCase(
                analysis_result_id=int(candidate["analysis_result_id"]),
                sensor_record_id=int(candidate["sensor_record_id"]),
                equipment_name=str(candidate["equipment_name"]),
                timestamp=str(candidate["timestamp"]),
                anomaly_score=float(candidate["anomaly_score"]),
                similarity_score=similarity_score,
            )
        )

    ranked_cases = sorted(similar_cases, key=lambda item: item.similarity_score, reverse=True)[:3]
    return AnalysisComputation(
        anomaly_score=anomaly_score,
        is_anomaly=is_anomaly,
        fallback_explanation=explanation_text,
        explanation_source=explanation_source,
        similar_cases=ranked_cases,
    )
