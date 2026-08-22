# Evaluation

When a true middle frame is available, `ml/evaluation/evaluate.py` computes:

- MAE on normalized RGB pixels.
- PSNR from normalized RGB mean squared error.
- SSIM using scikit-image when installed, with a documented global-SSIM
  fallback so the evaluation command remains usable in a minimal environment.

`ml/evaluation/baseline.py` evaluates the RIFE result and the classical linear
midpoint `0.5*T0 + 0.5*T1` using the same metrics. Without ground truth the
command prints exactly: `Ground truth unavailable — qualitative evaluation
only.` No fabricated values are emitted.

