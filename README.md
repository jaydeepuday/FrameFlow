# FrameFlow

FrameFlow is a small, observational prototype for generating one plausible
intermediate image between two manually supplied satellite frames. It uses the
official PyTorch implementation of RIFE (Real-Time Intermediate Flow
Estimation) as the pretrained interpolation backbone. A midpoint is an
AI-generated visual aid; it is not a real satellite observation, a calibrated
uncertainty estimate, or a disaster-prediction model.

## What

The v1 chain is exactly `T0 + T1 → pretrained RIFE → T0.5`, followed by a
consistency-based confidence proxy, a FastAPI endpoint, and a React dashboard.
Only PNG/JPEG inputs and timesteps `0`, `0.5`, and `1` are exposed.

## Why

The prototype makes temporal changes easier to inspect in an exploratory
monitoring workflow. It does not create new observations or replace domain
review.

## Install

Use a fresh Python environment. `environment.yml` targets Python 3.11 because
the upstream RIFE dependency ceiling predates Python 3.14; the local verification
environment was Python 3.14.6 with `torch 2.12.0+cpu`. Then run:

```powershell
pip install -r requirements.txt
```

The official upstream requirements were inspected at
`ml/models/rife/upstream/requirements.txt` and reconciled in the comments above;
the project does not copy the obsolete NumPy ceiling verbatim.
The upstream `sk-video` and `moviepy` entries are for optional upstream video
scripts and are intentionally omitted because FrameFlow v1 is image-to-image.

## Weights

The official PyTorch source is vendored at `ml/models/rife/upstream/` from
`https://github.com/megvii-research/ECCV2022-RIFE` (MIT license, inspected
commit `5d8adbdd40e12c2c8f91930eff838aebe561c086`). The externally distributed
HD checkpoint is expected at:

```text
models/rife/train_log/flownet.pkl
```

This mirrors the upstream archive's `train_log/*.pkl` convention. Weights are
not pip-installable. Before any redistribution or commercial use, reconfirm
the upstream license and checkpoint terms.

## Run inference

Place user-supplied files at `data/samples/frame_t0.png` and
`data/samples/frame_t1.png`, or provide any PNG/JPEG paths directly:

```powershell
python ml/inference/interpolate.py `
  --frame0 data/samples/frame_t0.png `
  --frame1 data/samples/frame_t1.png `
  --timestep 0.5 `
  --flow
```

Outputs are written to `ml/outputs/`: the processed inputs,
`frame_t05_generated.png`, `comparison.png`, `confidence_map.png`, and (when
requested) `flow/optical_flow_visualization.png`. The CLI prints device,
model-load time, inference time, resolution, and timestep. Device selection is
driven by `torch.cuda.is_available()`; FP16 is opt-in and CUDA-only.

## Run backend

```powershell
uvicorn backend.main:app --reload --port 8000
```

Then check `GET /api/health`. `POST /api/interpolate` accepts multipart
`frame0`, `frame1`, and optional `timestep` (default `0.5`). Uploads are
validated as PNG/JPEG, capped at 15 MB, and written with server-generated names.
The local CORS allowlist is explicit for ports 5173; tighten it for anything
beyond a local demo.

## Run frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, upload T0/T1, keep the slider at `T0.5`, and choose
“Generate midpoint”. The dashboard shows a three-panel comparison, an
AI-generated label, a real-vs-generated timeline, telemetry, and a confidence
proxy toggle. It shows PSNR/SSIM/MAE only when a ground-truth result is supplied
by a future evaluation-integrated workflow.

## Evaluate

Without a true middle frame:

```powershell
python ml/evaluation/evaluate.py --prediction ml/outputs/frame_t05_generated.png
```

The literal result is `Ground truth unavailable — qualitative evaluation only.`
With a true midpoint and endpoints:

```powershell
python ml/evaluation/baseline.py `
  --prediction ml/outputs/frame_t05_generated.png `
  --frame0 ml/outputs/frame_t0.png `
  --frame1 ml/outputs/frame_t1.png `
  --ground-truth path/to/true_middle.png
```

This reports MAE, PSNR, and SSIM for both RIFE and the classical `0.5*T0 +
0.5*T1` baseline.

## Limitations

The model is pretrained on general video interpolation data, not a calibrated
satellite or disaster-monitoring dataset. PNG/JPEG only; GeoTIFF, HDF,
multi-band, radiometric, and geospatial metadata support is deferred. The
confidence map is a consistency proxy, not a probability. No real-time claim
is made. No disaster prediction is implemented. No satellite imagery is
bundled or fabricated.

## Future fine-tuning plan

`ml/data/dataset.py`, `ml/scripts/train.py`, and `ml/scripts/validate.py` are
importable scaffolds with `TRAINING_ENABLED = False`. A future dataset should
split by sequence/date/event so frames from one sequence never leak across
train, validation, and test sets. Training has not been started in v1.

## Upstream dependency

The runtime backbone is the PyTorch `megvii-research/ECCV2022-RIFE` source,
not the MegEngine sibling repository and not Practical-RIFE. Upstream script
inspection confirmed `inference_img.py --img img0.png img1.png --exp=N`; FrameFlow
uses its `train_log/flownet.pkl` checkpoint through a smaller project adapter.
