import cv2
import numpy as np

def linear_interpolate(frame0_path, frame1_path, timestep=0.5):
    """
    Classical linear interpolation baseline.
    output = (1-t) * frame0 + t * frame1
    """
    img0 = cv2.imread(frame0_path, cv2.IMREAD_UNCHANGED)
    img1 = cv2.imread(frame1_path, cv2.IMREAD_UNCHANGED)
    
    if img0 is None or img1 is None:
        raise ValueError("Could not read input frames.")
        
    img0 = img0.astype(float)
    img1 = img1.astype(float)
    
    out = (1.0 - timestep) * img0 + timestep * img1
    
    return np.clip(out, 0, 255).astype(np.uint8)
