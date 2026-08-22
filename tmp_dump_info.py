import os
import cv2
import time

dirs = ['data/satellite', 'ml/outputs/satellite_evaluation']
res = []
for d in dirs:
    if not os.path.exists(d): continue
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            size = os.path.getsize(p) / 1024.0
            mod = time.ctime(os.path.getmtime(p))
            img = cv2.imread(p)
            if img is not None:
                h, w, c = img.shape
                res.append(f"File: {f} | Path: {p} | Format: {p.split('.')[-1].upper()} | Width: {w} | Height: {h} | Channels: {c} | Size: {size:.2f} KB | Timestamp: {mod}")
            else:
                res.append(f"File: {f} | Path: {p} | Format: {p.split('.')[-1].upper()} | Not an Image | Size: {size:.2f} KB | Timestamp: {mod}")

with open('tmp_metrics2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(res))
