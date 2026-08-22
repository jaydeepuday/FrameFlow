import numpy as np
import torch
import torch.nn.functional as F

def normalize_and_tensorize(img_np, device):
    """
    Normalizes the NumPy image to [0, 1] range and converts to PyTorch tensor format (1, C, H, W).
    """
    # Create float tensor 
    img_tensor = torch.from_numpy(img_np.transpose(2, 0, 1)).to(device).float()
    
    # RIFE expects [0, 1] interval float tensor.
    if img_tensor.max() > 1.0:
        img_tensor = img_tensor / 255.0
        
    return img_tensor.unsqueeze(0)
    
def pad_for_rife(img_tensor):
    """
    Pads the spatial dimensions of the tensor to be a multiple of 32, as required by RIFE.
    """
    _, _, h, w = img_tensor.shape
    ph = ((h - 1) // 32 + 1) * 32
    pw = ((w - 1) // 32 + 1) * 32
    padding = (0, pw - w, 0, ph - h)
    
    padded_tensor = F.pad(img_tensor, padding)
    return padded_tensor, padding

def unpad_from_rife(img_tensor, padding):
    """
    Removes the padding that was added for RIFE inference.
    padding format used by F.pad is (left, right, top, bottom)
    """
    _, _, h, w = img_tensor.shape
    top, bottom = padding[2], padding[3]
    left, right = padding[0], padding[1]
    
    # Slice the padding off
    out_h = h - bottom
    out_w = w - right
    return img_tensor[:, :, top : out_h, left : out_w]
