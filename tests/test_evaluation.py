import os
import sys
import pytest
import cv2
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from ml.evaluation.evaluate import evaluate_prediction
from ml.baselines.linear import linear_interpolate

@pytest.fixture
def dummy_triplet(tmp_path):
    img0 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.full((100, 100, 3), 255, dtype=np.uint8)
    img1_gt = np.full((100, 100, 3), 127, dtype=np.uint8) 
    
    path0 = str(os.path.join(tmp_path, "f0.png"))
    path1 = str(os.path.join(tmp_path, "f1.png"))
    path2 = str(os.path.join(tmp_path, "f2.png"))
    
    cv2.imwrite(path0, img0)
    cv2.imwrite(path1, img1_gt)
    cv2.imwrite(path2, img2)
    
    return path0, path1, path2

def test_evaluation_metrics():
    imgA = np.zeros((50, 50, 3), dtype=np.uint8)
    imgB = np.zeros((50, 50, 3), dtype=np.uint8)
    
    res = evaluate_prediction(imgA, imgB)
    assert res['mae'] == 0.0
    assert np.isclose(res['ssim'], 1.0)
    
    imgC = np.full((50, 50, 3), 255, dtype=np.uint8)
    res2 = evaluate_prediction(imgA, imgC)
    assert res2['mae'] == 255.0

def test_linear_baseline(dummy_triplet):
    f0, f1_gt, f2 = dummy_triplet
    out = linear_interpolate(f0, f2, 0.5)
    
    assert out.shape == (100, 100, 3)
    # 0.5 * 0 + 0.5 * 255 = 127.5 -> uint8 cast generally truncates to 127 without careful rounding
    # Wait, our logic: out = (1 - 0.5) * 0 + 0.5 * 255.0 = 127.5. astype(uint8) of 127.5 is 127.
    assert np.all(out == 127)
