from pathlib import Path

import numpy as np
from PIL import Image

from ml.evaluation.evaluate import NO_GROUND_TRUTH_MESSAGE, compute_metrics, evaluate_paths


def _save(path: Path, array: np.ndarray) -> None:
    Image.fromarray((array * 255).astype(np.uint8), mode="RGB").save(path)


def test_metrics_against_true_middle_and_linear_baseline(tmp_path):
    frame0 = np.zeros((16, 16, 3), dtype=np.float32)
    frame1 = np.ones((16, 16, 3), dtype=np.float32)
    truth = np.full((16, 16, 3), 0.5, dtype=np.float32)
    prediction = np.full((16, 16, 3), 0.5, dtype=np.float32)
    paths = [tmp_path / name for name in ("f0.png", "f1.png", "truth.png", "pred.png")]
    for path, array in zip(paths, (frame0, frame1, truth, prediction)):
        _save(path, array)
    result = evaluate_paths(paths[3], paths[2], frame0_path=paths[0], frame1_path=paths[1])
    assert result["rife"]["mae"] == 0
    assert result["linear_baseline"]["mae"] < 0.01
    assert result["linear_baseline"]["psnr"] > 40


def test_missing_ground_truth_message(tmp_path):
    path = tmp_path / "prediction.png"
    _save(path, np.zeros((4, 4, 3), dtype=np.float32))
    result = evaluate_paths(path, None)
    assert result["message"] == NO_GROUND_TRUTH_MESSAGE
