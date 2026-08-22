import os
import cv2
import numpy as np
import pytest
import torch
import sys

# Ensure root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from ml.preprocessing.image_loader import load_satellite_image
from ml.preprocessing.normalization import pad_for_rife, unpad_from_rife, normalize_and_tensorize
from ml.preprocessing.satellite import preprocess_satellite_image

@pytest.fixture
def create_dummy_images(tmp_path):
    img_rgb = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img_gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    
    rgb_path = os.path.join(tmp_path, "rgb.png")
    gray_path = os.path.join(tmp_path, "gray.png")
    
    cv2.imwrite(rgb_path, img_rgb)
    cv2.imwrite(gray_path, img_gray)
    
    return str(rgb_path), str(gray_path)

def test_load_satellite_image(create_dummy_images):
    rgb_path, gray_path = create_dummy_images
    
    img_rgb = load_satellite_image(rgb_path)
    assert img_rgb.shape == (100, 100, 3)
    
    img_gray = load_satellite_image(gray_path)
    assert img_gray.shape == (100, 100, 3) # Even grayscale should become 3 channel RGB

def test_pad_and_unpad():
    device = torch.device('cpu')
    dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    tensor = normalize_and_tensorize(dummy_img, device)
    
    padded, padding = pad_for_rife(tensor)
    
    # 100 isn't modulo 32. Next modulo 32 is 128.
    assert padded.shape == (1, 3, 128, 128)
    
    unpadded = unpad_from_rife(padded, padding)
    assert unpadded.shape == tensor.shape
