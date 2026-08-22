import os
import boto3
from botocore import UNSIGNED
from botocore.config import Config

s3 = boto3.client('s3', region_name='us-east-1', config=Config(signature_version=UNSIGNED))

# Hurricane Ian landfall approach - Year 2022, Day of Year 271, Hour 00
prefix = 'ABI-L2-CMIPC/2022/271/00/'
bucket_name = 'noaa-goes16'

print(f"Listing keys in s3://{bucket_name}/{prefix}...")
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

# -M6 means Mode 6 (10 minute CONUS refresh)
# C13 means Channel 13 (Clean IR longwave ~10.3um)
# G16 means GOES-16
b13_files = [obj['Key'] for obj in response.get('Contents', []) if '-M6C13_G16' in obj['Key']]
b13_files.sort()

if len(b13_files) < 3:
    print("Error: Less than 3 files found in this hour.")
    exit(1)

triplet = b13_files[:3]

os.makedirs('data/satellite/raw/goes16_b13', exist_ok=True)

for key in triplet:
    filename = os.path.basename(key)
    out_path = f'data/satellite/raw/goes16_b13/{filename}'
    print(f"Downloading {filename}...")
    s3.download_file(bucket_name, key, out_path)

print("Download complete.")
