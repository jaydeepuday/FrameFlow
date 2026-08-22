from pathlib import Path

from fastapi.testclient import TestClient

import backend.main as backend


class FakeAdapter:
    model_loaded = True
    device = "cpu"


def _fake_result():
    return {
        "output_path": str(Path("C:/internal/secret/frame_t05_generated.png")),
        "comparison_path": "C:/internal/secret/comparison.png",
        "confidence_map_path": "C:/internal/secret/confidence_map.png",
        "flow_visualization_path": None,
        "device": "cpu",
        "timestep": 0.5,
        "inference_time_ms": 12.3,
        "model_load_time_ms": 3.4,
        "model_load_count": 1,
        "input_resolution": {"frame0": {"width": 2, "height": 2}, "frame1": {"width": 2, "height": 2}},
        "processed_resolution": {"width": 32, "height": 32},
        "confidence_label": "Model confidence proxy based on interpolation/reconstruction consistency",
        "generated_label": "AI GENERATED — not a real observation",
    }


def test_health_shape_and_safe_api_response(monkeypatch):
    monkeypatch.setattr(backend, "get_default_adapter", lambda: FakeAdapter())
    monkeypatch.setattr(backend, "interpolate", lambda *args, **kwargs: _fake_result())
    client = TestClient(backend.app)
    health = client.get("/api/health")
    assert health.json() == {"status": "ok", "model_loaded": True, "device": "cpu"}
    payload = {"frame0": ("safe.png", b"not-used", "image/png"), "frame1": ("safe.png", b"not-used", "image/png")}
    response = client.post("/api/interpolate", files=payload, data={"timestep": "0.5"})
    assert response.status_code == 200
    body = response.json()
    assert "C:/internal" not in response.text
    assert body["output_urls"]["generated"] == "/api/output/frame_t05_generated.png"


def test_upload_validation_rejects_unsupported_and_oversized(monkeypatch):
    monkeypatch.setattr(backend, "get_default_adapter", lambda: FakeAdapter())
    client = TestClient(backend.app)
    invalid = client.post(
        "/api/interpolate",
        files={"frame0": ("bad.tif", b"data", "image/tiff"), "frame1": ("x.png", b"data", "image/png")},
    )
    assert invalid.status_code == 415
    huge = b"x" * (backend.MAX_UPLOAD_BYTES + 1)
    oversized = client.post(
        "/api/interpolate",
        files={"frame0": ("x.png", huge, "image/png"), "frame1": ("x.png", b"data", "image/png")},
    )
    assert oversized.status_code == 413
    assert oversized.json()["detail"]["code"] == "oversized_image"

