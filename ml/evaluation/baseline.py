"""Classical linear midpoint baseline using the same metric implementation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.evaluation.evaluate import evaluate_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare RIFE with a linear midpoint baseline")
    parser.add_argument("--prediction", required=True, help="RIFE generated midpoint")
    parser.add_argument("--frame0", required=True)
    parser.add_argument("--frame1", required=True)
    parser.add_argument("--ground-truth")
    args = parser.parse_args()
    result = evaluate_paths(
        args.prediction,
        args.ground_truth,
        frame0_path=args.frame0,
        frame1_path=args.frame1,
    )
    print(json.dumps(result, indent=2, allow_nan=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
