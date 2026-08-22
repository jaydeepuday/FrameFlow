# Architecture

```text
PNG/JPEG T0 + T1
       ↓
preprocessing adapter (RGB, validation, fit/pad, BCHW tensor)
       ↓
official PyTorch ECCV2022-RIFE HDv3 adapter (one lazy process-level load)
       ↓
AI GENERATED T0.5 + run telemetry
       ├── comparison.png
       ├── consistency confidence_map.png
       └── optional Farneback Optical Flow Visualization
       ↓
FastAPI /api/interpolate
       ↓
React/Vite dashboard
```

`ml/models/rife/upstream/` contains the inspected official PyTorch source and
`models/rife/train_log/` contains the externally supplied checkpoint. The
adapter only exposes midpoint inference; it does not modify RIFE internals or
pretend that classical optical flow is RIFE's internal flow.

