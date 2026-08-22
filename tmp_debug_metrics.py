import requests
import json
f0 = open('data/satellite/validation/sequence_001/frame_000.jpg', 'rb')
gt = open('data/satellite/validation/sequence_001/frame_001.jpg', 'rb')
f2 = open('data/satellite/validation/sequence_001/frame_002.jpg', 'rb')
res2 = requests.post('http://localhost:8000/evaluate', files={'frame0': f0, 'ground_truth': gt, 'frame2': f2})
print(json.dumps(res2.json(), indent=2))
