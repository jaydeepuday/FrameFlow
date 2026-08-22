import json
import time
import os
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from ml.evaluation.evaluate import evaluate_prediction
from ml.baselines.linear import linear_interpolate
from ml.inference.interpolate import interpolate
from ml.rife.wrapper import RIFEWrapper
from ml.confidence.confidence import estimate_confidence
from ml.preprocessing.satellite import preprocess_satellite_image
from ml.preprocessing.image_loader import load_satellite_image

sat_f0 = 'data/satellite/validation/sequence_001/frame_000.jpg'
sat_f1 = 'data/satellite/validation/sequence_001/frame_001.jpg'
sat_f2 = 'data/satellite/validation/sequence_001/frame_002.jpg'

print("Loading Satellite Triplet...")
img0_padded, pad0, shape0 = preprocess_satellite_image(sat_f0, "cuda")
img2_padded, pad2, shape2 = preprocess_satellite_image(sat_f2, "cuda")
gt_img = load_satellite_image(sat_f1)
h, w = shape0[0], shape0[1]

print("Evaluating RIFE...")
model = RIFEWrapper(device_override="cuda")
with torch.no_grad():
    mid = model.model.inference(img0_padded, img2_padded)
    out = (mid[0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:h, :w]
res_rife_eval = evaluate_prediction(out, gt_img)

print("Evaluating Linear...")
res_linear_path = 'ml/outputs/satellite_evaluation/sat_linear.png'
os.makedirs('ml/outputs/satellite_evaluation', exist_ok=True)
linear_out = linear_interpolate(sat_f0, sat_f2, 0.5)
cv2.imwrite(res_linear_path, cv2.cvtColor(linear_out, cv2.COLOR_RGB2BGR))
res_linear_eval = evaluate_prediction(linear_out, gt_img)

# Compute Confidence
print("Computing Confidence...")
cmap, mean_conf, low_frac = estimate_confidence(model.model, img0_padded, img2_padded)
cmap = cmap[:h, :w]
plt.imsave('ml/outputs/satellite_evaluation/confidence_map.png', cmap, cmap='hot')

# Save Visuals
print("Generating Visual Comparison...")
fig, axes = plt.subplots(1, 5, figsize=(25, 5))
axes[0].imshow(load_satellite_image(sat_f0)); axes[0].set_title('Frame 0')
axes[1].imshow(gt_img); axes[1].set_title('Ground Truth 1')
axes[2].imshow(out); axes[2].set_title('RIFE Prediction')
axes[3].imshow(linear_out); axes[3].set_title('Linear Prediction')
axes[4].imshow(load_satellite_image(sat_f2)); axes[4].set_title('Frame 2')
plt.tight_layout()
plt.savefig('ml/outputs/satellite_evaluation/visual_comparison.png')
plt.close()

report = {
    "dataset": "NOAA GOES-16 ABI CONUS GEOCOLOR",
    "temporal_spacing": "10 Minutes",
    "spatial_resolution": "1000x1000",
    "rife": res_rife_eval,
    "linear": res_linear_eval
}

with open('outputs/evaluation/satellite_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Satellite Validation Complete.")
print(json.dumps(report, indent=2))
