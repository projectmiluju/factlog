from __future__ import annotations

from factlog_ml.analysis import build_analysis, build_fallback_explanation, compute_anomaly_score


def test_compute_anomaly_score_marks_high_risk_record() -> None:
    score = compute_anomaly_score(
        {
            "temperature": 312.0,
            "vibration": 0.24,
            "rpm": 1200.0,
            "torque": 45.0,
            "tool_wear": 28.0,
        }
    )

    assert score >= 0.55


def test_build_fallback_explanation_includes_threshold_reasons() -> None:
    explanation = build_fallback_explanation(
        {
            "temperature": 312.0,
            "vibration": 0.24,
            "rpm": 1200.0,
            "torque": 45.0,
            "tool_wear": 28.0,
        },
        anomaly_score=0.82,
    )

    assert "온도" in explanation
    assert "진동값" in explanation


def test_build_analysis_returns_top_three_similar_cases() -> None:
    computation = build_analysis(
        sensor_record={
            "temperature": 310.0,
            "vibration": 0.2,
            "rpm": 1300.0,
            "torque": 42.0,
            "tool_wear": 20.0,
        },
        previous_cases=[
            {
                "analysis_result_id": 1,
                "sensor_record_id": 11,
                "equipment_name": "MILL-01",
                "timestamp": "2026-04-03T10:00:00Z",
                "temperature": 309.0,
                "vibration": 0.19,
                "rpm": 1290.0,
                "torque": 41.0,
                "tool_wear": 19.0,
                "anomaly_score": 0.7,
            },
            {
                "analysis_result_id": 2,
                "sensor_record_id": 12,
                "equipment_name": "MILL-02",
                "timestamp": "2026-04-03T10:05:00Z",
                "temperature": 295.0,
                "vibration": 0.1,
                "rpm": 1500.0,
                "torque": 30.0,
                "tool_wear": 10.0,
                "anomaly_score": 0.2,
            },
            {
                "analysis_result_id": 3,
                "sensor_record_id": 13,
                "equipment_name": "MILL-03",
                "timestamp": "2026-04-03T10:10:00Z",
                "temperature": 308.0,
                "vibration": 0.18,
                "rpm": 1310.0,
                "torque": 40.0,
                "tool_wear": 18.0,
                "anomaly_score": 0.65,
            },
            {
                "analysis_result_id": 4,
                "sensor_record_id": 14,
                "equipment_name": "MILL-04",
                "timestamp": "2026-04-03T10:15:00Z",
                "temperature": 311.0,
                "vibration": 0.21,
                "rpm": 1280.0,
                "torque": 43.0,
                "tool_wear": 21.0,
                "anomaly_score": 0.74,
            },
        ],
    )

    assert len(computation.similar_cases) == 3
    assert computation.similar_cases[0].similarity_score >= computation.similar_cases[1].similarity_score
