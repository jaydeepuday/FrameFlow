import os, cv2, time
res = ['DATASET LISTING:']
for d in ['data/satellite', 'ml/outputs/satellite_evaluation']:
    if not os.path.exists(d): continue
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            size = os.path.getsize(p)/1024
            mod = time.ctime(os.path.getmtime(p))
            img = cv2.imread(p)
            if img is not None:
                res.append(f"{f} | {p} | {p.split('.')[-1]} | {img.shape[1]}x{img.shape[0]} | Channels: {img.shape[2]} | Size: {size:.2f}KB | Time: {mod}")
            else:
                res.append(f"{f} | {p} | {p.split('.')[-1]} | Not Image | Size: {size:.2f}KB | Time: {mod}")

with open('output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(res))
