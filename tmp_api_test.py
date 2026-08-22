import requests
import time
print("Giving backend 3s to boot...")
time.sleep(3)

# 1. Test Interpolate
f0 = open('data/satellite/validation/sequence_001/frame_000.jpg', 'rb')
f1 = open('data/satellite/validation/sequence_001/frame_001.jpg', 'rb')
res = requests.post('http://localhost:8000/interpolate', data={'timestep': 0.5}, files={'frame0': f0, 'frame1': f1})
print('Interpolate Status:', res.status_code)
if res.status_code == 200:
    j = res.json()
    print('Interpolation contains RIFE time?', 'rife_inference_time_ms' in j)
    print('Interpolation contains Total time?', 'total_processing_time_ms' in j)
else:
    print('Error:', res.text)
f0.close()
f1.close()

# 2. Test Evaluate
f0 = open('data/satellite/validation/sequence_001/frame_000.jpg', 'rb')
gt = open('data/satellite/validation/sequence_001/frame_001.jpg', 'rb')
f2 = open('data/satellite/validation/sequence_001/frame_002.jpg', 'rb')

res2 = requests.post('http://localhost:8000/evaluate', files={'frame0': f0, 'ground_truth': gt, 'frame2': f2})
print('Evaluate Status:', res2.status_code)
if res2.status_code == 200:
    j2 = res2.json()
    print('Evaluate contains linear and rife metrics?', 'rife_metrics' in j2 and 'linear_metrics' in j2)
    print('Evaluate outputs 3 image urls?', 'rife_image_url' in j2 and 'linear_image_url' in j2 and 'confidence_map_url' in j2)
else:
    print('Error:', res2.text)
