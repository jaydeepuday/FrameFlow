"""PNG/JPEG preprocessing for the v1 FrameFlow pipeline.

The adapter boundary is intentional: GeoTIFF, HDF, multi-band and radiometric
metadata adapters can be added later without changing inference code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = False

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg"}
DEFAULT_MAX_DIMENSION = 2048
DEFAULT_MAX_PIXELS = 16_777_216


class PreprocessingError(ValueError):
    """Base class for safe, user-actionable preprocessing errors."""

    code = "preprocessing_error"


class UnsupportedFormatError(PreprocessingError):
    code = "unsupported_format"


class CorruptImageError(PreprocessingError):
    code = "corrupt_image"


class OversizedImageError(PreprocessingError):
    code = "oversized_image"


class DimensionMismatchError(PreprocessingError):
    code = "dimension_mismatch"


@dataclass(frozen=True)
class PreparedImage:
    original_path: Path
    original_size: tuple[int, int]
    rgb_image: Image.Image
    processed_image: Image.Image
    tensor: "object"
    resized_or_padded: bool

    @property
    def size(self) -> tuple[int, int]:
        return self.processed_image.size


def _check_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Input image was not found: {candidate.name}")
    if not candidate.is_file():
        raise PreprocessingError(f"Input image is not a file: {candidate.name}")
    if candidate.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise UnsupportedFormatError(
            "Unsupported image format. v1 accepts PNG and JPEG only."
        )
    return candidate


def read_rgb_image(
    path: str | Path,
    *,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    max_pixels: int = DEFAULT_MAX_PIXELS,
) -> tuple[Path, Image.Image, tuple[int, int]]:
    """Read and validate a PNG/JPEG as RGB without trusting its filename."""

    candidate = _check_path(path)
    try:
        with Image.open(candidate) as opened:
            width, height = opened.size
            if width <= 0 or height <= 0:
                raise CorruptImageError(f"Image has invalid dimensions: {candidate.name}")
            if width > max_dimension or height > max_dimension or width * height > max_pixels:
                raise OversizedImageError(
                    f"Image is too large. Maximum is {max_dimension}px per side and "
                    f"{max_pixels:,} pixels."
                )
            opened.verify()
        with Image.open(candidate) as opened:
            rgb = opened.convert("RGB")
            rgb.load()
    except (UnsupportedFormatError, OversizedImageError, CorruptImageError):
        raise
    except Exception as exc:
        raise CorruptImageError(
            f"Could not decode image {candidate.name}; upload a valid PNG or JPEG."
        ) from exc
    return candidate, rgb, (width, height)


def _resize_and_pad(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Fit an image into (width, height) while preserving aspect ratio."""

    target_width, target_height = target_size
    scale = min(target_width / image.width, target_height / image.height)
    resized = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGB", target_size, (0, 0, 0))
    left = (target_width - resized.width) // 2
    top = (target_height - resized.height) // 2
    canvas.paste(resized, (left, top))
    return canvas


def _pad_to_multiple(image: Image.Image, multiple: int = 32) -> Image.Image:
    width, height = image.size
    padded_width = ((width + multiple - 1) // multiple) * multiple
    padded_height = ((height + multiple - 1) // multiple) * multiple
    if (width, height) == (padded_width, padded_height):
        return image
    canvas = Image.new("RGB", (padded_width, padded_height), (0, 0, 0))
    canvas.paste(image, (0, 0))
    return canvas


def image_to_tensor(image: Image.Image):
    """Convert RGB pixels to a BCHW float tensor in [0, 1]."""

    import torch

    array = np.asarray(image, dtype=np.float32) / 255.0
    return torch.from_numpy(array.transpose(2, 0, 1)).unsqueeze(0)


def prepare_pair(
    frame0_path: str | Path,
    frame1_path: str | Path,
    *,
    auto_resize: bool = True,
    strict_dimensions: bool = False,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    max_pixels: int = DEFAULT_MAX_PIXELS,
    pad_to_multiple: int = 32,
) -> tuple[PreparedImage, PreparedImage]:
    """Prepare two images for RIFE.

    By default, differing input sizes are fit and padded into a common canvas.
    Callers that need strict validation can pass ``strict_dimensions=True``.
    """

    path0, rgb0, size0 = read_rgb_image(
        frame0_path, max_dimension=max_dimension, max_pixels=max_pixels
    )
    path1, rgb1, size1 = read_rgb_image(
        frame1_path, max_dimension=max_dimension, max_pixels=max_pixels
    )
    if size0 != size1 and strict_dimensions:
        raise DimensionMismatchError(
            f"Input dimensions differ: frame0={size0[0]}x{size0[1]}, "
            f"frame1={size1[0]}x{size1[1]}."
        )
    if size0 != size1 and not auto_resize:
        raise DimensionMismatchError(
            "Input dimensions differ and automatic resize is disabled."
        )

    common_size = (max(size0[0], size1[0]), max(size0[1], size1[1]))
    processed0 = _resize_and_pad(rgb0, common_size) if size0 != common_size else rgb0
    processed1 = _resize_and_pad(rgb1, common_size) if size1 != common_size else rgb1
    padded0 = _pad_to_multiple(processed0, pad_to_multiple)
    padded1 = _pad_to_multiple(processed1, pad_to_multiple)
    # Both images use the same common size, so padding produces the same shape.
    return (
        PreparedImage(path0, size0, rgb0, padded0, image_to_tensor(padded0), padded0 != rgb0),
        PreparedImage(path1, size1, rgb1, padded1, image_to_tensor(padded1), padded1 != rgb1),
    )


def crop_array_to_size(array: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """Crop a HWC array to a Pillow-style (width, height) size."""

    width, height = size
    return array[:height, :width]
