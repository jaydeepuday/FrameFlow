# RIFE weights

FrameFlow integrates the official PyTorch implementation at
`ml/models/rife/upstream/` and expects the externally distributed checkpoint at:

```text
models/rife/train_log/flownet.pkl
```

The upstream archive uses a `train_log/` directory. The archive downloaded from
the official README was extracted here, so the conventions are reconciled by
keeping the upstream `train_log/*.pkl` files under this project's
`models/rife/train_log/` directory. Weights are not pip-installable and are not
redistributed by FrameFlow documentation.

The source repository is `https://github.com/megvii-research/ECCV2022-RIFE` and
is MIT-licensed at the inspected commit. Confirm upstream terms again before
redistributing weights or making a commercial claim.

