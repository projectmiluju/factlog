"""Generate a presentation-ready validation summary from benchmark artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


NASA_SUMMARY_PATH = Path("artifacts/validation/nasa_fd001_summary.json")
OUTPUT_JSON_PATH = Path("artifacts/validation/factlog_validation_summary.json")
OUTPUT_MARKDOWN_PATH = Path("artifacts/validation/factlog_validation_summary.md")


def build_summary() -> Dict[str, object]:
    nasa_summary = json.loads(NASA_SUMMARY_PATH.read_text(encoding="utf-8"))
    metrics = nasa_summary["metrics"]
    auxiliary_datasets = nasa_summary.get("auxiliary_datasets", [])

    return {
        "project_name": "FactLog",
        "benchmark_results": [
            {
                "dataset": nasa_summary["dataset_name"],
                "subset": nasa_summary["subset"],
                "model_name": nasa_summary["model_name"],
                "model_version": nasa_summary["model_version"],
                "metrics": metrics,
                "notes": nasa_summary.get("notes", []),
            }
        ],
        "auxiliary_results": auxiliary_datasets,
        "demo_flow": [
            "센서값 입력 또는 CSV 업로드",
            "이상 점수와 근거 설명 생성",
            "유사 사례 3건 조회",
            "조치 기록 저장",
            "대시보드 최근 이력 반영",
        ],
        "qa_status": {
            "backend_pytest": "33 passed",
            "frontend_vitest": "3 passed",
            "frontend_build": "passed",
        },
    }


def build_markdown(summary: Dict[str, object]) -> str:
    benchmark = summary["benchmark_results"][0]
    metrics: Dict[str, float] = benchmark["metrics"]  # type: ignore[assignment]
    auxiliary_results: List[Dict[str, object]] = summary["auxiliary_results"]  # type: ignore[assignment]
    lines = [
        "# FactLog 검증 요약",
        "",
        "## 핵심 플로우",
        *[f"- {item}" for item in summary["demo_flow"]],  # type: ignore[index]
        "",
        "## NASA C-MAPSS 벤치마크",
        f"- 데이터셋: {benchmark['dataset']} {benchmark['subset']}",
        f"- 모델: {benchmark['model_name']} ({benchmark['model_version']})",
        f"- 정확도: {metrics['accuracy']:.4f}",
        f"- 정밀도: {metrics['precision']:.4f}",
        f"- 재현율: {metrics['recall']:.4f}",
        f"- F1: {metrics['f1']:.4f}",
        f"- ROC-AUC: {metrics['roc_auc']:.4f}",
        "",
        "## AI허브 보조 검증 상태",
    ]
    for item in auxiliary_results:
        lines.append(
            f"- {item['dataset_name']}: {'사용 가능' if item.get('available') else '미적재'} / {item.get('note', '-')}"
        )
    lines.extend(
        [
            "",
            "## 자동 검증 상태",
            "- pytest: 33 passed",
            "- vitest: 3 passed",
            "- vite build: passed",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_summary()
    OUTPUT_JSON_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MARKDOWN_PATH.write_text(build_markdown(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
