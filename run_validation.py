import json
import time
import os
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from ml.evaluation.evaluate import evaluate_prediction
from ml.baselines.linear import linear_interpolate
from ml.rife.wrapper import RIFEWrapper
from ml.confidence.confidence import estimate_confidence
from ml.preprocessing.satellite import preprocess_satellite_image
from ml.preprocessing.image_loader import load_satellite_image

seq_dir = 'data/satellite/validation/sequence_001'
sat_f0 = f'{seq_dir}/frame_000.jpg'
sat_f1 = f'{seq_dir}/frame_001.jpg'
sat_f2 = f'{seq_dir}/frame_002.jpg'

print(f"T0: {os.path.abspath(sat_f0)}")
print(f"GT T1: {os.path.abspath(sat_f1)}")
print(f"T2: {os.path.abspath(sat_f2)}")

img0_padded, _, shape0 = preprocess_satellite_image(sat_f0, "cuda")
img2_padded, _, _ = preprocess_satellite_image(sat_f2, "cuda")
gt_img = load_satellite_image(sat_f1)
h, w, c = shape0[0], shape0[1], gt_img.shape[2]
dtype = gt_img.dtype

print(f"Dimensions: {w}x{h}")
print(f"Channels: {c}")
print(f"DType: {dtype}")

model = RIFEWrapper(device_override="cuda")
with torch.no_grad():
    mid = model.model.inference(img0_padded, img2_padded)
    rife_out = (mid[0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:h, :w]
res_rife_eval = evaluate_prediction(rife_out, gt_img)

linear_out = linear_interpolate(sat_f0, sat_f2, 0.5)
res_linear_eval = evaluate_prediction(linear_out, gt_img)

cmap, _, _ = estimate_confidence(model.model, img0_padded, img2_padded)
cmap = cmap[:h, :w]

out_dir = 'outputs/evaluation'
os.makedirs(out_dir, exist_ok=True)
cv2.imwrite(f"{out_dir}/satellite_sequence_001_rife.png", cv2.cvtColor(rife_out, cv2.COLOR_RGB2BGR))
cv2.imwrite(f"{out_dir}/satellite_sequence_001_linear.png", cv2.cvtColor(linear_out, cv2.COLOR_RGB2BGR))
cv2.imwrite(f"{out_dir}/satellite_sequence_001_ground_truth.png", cv2.cvtColor(gt_img, cv2.COLOR_RGB2BGR))
plt.imsave(f"{out_dir}/satellite_sequence_001_confidence.png", cmap, cmap='hot')

fig, axes = plt.subplots(1, 5, figsize=(25, 5))
axes[0].imshow(load_satellite_image(sat_f0)); axes[0].set_title('T0')
axes[1].imshow(gt_img); axes[1].set_title('GT T1')
axes[2].imshow(rife_out); axes[2].set_title('RIFE T1')
axes[3].imshow(linear_out); axes[3].set_title('Linear T1')
axes[4].imshow(load_satellite_image(sat_f2)); axes[4].set_title('T2')
plt.savefig(f"{out_dir}/satellite_sequence_001_comparison.png")
plt.close()

report = {
    "dataset": "GOES-East / Hurricane Ian",
    "sequence": "sequence_001",
    "type": "Real satellite validation",
    "verification": {
        "dimensions": f"{w}x{h}",
        "channels": c,
        "dtype": str(dtype),
        "metric_data_range": "255.0",
        "alignment": "Extracted linearly from geostationary ABI bounds",
        "files": [sat_f0, sat_f1, sat_f2]
    },
    "rife": res_rife_eval,
    "linear": res_linear_eval
}

with open(f"{out_dir}/satellite_sequence_001.json", 'w') as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
