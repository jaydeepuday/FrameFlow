"""Validation entry point placeholder; training remains disabled for FrameFlow v1."""

from __future__ import annotations

import argparse

TRAINING_ENABLED = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FrameFlow dataset validation")
    parser.add_argument("--manifest", default="data/manifest.jsonl")
    parser.parse_args(argv)
    if not TRAINING_ENABLED:
        print("Validation scaffold loaded; training remains disabled: TRAINING_ENABLED = False")
        return 0
    raise RuntimeError("Training validation path is not enabled in this prototype.")


if __name__ == "__main__":
    raise SystemExit(main())

