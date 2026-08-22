from pathlib import Path

import pytest
from PIL import Image

from ml.inference.errors import InvalidTimestepError, MissingWeightsError
from ml.inference.interpolate import _validate_timestep
from ml.models.rife.adapter import RifeModelAdapter
from ml.preprocessing.pipeline import CorruptImageError, UnsupportedFormatError, read_rgb_image


def test_invalid_timestep_is_clean():
    with pytest.raises(InvalidTimestepError, match="only 0, 0.5, and 1"):
        _validate_timestep(0.25)


def test_missing_weights_points_to_expected_directory(tmp_path):
    with pytest.raises(MissingWeightsError, match="models/rife/train_log"):
        RifeModelAdapter(tmp_path).load()


def test_corrupt_and_unsupported_images_are_clean(tmp_path):
    corrupt = tmp_path / "bad.png"
    corrupt.write_bytes(b"not an image")
    with pytest.raises(CorruptImageError, match="Could not decode"):
        read_rgb_image(corrupt)
    unsupported = tmp_path / "image.tif"
    Image.new("RGB", (2, 2)).save(unsupported)
    with pytest.raises(UnsupportedFormatError, match="PNG and JPEG"):
        read_rgb_image(unsupported)

