import sys
import os
import torch
import cv2
import torch.nn.functional as F

# Adjust paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

weights_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'models', 'rife'))
if weights_dir not in sys.path:
    sys.path.append(weights_dir)

import RIFE_HDv3

class RIFEWrapper:
    def __init__(self, model_dir=None, device_override="auto"):
        if model_dir is None:
            model_dir = weights_dir
            
        if device_override == "cpu":
            self.device = torch.device("cpu")
        elif device_override == "cuda":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
        # Monkey-patch upstream device declaration
        RIFE_HDv3.device = self.device
        import IFNet_HDv3
        IFNet_HDv3.device = self.device
        import model.warplayer
        model.warplayer.device = self.device
        
        torch.set_grad_enabled(False)
        if self.device.type == "cuda":
            torch.backends.cudnn.enabled = True
            torch.backends.cudnn.benchmark = True

        self.model = RIFE_HDv3.Model(-1)
        self.model.load_model(model_dir, -1)
        self.model.eval()
        self.model.device()

    def interpolate(self, img0_path, img1_path, timestep=0.5):
        img0 = cv2.imread(img0_path, cv2.IMREAD_UNCHANGED)
        img1 = cv2.imread(img1_path, cv2.IMREAD_UNCHANGED)
        
        img0 = (torch.tensor(img0.transpose(2, 0, 1)).to(self.device).float() / 255.0).unsqueeze(0)
        img1 = (torch.tensor(img1.transpose(2, 0, 1)).to(self.device).float() / 255.0).unsqueeze(0)
        
        n, c, h, w = img0.shape
        ph = ((h - 1) // 32 + 1) * 32
        pw = ((w - 1) // 32 + 1) * 32
        padding = (0, pw - w, 0, ph - h)
        img0 = F.pad(img0, padding)
        img1 = F.pad(img1, padding)
        
        # Single inference for exactly 0.5 (midpoint)
        mid = self.model.inference(img0, img1)
        
        out = (mid[0] * 255).byte().cpu().numpy().transpose(1, 2, 0)[:h, :w]
        return out
