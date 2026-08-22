# FrameFlow Environment

## Core Stack
- **Python:** 3.12.10 (Isolated Virtual Environment)
- **PyTorch:** 2.5.1+cu121

## Hardware/Inference
- **CUDA Available:** True
- **GPU Detected:** NVIDIA GeForce RTX 4070 Laptop GPU

## Justification & Safety
Created a dedicated Python 3.12 virtual environment rather than using systemic Python 3.13.7. PyTorch CUDA wheels were explicitly fetched to ensure GPU-accelerated inference capability for the RIFE backbone.
