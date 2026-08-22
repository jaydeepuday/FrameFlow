import { useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function Timeline() {
  return (
    <div className="timeline" aria-label="Timeline showing real and AI-generated frames">
      <div className="timeline-line" />
      <div className="timeline-point real"><span>●</span><small>T0 · real input</small></div>
      <div className="timeline-point generated"><span>○</span><small>T0.5 · AI generated</small></div>
      <div className="timeline-point real"><span>●</span><small>T1 · real input</small></div>
    </div>
  )
}

function UploadCard({ label, file, onChange }) {
  return (
    <label className="upload-card">
      <span className="eyebrow">{label}</span>
      <strong>{file ? file.name : 'Choose a PNG or JPEG'}</strong>
      <span className="upload-hint">Satellite imagery or other image pairs · v1 is observational</span>
      <input type="file" accept="image/png,image/jpeg" onChange={(event) => onChange(event.target.files?.[0] || null)} />
    </label>
  )
}

function App() {
  const [frame0, setFrame0] = useState(null)
  const [frame1, setFrame1] = useState(null)
  const [timestep, setTimestep] = useState(0.5)
  const [includeFlow, setIncludeFlow] = useState(false)
  const [showConfidence, setShowConfidence] = useState(false)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const canGenerate = useMemo(() => Boolean(frame0 && frame1 && !busy), [frame0, frame1, busy])

  async function generate() {
    if (!canGenerate) return
    setBusy(true)
    setError('')
    const body = new FormData()
    body.append('frame0', frame0)
    body.append('frame1', frame1)
    body.append('timestep', String(timestep))
    body.append('generate_flow', String(includeFlow))
    try {
      const response = await fetch(`${API_BASE}/api/interpolate`, { method: 'POST', body })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail?.message || 'Interpolation failed.')
      setResult(payload)
    } catch (err) {
      setError(err.message || 'Could not reach the FrameFlow backend.')
    } finally {
      setBusy(false)
    }
  }

  const imageUrl = (path) => path ? `${API_BASE}${path}` : ''

  return (
    <main className="shell">
      <header className="topbar">
        <div><span className="brand-mark">FF</span><span className="brand-name">FrameFlow</span></div>
        <span className="status-chip">AI-assisted · observational demo</span>
      </header>

      <section className="hero">
        <div>
          <p className="eyebrow">Temporal detail, made visible</p>
          <h1>Read the moment between<br /><em>two satellite frames.</em></h1>
          <p className="hero-copy">FrameFlow uses pretrained RIFE to generate one plausible midpoint for exploratory disaster monitoring workflows. Generated images are visual aids, never real observations or predictions.</p>
        </div>
        <div className="hero-orbit" aria-hidden="true"><span /><span /><span /></div>
      </section>

      <section className="workspace-grid">
        <div className="panel input-panel">
          <div className="panel-heading"><div><p className="eyebrow">01 · Input pair</p><h2>Set the observed interval</h2></div><span className="step-pill">T0 + T1</span></div>
          <div className="upload-grid">
            <UploadCard label="Frame T0 · earlier" file={frame0} onChange={setFrame0} />
            <UploadCard label="Frame T1 · later" file={frame1} onChange={setFrame1} />
          </div>
          <div className="control-row">
            <div className="range-wrap"><label htmlFor="timestep">Target timestep <strong>T{timestep}</strong></label><input id="timestep" type="range" min="0" max="1" step="0.5" value={timestep} onChange={(event) => setTimestep(Number(event.target.value))} /><div className="range-labels"><span>T0</span><span>T0.5 midpoint</span><span>T1</span></div></div>
            <label className="toggle"><input type="checkbox" checked={includeFlow} onChange={(event) => setIncludeFlow(event.target.checked)} /><span>Optical flow visualization</span></label>
          </div>
          <button className="primary-button" disabled={!canGenerate} onClick={generate}>{busy ? 'Running RIFE inference…' : 'Generate midpoint  →'}</button>
          {error && <p className="error-message" role="alert">{error}</p>}
        </div>

        <aside className="panel timeline-panel">
          <p className="eyebrow">Time axis</p><h2>Observed + inferred</h2><Timeline />
          <div className="legend"><span><i className="dot-real">●</i> Real input</span><span><i className="dot-generated">○</i> AI generated</span></div>
          <p className="small-note">The midpoint is reconstructed for visual exploration and must be reviewed alongside the real frames.</p>
        </aside>
      </section>

      {result && <section className="panel results-panel">
        <div className="panel-heading"><div><p className="eyebrow">02 · Result</p><h2>One generated frame, clearly marked</h2></div><span className="ai-badge">AI GENERATED</span></div>
        <div className="results-layout">
          <div className="comparison-wrap"><img src={imageUrl(showConfidence ? result.output_urls.confidence_map : result.output_urls.comparison)} alt={showConfidence ? 'Model confidence proxy map' : 'T0, AI generated T0.5, and T1 comparison'} /><div className="image-caption">{showConfidence ? 'Confidence proxy · Low / Medium / High' : 'T0 real input  |  T0.5 AI GENERATED  |  T1 real input'}</div></div>
          <div className="result-aside">
            <div className="result-callout"><span className="eyebrow">Generated midpoint</span><strong>T0.5</strong><p>AI GENERATED · not a real satellite observation</p></div>
            <button className="secondary-button" onClick={() => setShowConfidence(!showConfidence)}>{showConfidence ? 'Show comparison' : 'Show confidence proxy'}</button>
            {showConfidence && <p className="confidence-copy">Model confidence proxy based on interpolation/reconstruction consistency. This is not a calibrated probability.</p>}
            <div className="metrics-card"><span className="eyebrow">Run telemetry</span><div><span>Device</span><strong>{result.device}</strong></div><div><span>Inference</span><strong>{result.inference_time_ms} ms</strong></div><div><span>Model load</span><strong>{result.model_load_time_ms} ms</strong></div><div><span>Processed size</span><strong>{result.processed_resolution.width} × {result.processed_resolution.height}</strong></div></div>
            {result.metrics && <div className="metrics-card"><span className="eyebrow">Ground-truth metrics</span><div><span>MAE</span><strong>{result.metrics.rife.mae}</strong></div><div><span>PSNR</span><strong>{result.metrics.rife.psnr}</strong></div><div><span>SSIM</span><strong>{result.metrics.rife.ssim}</strong></div></div>}
          </div>
        </div>
      </section>}

      <footer><span>FrameFlow v1 · pretrained RIFE backbone</span><span>Generated imagery is demonstrative only · no disaster prediction</span></footer>
    </main>
  )
}

export default App
