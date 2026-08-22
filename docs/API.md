# FrameFlow API Documentation

## Endpoints

### `GET /health`
Standard health check.
**Response:**
```json
{
  "status": "ok",
  "device": "cuda:0",
  "cuda_available": true,
  "model_loaded": true
}
```

### `GET /model/info`
Retrieves loaded model configurations.
**Response:**
```json
{
  "model_name": "ECCV2022-RIFE",
  "model_variant": "RIFE_HDv3",
  "device": "cuda:0",
  "weights_availability": "Loaded from models/rife",
  "supported_timestep": "Continuous (0.0 to 1.0 but optimal at 0.5)",
  "input_output_capabilities": {
    "format": "RGB 8-bit OR Grayscale/Multi-band TIFF via Preprocessing API",
    "dim": "Padding to multiple of 32 internally"
  }
}
```

### `POST /interpolate`
Generates temporal interpolations with physics-driven confidence metrics.
**Request:** `multipart/form-data`
- `frame0`: Image File
- `frame1`: Image File
- `timestep`: Float (Default: `0.5`)

**Response:**
```json
{
  "generated_image_url": "/outputs/[uuid]_out.png",
  "confidence_map_url": "/outputs/[uuid]_cmap.png",
  "timestep": 0.5,
  "device": "cuda:0",
  "inference_time_ms": 12.19,
  "image_dimensions": "128x128",
  "confidence_metrics": {
      "mean_confidence": 0.999,
      "low_confidence_fraction": 0.001
  }
}
```

### `POST /evaluate`
Calculates structural evaluation metrics for provided truths.
**Request:** `multipart/form-data`
- `frame0`: Image File
- `ground_truth`: Image File
- `frame2`: Image File

**Response:**
```json
{
  "mae": 1.05,
  "psnr": 40.74,
  "ssim": 0.99,
  "runtime": 12.19
}
```
