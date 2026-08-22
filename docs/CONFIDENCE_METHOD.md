# Interpolation Confidence Proxy

## Methodology
To evaluate the relative reliability of PyTorch RIFE's interpolation between two frames, we calculate a **Confidence / Uncertainty Estimate** driven by mathematical consistency rather than an arbitrary heatmap.

The algorithm leverages the internal dense optical flow (`flownet`) already derived by RIFE to warp `Frame 0` and `Frame 1` to the estimated midpoint ($t=0.5$).

**Steps:**
1. Feed $I_{0}$ and $I_{1}$ to RIFE and retrieve bidirectional optical flow fields $F_{0 \rightarrow 0.5}$ and $F_{1 \rightarrow 0.5}$.
2. Use RIFE's `warp` layer to produce interpolated estimates: $\hat{I}_{0}$ (from $I_0$) and $\hat{I}_{1}$ (from $I_1$).
3. Calculate the absolute pixel-wise reconstruction residual: $\Delta = |\hat{I}_0 - \hat{I}_1|$.
4. If $\Delta$ is high, it heavily implies structural discrepancy (e.g. extreme motion occlusion, newly uncovered background, or simply failed modeling interpolation). 

## Output Generation
The residual $\Delta$ is translated to a `(0, 1)` map (where $1$ is high confidence) utilizing exponential decay $C = \exp(\frac{-\Delta}{\sigma})$, yielding a `confidence_map`. We further output global metrics `mean_confidence` and `low_confidence_fraction` designed specifically for UI thresholds.

*Note:* This proxy represents mathematical warping consistency, not calibrated probabilistic uncertainty. It should solely be utilized to highlight regions where interpolation physics struggled.
