"""CLI entrypoint for the FactLog validation pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from factlog_ml.constants import DEFAULT_ANOMALY_THRESHOLD, DEFAULT_DATA_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_SUBSET
from factlog_ml.validate import run_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run NASA C-MAPSS validation for FactLog.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--subset", type=str, default=DEFAULT_SUBSET)
    parser.add_argument("--threshold", type=int, default=DEFAULT_ANOMALY_THRESHOLD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--aihub-available",
        action="store_true",
        help="Mark AIHub auxiliary dataset as locally available.",
    )
    parser.add_argument(
        "--aihub-note",
        type=str,
        default="아직 AI허브 데이터 적재 전",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_validation(
        data_dir=args.data_dir,
        subset=args.subset,
        anomaly_threshold_cycles=args.threshold,
        output_dir=args.output_dir,
        aihub_available=args.aihub_available,
        aihub_note=args.aihub_note,
    )
    print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
