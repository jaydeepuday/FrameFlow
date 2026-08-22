import os
import glob
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import torch
from ml.rife.wrapper import RIFEWrapper
from ml.evaluation.evaluate import evaluate_prediction
from ml.baselines.linear import linear_interpolate
from ml.confidence.confidence import estimate_confidence
from ml.preprocessing.satellite import preprocess_satellite_image
from ml.preprocessing.image_loader import load_satellite_image

out_dir = 'outputs/evaluation'
os.makedirs(out_dir, exist_ok=True)

seq_dirs = sorted(glob.glob('data/satellite/validation/sequence_*'))

model = RIFEWrapper(device_override="cuda")

results = []

for seq_dir in seq_dirs:
    seq_name = os.path.basename(seq_dir)
    print(f"Evaluating {seq_name}...")
    
    sat_f0 = f'{seq_dir}/frame_000.jpg'
    sat_f1 = f'{seq_dir}/frame_001.jpg'
    sat_f2 = f'{seq_dir}/frame_002.jpg'
    
    img0_padded, _, shape0 = preprocess_satellite_image(sat_f0, "cuda")
    img2_padded, _, _ = preprocess_satellite_image(sat_f2, "cuda")
    gt_img = load_satellite_image(sat_f1)
    h, w = shape0[0], shape0[1]
    
    with torch.no_grad():
        mid = model.model.inference(img0_padded, img2_padded)
        rife_out = (mid[0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:h, :w]
    res_rife_eval = evaluate_prediction(rife_out, gt_img)
    
    linear_out = linear_interpolate(sat_f0, sat_f2, 0.5)
    res_linear_eval = evaluate_prediction(linear_out, gt_img)
    
    cmap, _, _ = estimate_confidence(model.model, img0_padded, img2_padded)
    cmap = cmap[:h, :w]
    
    # Save visuals for each
    cv2.imwrite(f"{out_dir}/{seq_name}_rife.png", cv2.cvtColor(rife_out, cv2.COLOR_RGB2BGR))
    cv2.imwrite(f"{out_dir}/{seq_name}_linear.png", cv2.cvtColor(linear_out, cv2.COLOR_RGB2BGR))
    cv2.imwrite(f"{out_dir}/{seq_name}_ground_truth.png", cv2.cvtColor(gt_img, cv2.COLOR_RGB2BGR))
    plt.imsave(f"{out_dir}/{seq_name}_confidence.png", cmap, cmap='hot')
    
    fig, axes = plt.subplots(1, 5, figsize=(25, 5))
    axes[0].imshow(load_satellite_image(sat_f0)); axes[0].set_title('T0')
    axes[1].imshow(gt_img); axes[1].set_title('GT T1')
    axes[2].imshow(rife_out); axes[2].set_title('RIFE T1')
    axes[3].imshow(linear_out); axes[3].set_title('Linear T1')
    axes[4].imshow(load_satellite_image(sat_f2)); axes[4].set_title('T2')
    plt.savefig(f"{out_dir}/{seq_name}_comparison.png")
    plt.close()
    
    seq_report = {
        "sequence": seq_name,
        "rife": res_rife_eval,
        "linear": res_linear_eval
    }
    results.append(seq_report)

# Aggregate
r_mae, r_psnr, r_ssim = [], [], []
l_mae, l_psnr, l_ssim = [], [], []

for r in results:
    r_mae.append(r["rife"]["mae"])
    r_psnr.append(r["rife"]["psnr"])
    r_ssim.append(r["rife"]["ssim"])
    
    l_mae.append(r["linear"]["mae"])
    l_psnr.append(r["linear"]["psnr"])
    l_ssim.append(r["linear"]["ssim"])

rife_better_mae = sum(1 for i in range(len(results)) if r_mae[i] < l_mae[i])
rife_better_psnr = sum(1 for i in range(len(results)) if r_psnr[i] > l_psnr[i])
rife_better_ssim = sum(1 for i in range(len(results)) if r_ssim[i] > l_ssim[i])

agg_report = {
    "number_of_sequences": len(results),
    "mean_MAE": {"rife": float(np.mean(r_mae)), "linear": float(np.mean(l_mae))},
    "median_MAE": {"rife": float(np.median(r_mae)), "linear": float(np.median(l_mae))},
    "std_MAE": {"rife": float(np.std(r_mae)), "linear": float(np.std(l_mae))},
    "mean_PSNR": {"rife": float(np.mean(r_psnr)), "linear": float(np.mean(l_psnr))},
    "median_PSNR": {"rife": float(np.median(r_psnr)), "linear": float(np.median(l_psnr))},
    "std_PSNR": {"rife": float(np.std(r_psnr)), "linear": float(np.std(l_psnr))},
    "mean_SSIM": {"rife": float(np.mean(r_ssim)), "linear": float(np.mean(l_ssim))},
    "median_SSIM": {"rife": float(np.median(r_ssim)), "linear": float(np.median(l_ssim))},
    "std_SSIM": {"rife": float(np.std(r_ssim)), "linear": float(np.std(l_ssim))},
    "percentage_rife_better_mae": float(rife_better_mae / len(results)) * 100,
    "percentage_rife_better_psnr": float(rife_better_psnr / len(results)) * 100,
    "percentage_rife_better_ssim": float(rife_better_ssim / len(results)) * 100,
    "per_sequence": results
}

with open(f"{out_dir}/satellite_multi_sequence_report.json", 'w') as f:
    json.dump(agg_report, f, indent=2)

import csv
with open(f"{out_dir}/satellite_multi_sequence_summary.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Sequence', 'RIFE_MAE', 'RIFE_PSNR', 'RIFE_SSIM', 'Linear_MAE', 'Linear_PSNR', 'Linear_SSIM'])
    for r in results:
        writer.writerow([r['sequence'], r['rife']['mae'], r['rife']['psnr'], r['rife']['ssim'], r['linear']['mae'], r['linear']['psnr'], r['linear']['ssim']])
    writer.writerow(['MEAN', float(np.mean(r_mae)), float(np.mean(r_psnr)), float(np.mean(r_ssim)), float(np.mean(l_mae)), float(np.mean(l_psnr)), float(np.mean(l_ssim))])

print("Evaluation complete.")
