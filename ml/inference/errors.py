"""Public error types used by CLI and API layers."""


class FrameFlowError(Exception):
    """Base class for expected, safe-to-display errors."""

    code = "frameflow_error"


class MissingWeightsError(FrameFlowError):
    code = "missing_model_weights"


class InvalidTimestepError(FrameFlowError):
    code = "invalid_timestep"


class InferenceFailureError(FrameFlowError):
    code = "inference_failure"


class GpuMemoryError(InferenceFailureError):
    code = "gpu_out_of_memory"

