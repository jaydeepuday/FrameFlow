# ML pipeline

1. Validate the extension and decode the bytes with Pillow.
2. Convert every input to RGB and reject corrupt, unsupported, oversized, or
   invalid images.
3. Fit differing dimensions into a common canvas, then pad to a multiple of 32
   for the upstream model. Original and processed images are saved separately.
4. Convert to float BCHW tensors in `[0, 1]`.
5. Select `cuda` only when `torch.cuda.is_available()` is true; otherwise use
   CPU. FP16 is optional and only entered on CUDA.
6. Run the real pretrained RIFE HDv3 model once at `t=0.5`.
7. Save the generated midpoint with AI-generated PNG metadata and derive a
   consistency proxy by comparing it with the linear endpoint reconstruction.

The preprocessing module is an adapter boundary for future GeoTIFF, HDF,
multi-band, radiometric, and geospatial-metadata support; those adapters are
not implemented in v1.

