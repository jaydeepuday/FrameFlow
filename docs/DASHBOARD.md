# FrameFlow Dashboard

The FrameFlow frontend provides an interactive GUI built locally with React and Vite. It is engineered with a structured scientific visual identity tailored explicitly towards tracking the optical flow metrics emitted by PyTorch RIFE.

## Usage
1. First start the API: `python -m uvicorn backend.main:app --port 8000`
2. From the `frontend/` directory, launch React: `npm run dev`
3. Navigate to `http://localhost:5173`.

## Architecture
- **Strict CSS:** No framework coupling. The aesthetics are maintained via an explicitly mapped dark theme suited identically for professional satellite tracking logic.
- **Direct Previews:** Input `Frame T` and `Frame T+1` are previewed live directly dynamically via `URL.createObjectURL(file)`.
- **Metadata Engine:** Timestep selection executes requests to the backend logic. Inferences report live device tracking, execution ms arrays, and global bounding consistencies alongside the actual `confidence_map` projection output.
