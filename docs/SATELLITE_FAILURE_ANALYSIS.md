# Satellite Imagery Failure Analysis on Pretrained RIFE

While the baseline interpolation significantly surpasses linear fading (SSIM 0.812 vs 0.682 on GOES convection loops), `FrameFlow` recognizes mechanical failure domains when applying standard multi-frame video models to atmospheric physics.

## 1. Cloud Morphogenesis & Non-Rigid Formation
Pretrained RIFE (originally trained on Vimeo90K) models optical flow based on classical camera motion and rigid body translations. Severe weather (such as Hurricane convection boundaries) inherently involves *generation* and *dissipation* of physical mass entirely outside classical rigid-warping equations, causing the model to attempt pulling features dynamically from unassociated neighboring pixel clouds.

## 2. Radiometric Drifting & Illumination
Sunrise, sunset, and solar reflection bands (glint) alter the pixel intensity of identical geolocation coordinates over time. RIFE will attempt to preserve luminosity across its blending steps rather than accounting for strict solar terminator movement, potentially dragging daylight across pixels artificially.

## 3. Disappearing Boundaries & Shear Velocities
Extreme horizontal shear (e.g., upper atmosphere jets moving contra directionally to localized lower cumulus banks) heavily corrupts the bi-directional optical flow fields within `warplayer`, occasionally tearing visual boundaries as vector mappings intersect.

## 4. Registration Errors
While geostationary ABI sensors preserve sub-pixel spatial consistency natively, minor mechanical drift (wobble) without projection realignment introduces massive global optical flow penalties. Preprocessing ingestion layers must guarantee geographic alignment perfectly prior to tensorization.
