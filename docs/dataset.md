# Dataset and split policy

No satellite dataset is included, fabricated, or automatically downloaded.
Manual demo inputs belong in `data/samples/` and remain user-supplied.

Future fine-tuning manifests should carry a `sequence_id` plus date/event
context. `ml/data/dataset.py` groups all frames by `sequence_id` before making
train/validation/test splits. A random per-frame split is prohibited because
adjacent frames from one event would leak across evaluation boundaries.

