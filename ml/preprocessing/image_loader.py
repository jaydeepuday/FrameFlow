import cv2
import numpy as np
import os
try:
    import tifffile
except ImportError:
    tifffile = None

def load_satellite_image(path):
    """
    Loads an image (PNG, JPG, TIFF) and returns a deterministic NumPy array (H, W, C) in RGB format.
    Validates input and ensures 3-channel layout.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")
        
    ext = os.path.splitext(path)[-1].lower()
    
    if ext in ['.tif', '.tiff'] and tifffile is not None:
        # tifffile loads efficiently and preserves values
        img = tifffile.imread(path)
        # Handle grayscale TIFFs
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif len(img.shape) == 3 and img.shape[2] > 3:
            # Multi-band (e.g. 4+ bands), just take first 3 for this MVP
            img = img[:, :, :3]
    else:
        # Fallback to OpenCV
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Unable to load image or unsupported format: {path}")
            
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            # OpenCV loads as BGR, convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            # Drop alpha if present
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            
    return img
