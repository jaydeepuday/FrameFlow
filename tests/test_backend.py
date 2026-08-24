import pytest
from fastapi.testclient import TestClient
import numpy as np
import cv2
import os
from backend.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cuda_available" in data

def test_model_info(client):
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "ECCV2022-RIFE"

def test_interpolate_invalid_image(client, tmp_path):
    # Upload a text file as image
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("not an image")
    
    # We need to seek to 0 if passing file object multiple times, but better to just open twice
    with open(bad_file, "rb") as f0, open(bad_file, "rb") as f1:
        response = client.post("/interpolate", files={"frame0": f0, "frame1": f1}, data={"timestep": 0.5})
    
    assert response.status_code == 500 # Should hit our exception wrapper when image load fails
    
def test_evaluate_endpoint(client, tmp_path):
    img = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    p = tmp_path / "f.png"
    cv2.imwrite(str(p), img)
    
    with open(p, "rb") as f0, open(p, "rb") as f1, open(p, "rb") as f2:
        response = client.post("/evaluate", files={"frame0": f0, "ground_truth": f1, "frame2": f2})
        
    assert response.status_code == 200
    data = response.json()
    assert "rife_metrics" in data
    assert "linear_metrics" in data
    assert "mae" in data["rife_metrics"]
    assert "psnr" in data["rife_metrics"]
    assert "ssim" in data["rife_metrics"]

