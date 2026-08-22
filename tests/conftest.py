from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture
def tmp_path():
    """Workspace-local temp fixture for restricted Windows test environments."""

    root = Path(__file__).resolve().parent / ".runtime-tmp" / uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)

