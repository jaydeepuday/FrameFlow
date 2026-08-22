import numpy as np
import pytest
from PIL import Image

import ml.inference.interpolate as interpolate_module
from ml.inference.errors import GpuMemoryError, InferenceFailureError
from ml.inference.interpolate import interpolate


class FailingAdapter:
    device = "cpu"
    model_load_time_ms = 1.0
    load_count = 1

    def load(self):
        return None

    def infer(self, *_):
        raise RuntimeError("CUDA out of memory during test")


class ErrorAdapter(FailingAdapter):
    def infer(self, *_):
        raise ValueError("synthetic model failure")


def _inputs(tmp_path):
    first, second = tmp_path / "a.png", tmp_path / "b.png"
    Image.new("RGB", (32, 32), (10, 20, 30)).save(first)
    Image.new("RGB", (32, 32), (30, 20, 10)).save(second)
    return first, second


def test_out_of_memory_is_translated_to_clean_error(tmp_path, monkeypatch):
    first, second = _inputs(tmp_path)
    monkeypatch.setattr(interpolate_module, "get_default_adapter", lambda **_: FailingAdapter())
    with pytest.raises(GpuMemoryError, match="ran out of GPU memory"):
        interpolate(first, second, output_dir=tmp_path / "output")


def test_inference_failure_is_translated_to_clean_error(tmp_path, monkeypatch):
    first, second = _inputs(tmp_path)
    monkeypatch.setattr(interpolate_module, "get_default_adapter", lambda **_: ErrorAdapter())
    with pytest.raises(InferenceFailureError, match="RIFE inference failed"):
        interpolate(first, second, output_dir=tmp_path / "output")

