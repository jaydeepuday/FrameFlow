from ml.data.dataset import FrameRecord, split_sequences


def test_sequence_ids_do_not_leak_across_splits():
    records = [FrameRecord(f"seq-{index}", f"seq-{index}/{frame}.png") for index in range(6) for frame in range(3)]
    splits = split_sequences(records, seed=3)
    ids = {name: {record.sequence_id for record in rows} for name, rows in splits.items()}
    assert ids["train"].isdisjoint(ids["val"])
    assert ids["train"].isdisjoint(ids["test"])
    assert ids["val"].isdisjoint(ids["test"])

