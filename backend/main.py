"""FastAPI API for FrameFlow's two-frame midpoint inference."""

from __future__ import annotations

from contextlib import asynccontextmanager
import re
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ml.inference.errors import FrameFlowError, GpuMemoryError, MissingWeightsError
from ml.inference.interpolate import OUTPUT_DIR, interpolate
from ml.models.rife.adapter import get_default_adapter
from ml.preprocessing.pipeline import PreprocessingError


MAX_UPLOAD_BYTES = 15 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg"}
SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        get_default_adapter().load()
    except FrameFlowError:
        # Health reports degraded status with a safe message; interpolation returns the
        # actionable missing-weight error. This keeps the API process inspectable.
        pass
    yield


app = FastAPI(title="FrameFlow API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/api/output", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


def _safe_upload_suffix(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if upload.content_type not in ALLOWED_CONTENT_TYPES or suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=415,
            detail={
                "code": "unsupported_format",
                "message": "Uploads must be PNG or JPEG images with a matching filename extension.",
            },
        )
    return suffix


async def _persist_upload(upload: UploadFile, label: str) -> Path:
    suffix = _safe_upload_suffix(upload)
    payload = await upload.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "oversized_image",
                "message": "Uploaded image exceeds the 15 MB size limit.",
            },
        )
    # The random server-generated name prevents path traversal from user filenames.
    safe_label = SAFE_NAME.sub("", label)[:16] or "frame"
    target = OUTPUT_DIR / "uploads" / f"{safe_label}_{uuid4().hex}{suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return target


@app.get("/api/health")
def health() -> dict:
    adapter = get_default_adapter()
    return {
        "status": "ok" if adapter.model_loaded else "degraded",
        "model_loaded": adapter.model_loaded,
        "device": str(adapter.device),
    }


@app.post("/api/interpolate")
async def api_interpolate(
    frame0: UploadFile = File(...),
    frame1: UploadFile = File(...),
    timestep: float = Form(0.5),
    generate_flow: bool = Form(False),
) -> JSONResponse:
    paths: list[Path] = []
    try:
        paths = [
            await _persist_upload(frame0, "frame0"),
            await _persist_upload(frame1, "frame1"),
        ]
        result = interpolate(
            paths[0], paths[1], timestep=timestep, generate_flow=generate_flow
        )
    except HTTPException:
        raise
    except FrameFlowError as exc:
        status = 503 if isinstance(exc, MissingWeightsError) else 400
        return JSONResponse(
            status_code=status,
            content={"detail": {"code": getattr(exc, "code", "frameflow_error"), "message": str(exc)}},
        )
    except PreprocessingError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"code": getattr(exc, "code", "preprocessing_error"), "message": str(exc)}},
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=400,
            content={"detail": {"code": "missing_image", "message": "An uploaded image could not be read."}},
        )
    except RuntimeError as exc:
        message = str(exc)
        if "out of memory" in message.lower():
            error = GpuMemoryError(
                "Inference ran out of GPU memory. Retry with a smaller image or CPU mode."
            )
            return JSONResponse(
                status_code=503,
                content={"detail": {"code": error.code, "message": str(error)}},
            )
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "code": "inference_failure",
                    "message": "RIFE inference failed. Check the image dimensions and model installation.",
                }
            },
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": {"code": "server_error", "message": "FrameFlow could not complete this request."}},
        )
    finally:
        for path in paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    result["output_urls"] = {
        "frame_t0": "/api/output/frame_t0.png",
        "generated": "/api/output/frame_t05_generated.png",
        "frame_t1": "/api/output/frame_t1.png",
        "comparison": "/api/output/comparison.png",
        "confidence_map": "/api/output/confidence_map.png",
        "flow_visualization": (
            "/api/output/flow/optical_flow_visualization.png"
            if result["flow_visualization_path"]
            else None
        ),
    }
    # Do not expose internal filesystem paths to clients.
    for key in ("output_path", "comparison_path", "confidence_map_path", "flow_visualization_path"):
        result.pop(key, None)
    return JSONResponse(status_code=200, content=result)
