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
from ml.preprocessing.normalization import pad_for_rife

def benchmark_inference(device_str, input0, input1, N_warmup=3, N_runs=5):
    model = RIFEWrapper(device_override=device_str)
    
    for _ in range(N_warmup):
        model.interpolate(input0, input1, 0.5)
        if device_str == 'cuda':
            torch.cuda.synchronize()
            
    times = []
    for _ in range(N_runs):
        start = time.time()
        model.interpolate(input0, input1, 0.5)
        if device_str == 'cuda':
            torch.cuda.synchronize()
        times.append((time.time() - start) * 1000)
        
    return {
        "average": float(np.mean(times)),
        "min": float(np.min(times)),
        "max": float(np.max(times)),
        "device_actual": str(next(model.model.flownet.parameters()).device)
    }

synthetic_f0 = 'data/samples/frame_000.png'
synthetic_f1 = 'data/samples/frame_001.png'
synthetic_f2 = 'data/samples/frame_002.png'

natural_f0 = 'data/temporal_benchmark/frame_000.png'
natural_f1 = 'data/temporal_benchmark/frame_001.png'
natural_f2 = 'data/temporal_benchmark/frame_002.png'

print("Generating Natural Triplet...")
from skimage import data
img = data.astronaut() 
os.makedirs('data/temporal_benchmark', exist_ok=True)
cv2.imwrite(natural_f0, cv2.cvtColor(img[100:228, 100:228], cv2.COLOR_RGB2BGR))
cv2.imwrite(natural_f1, cv2.cvtColor(img[100:228, 110:238], cv2.COLOR_RGB2BGR))
cv2.imwrite(natural_f2, cv2.cvtColor(img[100:228, 120:248], cv2.COLOR_RGB2BGR))

report = {
    "synthetic_sanity": {},
    "temporal_benchmark": {},
    "runtime": {}
}

os.makedirs('ml/outputs', exist_ok=True)

res_linear_synth_path = 'ml/outputs/synth_linear.png'
cv2.imwrite(res_linear_synth_path, linear_interpolate(synthetic_f0, synthetic_f2, 0.5))
res_linear_synth = evaluate_prediction(cv2.imread(res_linear_synth_path, cv2.IMREAD_UNCHANGED), cv2.imread(synthetic_f1, cv2.IMREAD_UNCHANGED))
res_rife_synth = interpolate(synthetic_f0, synthetic_f2, 0.5, device="cuda")
res_rife_synth_eval = evaluate_prediction(cv2.imread(res_rife_synth["output_path"], cv2.IMREAD_UNCHANGED), cv2.imread(synthetic_f1, cv2.IMREAD_UNCHANGED))

report["synthetic_sanity"] = {
    "linear": res_linear_synth,
    "rife": res_rife_synth_eval
}

res_linear_nat_path = 'ml/outputs/nat_linear.png'
cv2.imwrite(res_linear_nat_path, linear_interpolate(natural_f0, natural_f2, 0.5))
res_linear_nat = evaluate_prediction(cv2.imread(res_linear_nat_path, cv2.IMREAD_UNCHANGED), cv2.imread(natural_f1, cv2.IMREAD_UNCHANGED))
res_rife_nat = interpolate(natural_f0, natural_f2, 0.5, device="cuda")
res_rife_nat_eval = evaluate_prediction(cv2.imread(res_rife_nat["output_path"], cv2.IMREAD_UNCHANGED), cv2.imread(natural_f1, cv2.IMREAD_UNCHANGED))

report["temporal_benchmark"] = {
    "dataset": "Natural-image temporal interpolation benchmark — not satellite validation",
    "dataset_source": "skimage astronaut",
    "temporal_spacing": "10 pixels panning translation",
    "image_dimensions": "128x128x3",
    "metric_data_range": "0-255 uint8",
    "linear": res_linear_nat,
    "rife": res_rife_nat_eval
}

print("Running CPU/GPU inference benchmarking...")
report["runtime"]["gpu"] = benchmark_inference("cuda", natural_f0, natural_f2, 5, 20)
report["runtime"]["cpu"] = benchmark_inference("cpu", natural_f0, natural_f2, 2, 5)

os.makedirs('outputs/evaluation', exist_ok=True)
with open('outputs/evaluation/final_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Generating Visual Comparison...")
model = RIFEWrapper(device_override="cuda")
img0_t = torch.from_numpy(cv2.imread(natural_f0, cv2.IMREAD_UNCHANGED).transpose(2,0,1)).float().unsqueeze(0)/255.0
img2_t = torch.from_numpy(cv2.imread(natural_f2, cv2.IMREAD_UNCHANGED).transpose(2,0,1)).float().unsqueeze(0)/255.0
img0_p, pad = pad_for_rife(img0_t.cuda())
img2_p, _ = pad_for_rife(img2_t.cuda())
cmap, _, _ = estimate_confidence(model.model, img0_p, img2_p)

os.makedirs('ml/outputs/evaluation', exist_ok=True)
plt.imsave('ml/outputs/evaluation/confidence_map.png', cmap, cmap='hot')

fig, axes = plt.subplots(1, 5, figsize=(20, 4))
axes[0].imshow(cv2.cvtColor(cv2.imread(natural_f0), cv2.COLOR_BGR2RGB)); axes[0].set_title('Frame 0')
axes[1].imshow(cv2.cvtColor(cv2.imread(natural_f1), cv2.COLOR_BGR2RGB)); axes[1].set_title('Ground Truth 1')
axes[2].imshow(cv2.cvtColor(cv2.imread(res_rife_nat["output_path"]), cv2.COLOR_BGR2RGB)); axes[2].set_title('RIFE Prediction')
axes[3].imshow(cv2.cvtColor(cv2.imread(res_linear_nat_path), cv2.COLOR_BGR2RGB)); axes[3].set_title('Linear Prediction')
axes[4].imshow(cv2.cvtColor(cv2.imread(natural_f2), cv2.COLOR_BGR2RGB)); axes[4].set_title('Frame 2')
plt.savefig('ml/outputs/evaluation/visual_comparison.png')
plt.close()

print("Done!")
