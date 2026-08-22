import argparse
import sys
import os
import time
import cv2

current_dir = os.path.dirname(os.path.abspath(__file__))
ml_dir = os.path.abspath(os.path.join(current_dir, '..'))
if ml_dir not in sys.path:
    sys.path.append(ml_dir)

from rife.wrapper import RIFEWrapper

_MODEL_INSTANCE = None

def get_model(device_override="auto"):
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = RIFEWrapper(device_override=device_override)
    return _MODEL_INSTANCE

def interpolate(frame0_path, frame1_path, timestep=0.5, device="auto"):
    model = get_model(device_override=device)
    
    start_time = time.time()
    out_img_np = model.interpolate(frame0_path, frame1_path, timestep)
    inference_time_ms = (time.time() - start_time) * 1000
    
    output_dir = os.path.join(ml_dir, 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'frame_t05_generated.png')
    cv2.imwrite(output_path, out_img_np)
    
    device_name = model.device.type
    
    return {
        "output_path": output_path,
        "device": device_name,
        "inference_time_ms": inference_time_ms,
        "timestep": timestep
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FrameFlow RIFE Interpolation CLI")
    parser.add_argument("--frame0", required=True, help="Path to frame 0")
    parser.add_argument("--frame1", required=True, help="Path to frame 1")
    parser.add_argument("--timestep", type=float, default=0.5)
    parser.add_argument("--device", type=str, choices=["auto", "cuda", "cpu"], default="auto")
    
    args = parser.parse_args()
    
    result = interpolate(args.frame0, args.frame1, args.timestep, args.device)
    print(f"Interpolation complete:")
    print(f"  Device: {result['device']}")
    print(f"  Inference Time: {result['inference_time_ms']:.2f} ms")
    print(f"  Timestep: {result['timestep']}")
    print(f"  Output saved to: {result['output_path']}")
