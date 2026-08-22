import os
import sys
import pytest
import torch
import numpy as np

# Ensure root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from ml.rife.wrapper import RIFEWrapper
from ml.confidence.confidence import estimate_confidence

@pytest.fixture
def cpu_model():
    # Always test CPU logic on CI for stability
    return RIFEWrapper(device_override="cpu")

def test_confidence_estimate_shape_bounds(cpu_model):
    
    # Dims must be multiples of 32 for padding to avoid slicing errors
    img0 = torch.rand(1, 3, 128, 128).float()  # Mock tensor 1 
    img1 = torch.rand(1, 3, 128, 128).float()  # Mock tensor 2
    
    cmap, mean_conf, low_frac = estimate_confidence(cpu_model.model, img0, img1)
    
    # Ensure map has correct spatial resolution (using H, W from input)
    assert cmap.shape == (128, 128)
    
    # Assure all bounds conform to (0, 1)
    assert 0.0 <= mean_conf <= 1.0
    assert 0.0 <= low_frac <= 1.0
    assert np.min(cmap) >= 0.0
    assert np.max(cmap) <= 1.0
