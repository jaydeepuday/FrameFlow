"""Fine-tuning entry point placeholder; intentionally disabled for FrameFlow v1."""

from __future__ import annotations

import argparse

TRAINING_ENABLED = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FrameFlow RIFE fine-tuning (disabled in v1)")
    parser.add_argument("--config", default="configs/train.yaml")
    parser.parse_args(argv)
    if not TRAINING_ENABLED:
        print("Training disabled: TRAINING_ENABLED = False")
        return 0
    raise RuntimeError("Training path is not enabled in this prototype.")


if __name__ == "__main__":
    raise SystemExit(main())

