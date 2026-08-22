import urllib.request
import json
import os
from PIL import Image
import numpy as np
import cv2

# Get URL from Wikipedia API
api_url = 'https://en.wikipedia.org/w/api.php?action=query&titles=File:Hurricane_Ian_-_GOES-East_GEOCOLOR_satellite_image_on_27_September_2022,_just_after_sunset,_up_to_2331_UTC.gif&prop=imageinfo&iiprop=url&format=json'
req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
pages = data['query']['pages']
page = next(iter(pages.values()))
gif_url = page['imageinfo'][0]['url']

print(f"Downloading {gif_url}...")

os.makedirs('data/satellite/raw', exist_ok=True)
gif_path = 'data/satellite/raw/goes_ian.gif'

req = urllib.request.Request(gif_url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req).read()
with open(gif_path, 'wb') as f:
    f.write(data)

print("Extracting triplet...")
os.makedirs('data/satellite/validation/sequence_001', exist_ok=True)

img = Image.open(gif_path)
frames = []
try:
    for i in range(10):
        img.seek(i)
        frames.append(np.array(img.convert('RGB')))
except EOFError:
    pass

if len(frames) >= 3:
    cv2.imwrite('data/satellite/validation/sequence_001/frame_000.jpg', cv2.cvtColor(frames[0], cv2.COLOR_RGB2BGR))
    cv2.imwrite('data/satellite/validation/sequence_001/frame_001.jpg', cv2.cvtColor(frames[1], cv2.COLOR_RGB2BGR))
    cv2.imwrite('data/satellite/validation/sequence_001/frame_002.jpg', cv2.cvtColor(frames[2], cv2.COLOR_RGB2BGR))
    print("Successfully extracted frames.")
else:
    print(f"Not enough frames: {len(frames)}")
