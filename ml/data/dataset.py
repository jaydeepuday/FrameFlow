"""Sequence-aware dataset split scaffolding for future RIFE fine-tuning."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Sequence


@dataclass(frozen=True)
class FrameRecord:
    sequence_id: str
    frame_path: str
    date_or_event: str | None = None


def split_sequences(
    records: Sequence[FrameRecord],
    *,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 0,
) -> dict[str, list[FrameRecord]]:
    """Split whole sequences, never individual frames, across train/val/test."""

    if not records:
        return {"train": [], "val": [], "test": []}
    if train_ratio <= 0 or val_ratio < 0 or train_ratio + val_ratio >= 1:
        raise ValueError("train_ratio and val_ratio must leave a positive test split.")
    groups: dict[str, list[FrameRecord]] = {}
    for record in records:
        groups.setdefault(record.sequence_id, []).append(record)
    sequence_ids = list(groups)
    random.Random(seed).shuffle(sequence_ids)
    train_end = max(1, round(len(sequence_ids) * train_ratio))
    val_end = train_end + round(len(sequence_ids) * val_ratio)
    val_end = min(len(sequence_ids) - 1, max(train_end, val_end))
    assignments = {
        "train": sequence_ids[:train_end],
        "val": sequence_ids[train_end:val_end],
        "test": sequence_ids[val_end:],
    }
    return {name: [record for sequence_id in ids for record in groups[sequence_id]] for name, ids in assignments.items()}

