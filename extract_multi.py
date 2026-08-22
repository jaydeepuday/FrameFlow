import os
from PIL import Image
import numpy as np
import cv2

gif_path = 'data/satellite/raw/goes_ian.gif'
img = Image.open(gif_path)
frames = []
try:
    while True:
        img.seek(len(frames))
        frames.append(np.array(img.convert('RGB')))
except EOFError:
    pass

print(f"Total frames available: {len(frames)}")
num_seqs_max = 10
seq_count = 0

# Try non-overlapping first
if len(frames) >= 30:
    print("Using non-overlapping triplets.")
    for i in range(10):
        seq_idx = i + 1
        seq_dir = f'data/satellite/validation/sequence_{seq_idx:03d}'
        os.makedirs(seq_dir, exist_ok=True)
        cv2.imwrite(f'{seq_dir}/frame_000.jpg', cv2.cvtColor(frames[i*3], cv2.COLOR_RGB2BGR))
        cv2.imwrite(f'{seq_dir}/frame_001.jpg', cv2.cvtColor(frames[i*3+1], cv2.COLOR_RGB2BGR))
        cv2.imwrite(f'{seq_dir}/frame_002.jpg', cv2.cvtColor(frames[i*3+2], cv2.COLOR_RGB2BGR))
        seq_count += 1
else:
    print("Using overlapping triplets (not enough frames for 30).")
    for i in range(min(len(frames)-2, 10)):
        seq_idx = i + 1
        seq_dir = f'data/satellite/validation/sequence_{seq_idx:03d}'
        os.makedirs(seq_dir, exist_ok=True)
        cv2.imwrite(f'{seq_dir}/frame_000.jpg', cv2.cvtColor(frames[i], cv2.COLOR_RGB2BGR))
        cv2.imwrite(f'{seq_dir}/frame_001.jpg', cv2.cvtColor(frames[i+1], cv2.COLOR_RGB2BGR))
        cv2.imwrite(f'{seq_dir}/frame_002.jpg', cv2.cvtColor(frames[i+2], cv2.COLOR_RGB2BGR))
        seq_count += 1

print(f"Created {seq_count} sequences.")
