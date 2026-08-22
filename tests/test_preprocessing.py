from pathlib import Path

import pytest
from PIL import Image

from ml.preprocessing.pipeline import DimensionMismatchError, OversizedImageError, prepare_pair


def _image(path: Path, size: tuple[int, int]) -> None:
    Image.new("RGB", size, (80, 120, 160)).save(path)


def test_non_square_png_is_padded_and_converted(tmp_path):
    first, second = tmp_path / "a.png", tmp_path / "b.png"
    _image(first, (45, 29))
    _image(second, (45, 29))
    prepared0, prepared1 = prepare_pair(first, second)
    assert prepared0.tensor.shape == (1, 3, 32, 64)
    assert prepared1.tensor.shape == prepared0.tensor.shape
    assert prepared0.original_size == (45, 29)


def test_strict_dimension_mismatch_is_actionable(tmp_path):
    first, second = tmp_path / "a.png", tmp_path / "b.png"
    _image(first, (32, 32))
    _image(second, (40, 32))
    with pytest.raises(DimensionMismatchError, match="Input dimensions differ"):
        prepare_pair(first, second, strict_dimensions=True)


def test_oversized_image_is_rejected(tmp_path):
    first, second = tmp_path / "a.png", tmp_path / "b.png"
    _image(first, (64, 64))
    _image(second, (64, 64))
    with pytest.raises(OversizedImageError, match="too large"):
        prepare_pair(first, second, max_dimension=32)

