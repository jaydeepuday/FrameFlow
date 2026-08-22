import numpy as np
from PIL import Image

from ml.inference.confidence import CONFIDENCE_LABEL, confidence_levels, confidence_proxy, save_confidence_map


def test_confidence_proxy_is_consistency_based(tmp_path):
    frame0 = np.zeros((8, 8, 3), dtype=np.float32)
    frame1 = np.ones((8, 8, 3), dtype=np.float32)
    generated = np.full((8, 8, 3), 0.5, dtype=np.float32)
    score = confidence_proxy(frame0, generated, frame1)
    assert np.allclose(score, 1.0)
    assert np.all(confidence_levels(score) == 2)
    output = save_confidence_map(score, tmp_path / "confidence_map.png")
    assert output.exists()
    with Image.open(output) as image:
        assert image.info["Description"] == CONFIDENCE_LABEL
