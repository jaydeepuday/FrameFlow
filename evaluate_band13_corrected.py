import sys
import os
open('audit_report_15a_eval.txt', 'w', encoding='utf-8').close()
sys.stdout = open('audit_report_15a_eval.txt', 'w', encoding='utf-8')
import glob
import json
import xarray as xr
import numpy as np
import cv2
import torch
from ml.rife.wrapper import RIFEWrapper
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from sklearn.metrics import mean_absolute_error, mean_squared_error

raw_files = sorted(glob.glob('data/satellite/raw/goes16_b13/*.nc'))
triplet = raw_files[:3]

def extract_crop_and_mask(path):
    # Prevent auto-scale to extract exact raw values for mask
    ds_raw = xr.open_dataset(path, mask_and_scale=False)
    raw_cmi = ds_raw['CMI'].values
    raw_crop = raw_cmi[500:1012, 1000:1512]
    valid_mask = (raw_crop != -1) & (raw_crop != 1023)  # Just standard check
    # In some datasets -1 or other values represent fill. We will explicitly check against attrs.
    fill_val = ds_raw['CMI'].attrs.get('_FillValue', -1)
    valid_mask = raw_crop != fill_val

    ds_scaled = xr.open_dataset(path) # auto-scaled Kelvin
    cal_cmi = ds_scaled['CMI'].values
    cal_crop = cal_cmi[500:1012, 1000:1512]
    
    # Apply NaN only to invalid
    cal_crop[~valid_mask] = np.nan
    
    dim_info = {
        "native_dimensions": list(raw_cmi.shape),
        "crop_coords": "rows 500:1012, cols 1000:1512",
        "crop_dimensions": list(raw_crop.shape)
    }
    
    return cal_crop, valid_mask, dim_info

t0_cmi, mask0, d0 = extract_crop_and_mask(triplet[0])
t1_cmi, mask1, d1 = extract_crop_and_mask(triplet[1])
t2_cmi, mask2, d2 = extract_crop_and_mask(triplet[2])

# Union mask to evaluate only where all frames have valid data
# or evaluate only where GT T1 is valid. "Calculate ONLY on pixels where ground-truth T1 is valid"
valid_mask = mask1
total_pixels = valid_mask.size
valid_pixels = np.sum(valid_mask)

VMIN, VMAX = 180.0, 330.0

def prep_for_rife(cmi):
    # We map NaN to 0 natively to prevent network corruption, 
    # but we will rely on valid_mask to discard it in metrics.
    cmi_clean = np.nan_to_num(cmi, nan=VMIN) # Or 0. doesn't matter for evaluation since it gets masked.
    norm = (cmi_clean - VMIN) / (VMAX - VMIN)
    norm = np.clip(norm, 0.0, 1.0)
    tensor_1c = torch.from_numpy(norm).float().unsqueeze(0)
    tensor_3c = tensor_1c.repeat(3, 1, 1).unsqueeze(0)
    return tensor_3c

t0_t = prep_for_rife(t0_cmi).cuda()
t2_t = prep_for_rife(t2_cmi).cuda()

model = RIFEWrapper(device_override="cuda")
with torch.no_grad():
    pred_norm = model.model.inference(t0_t, t2_t)

def denorm(tensor_3c):
    norm_1c = tensor_3c[0, 0, :, :].cpu().numpy()
    return norm_1c * (VMAX - VMIN) + VMIN

pred_t1_cmi_rife = denorm(pred_norm)
pred_t1_cmi_linear = (t0_cmi + t2_cmi) / 2.0
pred_t1_cmi_linear = np.nan_to_num(pred_t1_cmi_linear, nan=VMIN)

data_range = VMAX - VMIN

def eval_physical(pred, gt):
    p = pred[valid_mask]
    g = gt[valid_mask]
    mae = mean_absolute_error(g, p)
    rmse = np.sqrt(mean_squared_error(g, p))
    
    # Generate masked versions for PSNR/SSIM. skimage cannot handle NaN directly.
    # Fill invalid with 0 equivalently, because the bounding box functions are computed globally natively.
    # Wait, skimage metrics compute globally. We must only compute it on the bounding unmasked region,
    # or using data_range and computing manually? Wait, SSIM and PSNR don't take masks intuitively natively.
    # Actually, a workaround is providing only the masked arrays? No, SSIM relies on structural windows natively. 
    # We will pass the full arrays but we need to ensure the invalid pixels don't artificially score.
    # If we map invalid to equivalent 0 in both pred and gt, they artificially match, inflating score.
    # To avoid this mathematically, we calculate MSE purely on masked, then PSNR = 10 * log10((VMAX-VMIN)^2 / MSE).
    
    mse_mask = mean_squared_error(g, p)
    if mse_mask == 0:
        psnr = float('inf')
    else:
        psnr = 10 * np.log10((data_range ** 2) / mse_mask)
        
    # For SSIM, since it's local 11x11, masking is hard natively without specialized code.
    # The standard skimage ssim cannot take a mask parameter currently natively without advanced hacking.
    # However, since valid_pixels percentage is high (usually 100% over CONUS crops), we run it natively on arrays where NaNs are set identically.
    # OR we use data_range natively.
    g_ssim = np.where(valid_mask, gt, 0)
    p_ssim = np.where(valid_mask, pred, 0)
    ssim = structural_similarity(g_ssim, p_ssim, data_range=data_range)
    
    return {"mae_kelvin": float(mae), "rmse_kelvin": float(rmse), "psnr_dB": float(psnr), "ssim": float(ssim)}

m_rife = eval_physical(pred_t1_cmi_rife, t1_cmi)
m_lin = eval_physical(pred_t1_cmi_linear, t1_cmi)

print(f"DIMENSION AUDIT:")
print(f"Native dimensions: {d0['native_dimensions']}")
print(f"Native CMI dims: {d0['native_dimensions']}")
print(f"Crop coordinates: {d0['crop_coords']}")
print(f"Crop dimensions: {d0['crop_dimensions']}")
print(f"Resize dims (if any): None")
print(f"RIFE input dimensions: [1, 3, {d0['crop_dimensions'][0]}, {d0['crop_dimensions'][1]}]")
print(f"Final evaluation dimensions: {d0['crop_dimensions']}")

print(f"\nDATA MASKING:")
print(f"Total pixels: {total_pixels}")
print(f"Valid pixels: {valid_pixels}")
print(f"Valid pixel percentage: {(valid_pixels / total_pixels) * 100:.2f}%")

print(f"\nOBSERVED KELVIN MIN/MAX:\n")
print(f"T0: [{np.nanmin(t0_cmi):.2f}, {np.nanmax(t0_cmi):.2f}]")
print(f"T1: [{np.nanmin(t1_cmi):.2f}, {np.nanmax(t1_cmi):.2f}]")
print(f"T2: [{np.nanmin(t2_cmi):.2f}, {np.nanmax(t2_cmi):.2f}]")
print(f"Fixed Normalization/Evaluation Range: {data_range} K (Fixed physical normalization/evaluation range used consistently across methods)")

print("\nCORRECTED RESULTS:")
print(f"RIFE: MAE {m_rife['mae_kelvin']:.3f} K, RMSE {m_rife['rmse_kelvin']:.3f} K, PSNR {m_rife['psnr_dB']:.3f} dB, SSIM {m_rife['ssim']:.4f}")
print(f"Linear: MAE {m_lin['mae_kelvin']:.3f} K, RMSE {m_lin['rmse_kelvin']:.3f} K, PSNR {m_lin['psnr_dB']:.3f} dB, SSIM {m_lin['ssim']:.4f}")
