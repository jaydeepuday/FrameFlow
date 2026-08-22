# Evaluation Metrics and Baseline

## Temporal Framework
Evaluations calculate the quality of an interpolated midpoint ($t=0.5$) using $I_0$ and $I_2$ compared directly against a known ground-truth $I_1$.

## Metrics Implemented
- **MAE (Mean Absolute Error):** Core pixel-wise accuracy index.
- **PSNR (Peak Signal-to-Noise Ratio):** Standard noise reflection ratio.
- **SSIM (Structural Similarity Index):** Human-perception aligned structural analysis.
- **Inference Time:** Hardware runtime tracked in ms.

## Linear Baseline
Evaluated precisely against naive classical $\frac{I_0 + I_2}{2}$ interpolations to measure the distinct value-add of the RIFE neural architecture. Expected to drastically outperform classical linear blending due to flow-awareness.
