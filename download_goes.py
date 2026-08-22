import urllib.request
import re
import os

url = 'https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/'
print(f"Fetching index from {url}...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Look for exactly sized images e.g. 1000x1000 or 500x500 to keep it lightweight.
# Format: 20261171731_GOES16-ABI-CONUS-GEOCOLOR-1000x1000.jpg
# We regex find all 1000x1000.jpg
pattern = r'href="([^"]+-1000x1000\.jpg)"'
matches = re.findall(pattern, html)

if len(matches) < 3:
    print(f"Found {len(matches)} images, not enough for triplet.")
    exit(1)

# We want the 3 latest or oldest from the array.
# Since they are time stamped, let's take 3 consecutive ones from the middle to ensure good data.
targets = sorted(list(set(matches)))[-5:-2] # take 3 recent but not the absolute latest which might be writing.

os.makedirs('data/satellite/validation/sequence_001', exist_ok=True)

print("Downloading:", targets)
for i, t in enumerate(targets):
    img_url = url + t
    out_path = f'data/satellite/validation/sequence_001/frame_{i:03d}.jpg'
    print(f"Downloading {img_url} -> {out_path}")
    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req).read()
    with open(out_path, 'wb') as f:
        f.write(data)

print("Download complete.")
