"""Optional classical optical-flow visualization."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


def save_optical_flow_visualization(
    frame0: np.ndarray, frame1: np.ndarray, output_path: str | Path
) -> Path:
    gray0 = cv2.cvtColor((np.clip(frame0, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    gray1 = cv2.cvtColor((np.clip(frame1, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    flow = cv2.calcOpticalFlowFarneback(gray0, gray1, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv = np.zeros((*gray0.shape, 3), dtype=np.uint8)
    hsv[..., 0] = (angle * 180 / np.pi / 2).astype(np.uint8)
    hsv[..., 1] = 255
    hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    visual = Image.fromarray(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB))
    draw = ImageDraw.Draw(visual)
    draw.rectangle((4, 4, 315, 28), fill=(20, 28, 40))
    draw.text((9, 9), "Optical Flow Visualization (Farneback)", fill=(255, 255, 255))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    visual.save(output)
    return output

