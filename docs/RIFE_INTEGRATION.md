# RIFE Integration

## Upstream Repository
- **Repository:** `https://github.com/hzwer/ECCV2022-RIFE`
- **Type:** PyTorch Reference Implementation
- **License:** MIT License (based on upstream LICENSE file)

## Integration Strategy
Instead of copy-and-pasting the full RIFE codebase, we place just the required `model/` implementation inside `ml/rife/model/` and expose it via our custom `wrapper.py`. This sandboxes the neural network backbone and abstracts inference so FrameFlow is not cluttered with upstream training or benchmark scripts.

## Local Modifications
- The RIFE codebase was not modified internally.
- Training dependencies were excluded from our global `requirements.txt`. Only core inference prerequisites (PyTorch, torchvision) were populated.
- Our `wrapper.py` handles image pre/post-processing for the model.

## Pretrained Weights
- **Weight Source:** (To be finalized based on upstream README)
- **Model Variant:** Default RIFE (v4.6 or similar)
- Weights are isolated in `models/rife/` rather than the `train_log` convention upstream.
