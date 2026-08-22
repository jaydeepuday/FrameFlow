import torch
import numpy as np
import sys
import os

# Ensure root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from ml.rife.model.warplayer import warp

def estimate_confidence(rife_model, img0_tensor, img1_tensor):
    """
    Estimates an Interpolation Confidence Proxy using reconstruction residual.
    
    Mechanism:
    1. Computes the optical flow from RIFE.
    2. Warps both input frames to the t=0.5 midpoint using their respective flow fields.
    3. Computes the absolute pixel-wise difference between the two warped frames.
    4. High difference implies structural inconsistency (occlusion or failure), yielding lower confidence.
    
    Returns:
    - confidence_map: (H, W) numpy array [0, 1] (0 = low, 1 = high)
    - mean_confidence: float
    - low_confidence_fraction: float
    """
    with torch.no_grad():
        imgs = torch.cat((img0_tensor, img1_tensor), 1)
        
        # RIFE flownet returns flow, mask, merged_image
        # flow length is 3 (for different scales). Index 2 is the full resolution flow.
        flow, mask, merged = rife_model.flownet(imgs, [4.0, 2.0, 1.0])
        
        final_flow = flow[2]
        
        # final_flow has 4 channels: [0:2] for F_{0->t}, [2:4] for F_{1->t}
        flow0 = final_flow[:, :2]
        flow1 = final_flow[:, 2:4]
        
        # Warp original frames to the midpoint
        warped_img0 = warp(img0_tensor, flow0)
        warped_img1 = warp(img1_tensor, flow1)
        
        # Compute absolute difference (B, 1, H, W)
        diff = torch.abs(warped_img0 - warped_img1).mean(dim=1, keepdim=True)
        
        # Exponential decay: diff=0 -> conf=1.0, diff=0.1 -> conf=0.36
        confidence_tensor = torch.exp(-diff / 0.1)
        
        confidence_map = confidence_tensor.squeeze().cpu().numpy()
        mean_confidence = float(np.mean(confidence_map))
        low_confidence_fraction = float(np.mean(confidence_map < 0.5))
        
        return confidence_map, mean_confidence, low_confidence_fraction
