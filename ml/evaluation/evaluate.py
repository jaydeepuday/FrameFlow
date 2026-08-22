"""MAE, PSNR and SSIM evaluation against a real midpoint when available."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


NO_GROUND_TRUTH_MESSAGE = "Ground truth unavailable — qualitative evaluation only."


def load_rgb(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0


def _ssim_fallback(a: np.ndarray, b: np.ndarray) -> float:
    # Global SSIM fallback keeps evaluation usable when scikit-image is absent.
    x = a.mean(axis=2)
    y = b.mean(axis=2)
    c1, c2 = 0.01**2, 0.03**2
    ux, uy = float(x.mean()), float(y.mean())
    vx, vy = float(x.var()), float(y.var())
    cov = float(((x - ux) * (y - uy)).mean())
    return ((2 * ux * uy + c1) * (2 * cov + c2)) / ((ux**2 + uy**2 + c1) * (vx + vy + c2))


def compute_metrics(prediction: np.ndarray, ground_truth: np.ndarray) -> dict[str, float]:
    if prediction.shape != ground_truth.shape:
        raise ValueError(
            f"Prediction and ground truth dimensions differ: {prediction.shape} vs {ground_truth.shape}."
        )
    mae = float(np.mean(np.abs(prediction - ground_truth)))
    mse = float(np.mean((prediction - ground_truth) ** 2))
    psnr = float("inf") if mse == 0 else float(10.0 * math.log10(1.0 / mse))
    try:
        from skimage.metrics import structural_similarity

        ssim = float(structural_similarity(ground_truth, prediction, channel_axis=2, data_range=1.0))
    except ImportError:
        ssim = _ssim_fallback(prediction, ground_truth)
    return {"mae": mae, "psnr": psnr, "ssim": ssim}


def evaluate_paths(
    prediction_path: str | Path,
    ground_truth_path: str | Path | None,
    *,
    frame0_path: str | Path | None = None,
    frame1_path: str | Path | None = None,
) -> dict:
    if not ground_truth_path:
        return {"message": NO_GROUND_TRUTH_MESSAGE, "rife": None, "linear_baseline": None}
    prediction = load_rgb(prediction_path)
    ground_truth = load_rgb(ground_truth_path)
    result = {"message": None, "rife": compute_metrics(prediction, ground_truth), "linear_baseline": None}
    if frame0_path and frame1_path:
        frame0, frame1 = load_rgb(frame0_path), load_rgb(frame1_path)
        if frame0.shape != ground_truth.shape or frame1.shape != ground_truth.shape:
            raise ValueError("Baseline inputs and ground truth must have matching dimensions.")
        result["linear_baseline"] = compute_metrics((frame0 + frame1) / 2.0, ground_truth)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate FrameFlow against a true midpoint")
    parser.add_argument("--prediction", required=True)
    parser.add_argument("--ground-truth")
    parser.add_argument("--frame0")
    parser.add_argument("--frame1")
    return parser


if __name__ == "__main__":
    args = _parser().parse_args()
    result = evaluate_paths(
        args.prediction,
        args.ground_truth,
        frame0_path=args.frame0,
        frame1_path=args.frame1,
    )
    print(json.dumps(result, indent=2, allow_nan=True))
    if result["message"]:
        print(result["message"])

