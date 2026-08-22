"""Consistency-based confidence proxy; it is not calibrated uncertainty."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


CONFIDENCE_LABEL = "Model confidence proxy based on interpolation/reconstruction consistency"


def confidence_proxy(frame0: np.ndarray, generated: np.ndarray, frame1: np.ndarray) -> np.ndarray:
    """Return a [0, 1] consistency score from agreement with a linear reconstruction."""

    expected = (frame0.astype(np.float32) + frame1.astype(np.float32)) / 2.0
    difference = np.mean(np.abs(generated.astype(np.float32) - expected), axis=2)
    return np.clip(1.0 - difference, 0.0, 1.0)


def confidence_levels(score: np.ndarray) -> np.ndarray:
    levels = np.zeros(score.shape, dtype=np.uint8)
    levels[score >= 0.66] = 2
    levels[(score >= 0.33) & (score < 0.66)] = 1
    return levels


def save_confidence_map(score: np.ndarray, output_path: str | Path) -> Path:
    """Save an interpretable red/yellow/green confidence proxy map with legend."""

    levels = confidence_levels(score)
    rgb = np.zeros((*levels.shape, 3), dtype=np.uint8)
    rgb[levels == 0] = (210, 65, 65)
    rgb[levels == 1] = (232, 181, 61)
    rgb[levels == 2] = (74, 167, 104)
    image = Image.fromarray(rgb, mode="RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((4, 4, 194, 42), fill=(20, 28, 40))
    draw.text((10, 10), "Low   Medium   High", fill=(255, 255, 255))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, pnginfo=_png_metadata(CONFIDENCE_LABEL))
    return output


def _png_metadata(description: str):
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("Description", description)
    return info

