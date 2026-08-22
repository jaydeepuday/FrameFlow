"""FrameFlow's two-frame to midpoint RIFE inference API and CLI."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from PIL.PngImagePlugin import PngInfo

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.inference.confidence import CONFIDENCE_LABEL, confidence_proxy, save_confidence_map
from ml.inference.errors import FrameFlowError, GpuMemoryError, InferenceFailureError, InvalidTimestepError
from ml.inference.flow import save_optical_flow_visualization
from ml.models.rife.adapter import get_default_adapter
from ml.preprocessing.pipeline import crop_array_to_size, prepare_pair


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "ml" / "outputs"
ALLOWED_TIMESTEPS = (0.0, 0.5, 1.0)


def _validate_timestep(timestep: float) -> float:
    try:
        value = float(timestep)
    except (TypeError, ValueError) as exc:
        raise InvalidTimestepError("Timestep must be one of 0, 0.5, or 1.") from exc
    if not any(math.isclose(value, allowed, abs_tol=1e-9) for allowed in ALLOWED_TIMESTEPS):
        raise InvalidTimestepError(
            f"Unsupported timestep {value}. v1 supports only 0, 0.5, and 1."
        )
    return value


def _array_from_tensor(tensor: torch.Tensor) -> np.ndarray:
    return (
        tensor.detach().float().cpu().clamp(0, 1)[0].permute(1, 2, 0).numpy().astype(np.float32)
    )


def _save_rgb(array: np.ndarray, path: Path, *, description: str | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray((np.clip(array, 0, 1) * 255).round().astype(np.uint8), mode="RGB")
    if description:
        metadata = PngInfo()
        metadata.add_text("Description", description)
        image.save(path, pnginfo=metadata)
    else:
        image.save(path)
    return path


def _save_comparison(frame0: np.ndarray, generated: np.ndarray, frame1: np.ndarray, path: Path) -> Path:
    from PIL import ImageDraw

    panels = [
        Image.fromarray((np.clip(frame0, 0, 1) * 255).round().astype(np.uint8), mode="RGB"),
        Image.fromarray((np.clip(generated, 0, 1) * 255).round().astype(np.uint8), mode="RGB"),
        Image.fromarray((np.clip(frame1, 0, 1) * 255).round().astype(np.uint8), mode="RGB"),
    ]
    width, height = panels[0].size
    comparison = Image.new("RGB", (width * 3, height), (20, 28, 40))
    labels = ("T0 • REAL INPUT", "T0.5 • AI GENERATED", "T1 • REAL INPUT")
    for index, panel in enumerate(panels):
        draw = ImageDraw.Draw(panel)
        draw.rectangle((4, 4, min(width - 4, 190), 27), fill=(20, 28, 40))
        draw.text((9, 9), labels[index], fill=(255, 255, 255))
        comparison.paste(panel, (index * width, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = PngInfo()
    metadata.add_text("Description", "T0 | AI GENERATED T0.5 | T1 comparison")
    comparison.save(path, pnginfo=metadata)
    return path


def interpolate(
    frame0_path: str | Path,
    frame1_path: str | Path,
    timestep: float = 0.5,
    *,
    generate_flow: bool = False,
    use_fp16: bool = False,
    strict_dimensions: bool = False,
    output_dir: str | Path = OUTPUT_DIR,
    weights_root: str | Path | None = None,
) -> dict:
    """Interpolate exactly one midpoint and return measured run metadata."""

    target_timestep = _validate_timestep(timestep)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    prepared0, prepared1 = prepare_pair(
        frame0_path,
        frame1_path,
        auto_resize=not strict_dimensions,
        strict_dimensions=strict_dimensions,
    )
    adapter = get_default_adapter(
        use_fp16=use_fp16,
        **({"weights_root": weights_root} if weights_root is not None else {}),
    )
    # Loading is lazy but happens once per process. Endpoint requests still report it.
    adapter.load()
    started = time.perf_counter()
    try:
        if target_timestep == 0.0:
            generated = _array_from_tensor(prepared0.tensor.to(adapter.device))
        elif target_timestep == 1.0:
            generated = _array_from_tensor(prepared1.tensor.to(adapter.device))
        else:
            generated = _array_from_tensor(
                adapter.infer(prepared0.tensor.to(adapter.device), prepared1.tensor.to(adapter.device))
            )
    except RuntimeError as exc:
        message = str(exc)
        if "out of memory" in message.lower():
            raise GpuMemoryError(
                "Inference ran out of GPU memory. Retry with a smaller image or CPU mode."
            ) from exc
        raise InferenceFailureError(
            "RIFE inference failed. Check the image dimensions and model installation."
        ) from exc
    except Exception as exc:
        raise InferenceFailureError(
            "RIFE inference failed. Check the image dimensions and model installation."
        ) from exc
    inference_time_ms = (time.perf_counter() - started) * 1000.0

    processed_size = prepared0.size
    generated = crop_array_to_size(generated, processed_size)
    frame0 = np.asarray(prepared0.processed_image, dtype=np.float32) / 255.0
    frame1 = np.asarray(prepared1.processed_image, dtype=np.float32) / 255.0
    # Save the processed inputs and the original inputs separately for traceability.
    _save_rgb(
        np.asarray(prepared0.rgb_image, dtype=np.float32) / 255.0,
        output_root / "frame_t0_original.png",
        description="Original input frame T0; real user-supplied image",
    )
    _save_rgb(
        np.asarray(prepared1.rgb_image, dtype=np.float32) / 255.0,
        output_root / "frame_t1_original.png",
        description="Original input frame T1; real user-supplied image",
    )
    _save_rgb(frame0, output_root / "frame_t0.png", description="Processed input frame T0; real input")
    _save_rgb(frame1, output_root / "frame_t1.png", description="Processed input frame T1; real input")
    generated_path = _save_rgb(
        generated,
        output_root / "frame_t05_generated.png",
        description="AI GENERATED midpoint T0.5; not a real satellite observation",
    )
    comparison_path = _save_comparison(frame0, generated, frame1, output_root / "comparison.png")
    confidence_path = save_confidence_map(
        confidence_proxy(frame0, generated, frame1), output_root / "confidence_map.png"
    )
    flow_path = None
    if generate_flow:
        flow_path = save_optical_flow_visualization(
            frame0, frame1, output_root / "flow" / "optical_flow_visualization.png"
        )

    result = {
        "output_path": str(generated_path),
        "comparison_path": str(comparison_path),
        "confidence_map_path": str(confidence_path),
        "flow_visualization_path": str(flow_path) if flow_path else None,
        "device": str(adapter.device),
        "timestep": target_timestep,
        "inference_time_ms": round(inference_time_ms, 3),
        "model_load_time_ms": round(adapter.model_load_time_ms or 0.0, 3),
        "model_load_count": adapter.load_count,
        "input_resolution": {
            "frame0": {"width": prepared0.original_size[0], "height": prepared0.original_size[1]},
            "frame1": {"width": prepared1.original_size[0], "height": prepared1.original_size[1]},
        },
        "processed_resolution": {"width": processed_size[0], "height": processed_size[1]},
        "confidence_label": CONFIDENCE_LABEL,
        "generated_label": "AI GENERATED — not a real observation",
    }
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FrameFlow RIFE midpoint interpolation")
    parser.add_argument("--frame0", required=True, help="PNG/JPEG frame T0")
    parser.add_argument("--frame1", required=True, help="PNG/JPEG frame T1")
    parser.add_argument("--timestep", type=float, default=0.5, choices=ALLOWED_TIMESTEPS)
    parser.add_argument("--flow", action="store_true", help="also save Farneback flow visualization")
    parser.add_argument("--fp16", action="store_true", help="opt into FP16 only when CUDA is available")
    parser.add_argument("--strict-dimensions", action="store_true")
    parser.add_argument(
        "--weights-root",
        default=str(PROJECT_ROOT / "models" / "rife"),
        help="directory containing train_log/flownet.pkl",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result = interpolate(
            args.frame0,
            args.frame1,
            args.timestep,
            generate_flow=args.flow,
            use_fp16=args.fp16,
            strict_dimensions=args.strict_dimensions,
            weights_root=args.weights_root,
        )
    except FrameFlowError as exc:
        print(f"ERROR [{getattr(exc, 'code', 'frameflow_error')}]: {exc}", file=sys.stderr)
        return 2
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    print(f"device: {result['device']}")
    print(f"inference_time_ms: {result['inference_time_ms']}")
    print(f"timestep: {result['timestep']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
