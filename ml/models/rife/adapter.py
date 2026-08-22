"""Thin adapter for the official PyTorch ECCV2022-RIFE source."""

from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

import torch

from ml.inference.errors import MissingWeightsError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPSTREAM_ROOT = PROJECT_ROOT / "ml" / "models" / "rife" / "upstream"
DEFAULT_WEIGHTS_ROOT = PROJECT_ROOT / "models" / "rife"


def select_device() -> torch.device:
    """Select CUDA only when the installed PyTorch build reports it available."""

    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


class RifeModelAdapter:
    """Load the official HDv3 checkpoint once and expose midpoint inference."""

    def __init__(self, weights_root: str | Path = DEFAULT_WEIGHTS_ROOT, use_fp16: bool = False):
        self.weights_root = Path(weights_root)
        self.train_log = self.weights_root / "train_log"
        self.device = select_device()
        self.use_fp16 = bool(use_fp16 and self.device.type == "cuda")
        self.model = None
        self.model_load_time_ms: float | None = None
        self.load_count = 0

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    def _check_weights(self) -> None:
        if not self.train_log.is_dir() or not (self.train_log / "flownet.pkl").is_file():
            raise MissingWeightsError(
                "Pretrained RIFE weights are missing. Place the upstream "
                "train_log/flownet.pkl under models/rife/train_log/."
            )
        if not UPSTREAM_ROOT.is_dir():
            raise MissingWeightsError(
                "The official PyTorch RIFE source is missing under ml/models/rife/upstream/."
            )

    def load(self) -> None:
        if self.model is not None:
            return
        self._check_weights()
        started = time.perf_counter()
        # RIFE's upstream modules use absolute package imports (model.* and train_log.*).
        for path in (str(UPSTREAM_ROOT), str(self.weights_root)):
            if path not in sys.path:
                sys.path.insert(0, path)
        importlib.invalidate_caches()
        try:
            module = importlib.import_module("train_log.RIFE_HDv3")
            model = module.Model()
            model.load_model(str(self.train_log), -1)
            model.eval()
        except Exception as exc:
            raise MissingWeightsError(
                "RIFE weights were found but could not be loaded with the vendored "
                "official PyTorch HDv3 model. Check the checkpoint and PyTorch install."
            ) from exc
        self.model = model
        self.model_load_time_ms = (time.perf_counter() - started) * 1000.0
        self.load_count += 1

    def infer(self, frame0, frame1):
        self.load()
        try:
            with torch.inference_mode():
                if self.use_fp16:
                    with torch.autocast(device_type="cuda", dtype=torch.float16):
                        return self.model.inference(frame0, frame1)
                return self.model.inference(frame0, frame1)
        except RuntimeError as exc:
            if "out of memory" in str(exc).lower():
                raise RuntimeError("CUDA out of memory during RIFE inference.") from exc
            raise


_DEFAULT_ADAPTER: RifeModelAdapter | None = None


def get_default_adapter(
    *, use_fp16: bool = False, weights_root: str | Path = DEFAULT_WEIGHTS_ROOT
) -> RifeModelAdapter:
    global _DEFAULT_ADAPTER
    requested_root = Path(weights_root)
    if _DEFAULT_ADAPTER is None or _DEFAULT_ADAPTER.weights_root.resolve() != requested_root.resolve():
        _DEFAULT_ADAPTER = RifeModelAdapter(requested_root, use_fp16=use_fp16)
    return _DEFAULT_ADAPTER
