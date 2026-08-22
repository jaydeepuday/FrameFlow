import os
import glob
import json
import xarray as xr
import numpy as np
import cv2
import torch
import matplotlib.pyplot as plt
from ml.rife.wrapper import RIFEWrapper
from ml.evaluation.evaluate import evaluate_prediction
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Load Data
raw_files = sorted(glob.glob('data/satellite/raw/goes16_b13/*.nc'))
if len(raw_files) < 3:
    raise Exception("Need at least 3 .nc files")

triplet = raw_files[:3]

def extract_crop(path):
    ds = xr.open_dataset(path)
    cmi = ds['CMI'].values
    cmi_crop = cmi[500:1012, 1000:1512]  # 512x512 crop for speed & memory
    ds.close()
    return cmi_crop

print("Extracting crops...")
t0_cmi = extract_crop(triplet[0])
t1_cmi = extract_crop(triplet[1])
t2_cmi = extract_crop(triplet[2])

print(f"Source shape: {t0_cmi.shape}")
print(f"Valid Data Range: [{np.nanmin(t0_cmi):.2f}, {np.nanmax(t0_cmi):.2f}] Kelvin")

# Handle missing values & Normalize
VMIN, VMAX = 180.0, 330.0

def prep_for_rife(cmi):
    cmi_clean = np.nan_to_num(cmi, nan=VMAX)
    norm = (cmi_clean - VMIN) / (VMAX - VMIN)
    norm = np.clip(norm, 0.0, 1.0)
    tensor_1c = torch.from_numpy(norm).float().unsqueeze(0) # [1, H, W]
    tensor_3c = tensor_1c.repeat(3, 1, 1).unsqueeze(0) # [1, 3, H, W]
    return tensor_3c

t0_t = prep_for_rife(t0_cmi).cuda()
t2_t = prep_for_rife(t2_cmi).cuda()

# Optional: modulo 32 padding if needed (512 is multiple of 32)
# model execution
print("Running RIFE HDv3...")
model = RIFEWrapper(device_override="cuda")
with torch.no_grad():
    pred_norm = model.model.inference(t0_t, t2_t)

# Reverse normalization
def denorm(tensor_3c):
    # tensor is [1, 3, H, W]
    norm_1c = tensor_3c[0, 0, :, :].cpu().numpy() # Extract single channel
    return norm_1c * (VMAX - VMIN) + VMIN

pred_t1_cmi_rife = denorm(pred_norm)

# Linear Baseline
pred_t1_cmi_linear = (t0_cmi + t2_cmi) / 2.0

# Evaluation against GT
# Data Range for PSNR/SSIM must be dynamically defined (VMAX - VMIN)
data_range = VMAX - VMIN

def eval_physical(pred, gt):
    # Mask out NaNs in GT
    mask = ~np.isnan(gt)
    p = pred[mask]
    g = gt[mask]
    mae = mean_absolute_error(g, p)
    rmse = np.sqrt(mean_squared_error(g, p))
    psnr = peak_signal_noise_ratio(gt, pred, data_range=data_range)
    ssim = structural_similarity(gt, pred, data_range=data_range)
    return {"mae_kelvin": mae, "rmse_kelvin": rmse, "psnr_dB": psnr, "ssim": ssim}

metrics_rife = eval_physical(pred_t1_cmi_rife, t1_cmi)
metrics_linear = eval_physical(pred_t1_cmi_linear, t1_cmi)

# Validation outputs
out_dir = 'outputs/evaluation'
os.makedirs(out_dir, exist_ok=True)

report = {
    "dataset": "GOES-16 ABI-L2-CMIPC",
    "band": 13,
    "wavelength": "10.3 um (Clean IR)",
    "units": "Kelvin (Brightness Temperature)",
    "scale": "Applied natively in netCDF metadata (xarray decoded)",
    "valid_range": f"[{VMIN}, {VMAX}] K",
    "missing_value_handling": "NaNs converted to VMAX prior to processing",
    "spatial_resolution": "2 km nominal at nadir (512x512 crop extracted)",
    "temporal_spacing": "10 minutes",
    "rife_input_representation": "Kelvin scaled to [0,1], replicated 3x across pseudo-RGB channels",
    "rife": metrics_rife,
    "linear": metrics_linear,
    "files": triplet
}

with open(os.path.join(out_dir, 'band13_experiment.json'), 'w') as f:
    json.dump(report, f, indent=2)

# Visualization
print("Generating Visualizations...")
def plot_thermal(cmi, title, fname):
    plt.imshow(cmi, cmap='nipy_spectral', vmin=180, vmax=330)
    plt.colorbar(label='Kelvin')
    plt.title(title)
    plt.savefig(os.path.join(out_dir, fname))
    plt.close()

plot_thermal(t0_cmi, 'T0 Band 13', 'satellite_band13_t0.png')
plot_thermal(t1_cmi, 'GT T1 Band 13', 'satellite_band13_ground_truth.png')
plot_thermal(pred_t1_cmi_rife, 'RIFE T1 Band 13', 'satellite_band13_rife.png')
plot_thermal(pred_t1_cmi_linear, 'Linear T1 Band 13', 'satellite_band13_linear.png')

# Error map
err_rife = np.abs(pred_t1_cmi_rife - t1_cmi)
plt.imshow(err_rife, cmap='hot', vmin=0, vmax=10)
plt.colorbar(label='Absolute Error (K)')
plt.title('RIFE Absolute Error')
plt.savefig(os.path.join(out_dir, 'satellite_band13_error_map.png'))
plt.close()

print(json.dumps(report, indent=2))
print("Evaluated.")
