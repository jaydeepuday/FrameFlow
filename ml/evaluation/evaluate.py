import argparse
import sys
import os
import time
import cv2
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
ml_dir = os.path.abspath(os.path.join(current_dir, '..'))
if ml_dir not in sys.path:
    sys.path.append(ml_dir)

from skimage.metrics import peak_signal_noise_ratio as compute_psnr
from skimage.metrics import structural_similarity as compute_ssim
import numpy as np

def evaluate_prediction(predicted_img_np, ground_truth_img_np):
    """
    Computes MAE, PSNR, and SSIM between two normalized RGB numpy images.
    Returns dictionary with metrics.
    """
    if predicted_img_np.shape != ground_truth_img_np.shape:
        raise ValueError(f"Predicted shape {predicted_img_np.shape} and ground truth shape {ground_truth_img_np.shape} must match")
        
    try:
        # Ensure we are evaluating on RGB dimension structures
        if len(ground_truth_img_np.shape) == 2:
            ground_truth_img_np = cv2.cvtColor(ground_truth_img_np, cv2.COLOR_GRAY2RGB)
            predicted_img_np = cv2.cvtColor(predicted_img_np, cv2.COLOR_GRAY2RGB)
            
        psnr = compute_psnr(ground_truth_img_np, predicted_img_np, data_range=255.0)
        ssim = compute_ssim(ground_truth_img_np, predicted_img_np, channel_axis=2, data_range=255.0)
        mae = np.mean(np.abs(predicted_img_np.astype(float) - ground_truth_img_np.astype(float)))
        
        return {
            "mae": float(mae),
            "psnr": float(psnr),
            "ssim": float(ssim)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    from inference.interpolate import interpolate
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame0", required=True)
    parser.add_argument("--ground-truth", required=False)
    parser.add_argument("--frame2", required=True)
    parser.add_argument("--device", default="auto")
    
    args = parser.parse_args()
    
    result = interpolate(args.frame0, args.frame2, timestep=0.5, device=args.device)
    
    if not args.ground_truth or not os.path.exists(args.ground_truth):
        print("Ground truth unavailable — qualitative evaluation only.")
        sys.exit(0)
        
    gt = cv2.imread(args.ground_truth, cv2.IMREAD_UNCHANGED)
        
    pred_path = result["output_path"]
    pred = cv2.imread(pred_path, cv2.IMREAD_UNCHANGED)
    
    metrics = evaluate_prediction(pred, gt)
    metrics["inference_time_ms"] = result["inference_time_ms"]
    metrics["device"] = result["device"]
    
    print(json.dumps(metrics, indent=2))
