from .image_loader import load_satellite_image
from .normalization import normalize_and_tensorize, pad_for_rife, unpad_from_rife

def preprocess_satellite_image(path, device):
    """
    High-level entrypoint for preprocessing a satellite image for RIFE.
    1. Loads the image (PNG/JPEG/TIFF).
    2. Converts to standard RGB representation.
    3. Transforms into a normalized (1, C, H, W) float PyTorch tensor.
    4. Pads the image to have dimensions that are a multiple of 32.
    
    Returns:
    - padded_tensor: The tensor ready for model inference.
    - padding_info: The tuple containing padding offsets (to remove later).
    - original_shape: The original (H, W, C) shape of the input image.
    """
    img_np = load_satellite_image(path)
    img_tensor = normalize_and_tensorize(img_np, device)
    padded_tensor, padding = pad_for_rife(img_tensor)
    
    return padded_tensor, padding, img_np.shape
