from pathlib import Path

import pytest
from PIL import Image
from PIL import Image as PILImage

from ml.inference.errors import MissingWeightsError
from ml.inference.interpolate import interpolate
from ml.models.rife.adapter import RifeModelAdapter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = PROJECT_ROOT / "models" / "rife"


@pytest.mark.integration
def test_real_rife_loads_once_and_writes_outputs(tmp_path, monkeypatch):
    if not (WEIGHTS / "train_log" / "flownet.pkl").exists():
        pytest.skip("Official RIFE checkpoint is not present")
    # Use the real adapter but direct the module-level singleton to a fresh engine.
    import ml.inference.interpolate as interpolate_module

    adapter = RifeModelAdapter(WEIGHTS)
    monkeypatch.setattr(interpolate_module, "get_default_adapter", lambda **_: adapter)
    first, second = tmp_path / "f0.png", tmp_path / "f1.png"
    Image.new("RGB", (32, 32), (20, 90, 160)).save(first)
    Image.new("RGB", (32, 32), (160, 90, 20)).save(second)
    result1 = interpolate(first, second, output_dir=tmp_path / "out")
    result2 = interpolate(first, second, output_dir=tmp_path / "out")
    assert result1["device"] == "cpu"
    assert result1["model_load_count"] == 1
    assert result2["model_load_count"] == 1
    assert (tmp_path / "out" / "frame_t05_generated.png").exists()
    with PILImage.open(tmp_path / "out" / "comparison.png") as comparison:
        assert comparison.size == (96, 32)
