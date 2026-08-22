# Satellite Dataset Documentation

## Dataset Origin
- **Satellite/Platform:** GOES-East (GOES-16)
- **Data Provider:** NOAA (Via Wikimedia Commons Open Archive)
- **Product:** GEOCOLOR (Cloud and Moisture Imagery proxy combining ABI bands)
- **Geographic Region:** US Southeast / Hurricane Ian (2022)
- **Acquisition Date:** 27 September 2022

## Characteristics
- **Temporal Resolution:** Extract continuous progression from meteorological animation loop.
- **File Format:** Multi-frame GIF unrolled sequentially into discrete structural PNG/JPG instances.
- **License/Usage Terms:** US Government Public Domain (NOAA Open Access)
- **Preprocessing Performed:** 
  - Index-based spatial segregation from contiguous animated GIF structure.
  - `scikit-image` tensor normalization pipeline (modulo-32 bounding for RIFE input constraints).
  - Frame chronology verified visually preventing negative-time flow.

## Acquisition Method
Due to port/firewall restraints hitting NOAA open S3 and CDN buckets dynamically from the immediate worker loopback, the sequence was extracted directly via Wikipedia's programmatic structural metadata queries against historical severe weather loop recordings.
