import React, { useState } from 'react';
import axios from 'axios';
import { FileUp, Play, Image as ImageIcon, BarChart3, Clock, AlertCircle } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:8000';

function InterpolationTab() {
    const [frame0, setFrame0] = useState(null);
    const [frame1, setFrame1] = useState(null);
    const [timestep, setTimestep] = useState(0.5);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e, setter) => {
        if (e.target.files && e.target.files[0]) setter(e.target.files[0]);
    };

    const handleGenerate = async () => {
        if (!frame0 || !frame1) return;
        setLoading(true); setError(null);
        const formData = new FormData();
        formData.append('frame0', frame0);
        formData.append('frame1', frame1);
        formData.append('timestep', timestep);
        try {
            const res = await axios.post(`${API_URL}/interpolate`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="timeline">
                <span>REAL T0</span>
                <span style={{ margin: '0 2rem' }}>───── {timestep === 0.5 ? 'AI T0.5' : `AI T${timestep}`} ─────</span>
                <span>REAL T1</span>
            </div>

            <div className="panel-grid">
                <div className="card">
                    <h3 className="card-title">Frame T</h3>
                    <div className="upload-box">
                        <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setFrame0)} />
                        {!frame0 ? (
                            <div><FileUp size={48} color="#484f58" style={{ margin: '0 auto 1rem' }} /><p>Click or drag image</p></div>
                        ) : (
                            <div><ImageIcon size={48} color="#58a6ff" style={{ margin: '0 auto 1rem' }} /><p>{frame0.name}</p></div>
                        )}
                    </div>
                </div>
                <div className="card">
                    <h3 className="card-title">Frame T+1</h3>
                    <div className="upload-box">
                        <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setFrame1)} />
                        {!frame1 ? (
                            <div><FileUp size={48} color="#484f58" style={{ margin: '0 auto 1rem' }} /><p>Click or drag image</p></div>
                        ) : (
                            <div><ImageIcon size={48} color="#58a6ff" style={{ margin: '0 auto 1rem' }} /><p>{frame1.name}</p></div>
                        )}
                    </div>
                </div>
            </div>

            <div className="controls">
                <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#8b949e' }}>Interpolation Timestep: <strong>{timestep}</strong></label>
                    <input type="range" min="0.1" max="0.9" step="0.1" value={timestep} onChange={e => setTimestep(parseFloat(e.target.value))} style={{ width: '100%', maxWidth: '300px' }} />
                </div>
                <button className="btn" onClick={handleGenerate} disabled={!frame0 || !frame1 || loading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {loading ? <div className="loader" /> : <Play size={18} />} {loading ? 'Processing...' : 'Generate Frame'}
                </button>
            </div>

            {error && <div style={{ background: '#3a1d1d', color: '#ff7b72', padding: '1rem', borderRadius: '6px', marginBottom: '2rem', border: '1px solid #ff7b72' }}><AlertCircle size={18} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />{error}</div>}

            {result && (
                <>
                    <h2 style={{ paddingBottom: '0.5rem', borderBottom: '1px solid #30363d', marginBottom: '1rem' }}>Results</h2>
                    <div className="results-grid">
                        <div className="result-panel">
                            <div className="result-panel-header">Frame T (Input)</div>
                            <div className="result-panel-content"><img src={URL.createObjectURL(frame0)} className="preview-img" alt="Frame T" /></div>
                        </div>
                        <div className="result-panel" style={{ border: '1px solid #58a6ff', boxShadow: '0 0 15px rgba(88, 166, 255, 0.1)' }}>
                            <div className="result-panel-header" style={{ color: '#58a6ff', fontWeight: 'bold' }}>Generated Frame T+{timestep}</div>
                            <div className="result-panel-content"><img src={`${API_URL}${result.generated_image_url}`} className="preview-img" style={{ maxHeight: '350px' }} alt="Generated" /></div>
                        </div>
                        <div className="result-panel">
                            <div className="result-panel-header">Frame T+1 (Input)</div>
                            <div className="result-panel-content"><img src={URL.createObjectURL(frame1)} className="preview-img" alt="Frame T+1" /></div>
                        </div>
                    </div>

                    <div className="panel-grid">
                        <div className="card" style={{ flex: 1 }}>
                            <h3 className="card-title" style={{ color: '#d2a8ff' }}>Interpolation Confidence Proxy</h3>
                            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                                <img src={`${API_URL}${result.confidence_map_url}`} className="preview-img" style={{ flex: 1, margin: 0, maxWidth: '50%' }} alt="Confidence Map" />
                                <div style={{ flex: 1 }}>
                                    <p style={{ fontSize: '0.9rem', color: '#8b949e', lineHeight: 1.5 }}>
                                        Structural consistency estimate; not a calibrated probability of correctness.
                                    </p>
                                    <div className="metric-box" style={{ marginTop: '1rem', border: '1px solid #d2a8ff', background: 'rgba(210, 168, 255, 0.05)' }}>
                                        <div className="metric-value" style={{ color: '#d2a8ff' }}>{(result.confidence_metrics.mean_confidence * 100).toFixed(1)}%</div>
                                        <div className="metric-label">Interpolation Confidence Proxy</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="card" style={{ flex: 1 }}>
                            <h3 className="card-title">Timing & Execution</h3>
                            <div className="metrics-grid">
                                <div className="metric-box">
                                    <Clock size={24} color="#8b949e" style={{ margin: '0 auto 0.5rem' }} />
                                    <div className="metric-value">{result.rife_inference_time_ms.toFixed(1)}</div>
                                    <div className="metric-label">RIFE Inference (ms)</div>
                                </div>
                                <div className="metric-box">
                                    <Clock size={24} color="#58a6ff" style={{ margin: '0 auto 0.5rem' }} />
                                    <div className="metric-value" style={{ color: '#58a6ff' }}>{result.total_processing_time_ms.toFixed(1)}</div>
                                    <div className="metric-label" style={{ color: '#58a6ff' }}>Total Processing (ms)</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

function EvaluationTab() {
    const [frame0, setFrame0] = useState(null);
    const [groundTruth, setGroundTruth] = useState(null);
    const [frame2, setFrame2] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e, setter) => {
        if (e.target.files && e.target.files[0]) setter(e.target.files[0]);
    };

    const handleEvaluate = async () => {
        if (!frame0 || !groundTruth || !frame2) return;
        setLoading(true); setError(null);
        const formData = new FormData();
        formData.append('frame0', frame0);
        formData.append('ground_truth', groundTruth);
        formData.append('frame2', frame2);
        try {
            const res = await axios.post(`${API_URL}/evaluate`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="panel-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
                <div className="card">
                    <h3 className="card-title">Frame T0</h3>
                    <div className="upload-box" style={{ padding: '2rem 1rem' }}>
                        <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setFrame0)} />
                        {!frame0 ? <div><FileUp size={32} color="#484f58" style={{ margin: '0 auto 0.5rem' }} /><p style={{ fontSize: '0.8rem' }}>Upload T0</p></div> : <div><ImageIcon size={32} color="#58a6ff" style={{ margin: '0 auto 0.5rem' }} /><p style={{ fontSize: '0.8rem' }}>{frame0.name}</p></div>}
                    </div>
                </div>
                <div className="card" style={{ border: '1px dashed #d2a8ff' }}>
                    <h3 className="card-title" style={{ color: '#d2a8ff' }}>Ground Truth T1</h3>
                    <div className="upload-box" style={{ padding: '2rem 1rem', background: 'rgba(210, 168, 255, 0.05)' }}>
                        <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setGroundTruth)} />
                        {!groundTruth ? <div><FileUp size={32} color="#d2a8ff" style={{ margin: '0 auto 0.5rem' }} /><p style={{ fontSize: '0.8rem' }}>Upload GT T1</p></div> : <div><ImageIcon size={32} color="#d2a8ff" style={{ margin: '0 auto 0.5rem' }} /><p style={{ fontSize: '0.8rem' }}>{groundTruth.name}</p></div>}
                    </div>
                </div>
                <div className="card">
                    <h3 className="card-title">Frame T2</h3>
                    <div className="upload-box" style={{ padding: '2rem 1rem' }}>
                        <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setFrame2)} />
                        {!frame2 ? <div><FileUp size={32} color="#484f58" style={{ margin: '0 auto 0.5rem' }} /><p style={{ fontSize: '0.8rem' }}>Upload T2</p></div> : <div><ImageIcon size={32} color="#58a6ff" style={{ margin: '0 auto 0.5rem' }} /><p style={{ fontSize: '0.8rem' }}>{frame2.name}</p></div>}
                    </div>
                </div>
            </div>

            <div className="controls" style={{ justifyContent: 'center' }}>
                <button className="btn" onClick={handleEvaluate} disabled={!frame0 || !groundTruth || !frame2 || loading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {loading ? <div className="loader" /> : <Play size={18} />} {loading ? 'Evaluating...' : 'Run Quantitative Benchmarks'}
                </button>
            </div>

            {error && <div style={{ background: '#3a1d1d', color: '#ff7b72', padding: '1rem', borderRadius: '6px', marginBottom: '2rem', border: '1px solid #ff7b72' }}><AlertCircle size={18} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />{error}</div>}

            {result && (
                <>
                    <h2 style={{ paddingBottom: '0.5rem', borderBottom: '1px solid #30363d', marginBottom: '1rem', marginTop: '2rem' }}>Evaluation Analytics</h2>

                    {result.dataset_info && (
                        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(48, 54, 61, 0.5)', borderRadius: '6px', borderLeft: '4px solid #58a6ff' }}>
                            <div style={{ fontSize: '0.9rem', color: '#8b949e', marginBottom: '0.3rem' }}>Dataset: <strong style={{ color: '#c9d1d9', fontSize: '1rem' }}>{result.dataset_info.dataset}</strong></div>
                            <div style={{ fontSize: '0.9rem', color: '#8b949e', marginBottom: '0.3rem' }}>Sequence: <strong style={{ color: '#c9d1d9', fontSize: '1rem' }}>{result.dataset_info.sequence}</strong></div>
                            <div style={{ fontSize: '0.9rem', color: '#8b949e' }}>Type: <strong style={{ color: '#c9d1d9', fontSize: '1rem' }}>{result.dataset_info.type}</strong></div>
                        </div>
                    )}

                    <div className="card" style={{ marginBottom: '2rem' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #30363d' }}>
                                    <th style={{ padding: '1rem', color: '#8b949e', textAlign: 'left' }}>Metric</th>
                                    <th style={{ padding: '1rem', color: '#58a6ff' }}>RIFE HDv3</th>
                                    <th style={{ padding: '1rem', color: '#ff7b72' }}>Linear Baseline</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style={{ borderBottom: '1px solid #21262d' }}>
                                    <td style={{ padding: '1rem', fontWeight: 'bold', textAlign: 'left' }}>Mean Absolute Error (↓)</td>
                                    <td style={{ padding: '1rem', fontSize: '1.2rem', fontWeight: 'bold', color: '#c9d1d9' }}>{result.rife_metrics.mae.toFixed(2)}</td>
                                    <td style={{ padding: '1rem', fontSize: '1.2rem', color: '#8b949e' }}>{result.linear_metrics.mae.toFixed(2)}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #21262d' }}>
                                    <td style={{ padding: '1rem', fontWeight: 'bold', textAlign: 'left' }}>PSNR (dB) (↑)</td>
                                    <td style={{ padding: '1rem', fontSize: '1.2rem', fontWeight: 'bold', color: '#c9d1d9' }}>{result.rife_metrics.psnr.toFixed(2)}</td>
                                    <td style={{ padding: '1rem', fontSize: '1.2rem', color: '#8b949e' }}>{result.linear_metrics.psnr.toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td style={{ padding: '1rem', fontWeight: 'bold', textAlign: 'left' }}>SSIM (↑)</td>
                                    <td style={{ padding: '1rem', fontSize: '1.2rem', fontWeight: 'bold', color: '#c9d1d9' }}>{result.rife_metrics.ssim.toFixed(4)}</td>
                                    <td style={{ padding: '1rem', fontSize: '1.2rem', color: '#8b949e' }}>{result.linear_metrics.ssim.toFixed(4)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div className="panel-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
                        <div className="card" style={{ padding: '1rem' }}>
                            <h3 className="card-title" style={{ color: '#d2a8ff', fontSize: '1rem' }}>Ground Truth T1</h3>
                            <img src={URL.createObjectURL(groundTruth)} className="preview-img" style={{ width: '100%', maxHeight: '400px' }} alt="Ground Truth" />
                        </div>
                        <div className="card" style={{ padding: '1rem' }}>
                            <h3 className="card-title" style={{ color: '#58a6ff', fontSize: '1rem' }}>RIFE Prediction T1</h3>
                            <img src={`${API_URL}${result.rife_image_url}`} className="preview-img" style={{ width: '100%', maxHeight: '400px' }} alt="RIFE Out" />
                        </div>
                        <div className="card" style={{ padding: '1rem' }}>
                            <h3 className="card-title" style={{ color: '#ff7b72', fontSize: '1rem' }}>Linear Prediction T1</h3>
                            <img src={`${API_URL}${result.linear_image_url}`} className="preview-img" style={{ width: '100%', maxHeight: '400px' }} alt="Linear Out" />
                        </div>
                        <div className="card" style={{ padding: '1rem' }}>
                            <h3 className="card-title" style={{ color: '#8b949e', fontSize: '1rem' }}>Interpolation Confidence Map</h3>
                            <img src={`${API_URL}${result.confidence_map_url}`} className="preview-img" style={{ width: '100%', maxHeight: '400px' }} alt="Confidence Map" />
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

function App() {
    const [mode, setMode] = useState('interpolate'); // 'interpolate' or 'evaluate'

    return (
        <div className="app-container">
            <header>
                <h1>FRAMEFLOW</h1>
                <div className="subtitle">AI-Enabled Spatial-Temporal Satellite Image Frame Interpolation</div>

                <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'center' }}>
                    <button
                        onClick={() => setMode('interpolate')}
                        style={{ padding: '0.5rem 2rem', background: mode === 'interpolate' ? '#58a6ff' : 'transparent', color: mode === 'interpolate' ? '#0d1117' : '#c9d1d9', border: '1px solid #58a6ff', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                        Interpolation
                    </button>
                    <button
                        onClick={() => setMode('evaluate')}
                        style={{ padding: '0.5rem 2rem', background: mode === 'evaluate' ? '#d2a8ff' : 'transparent', color: mode === 'evaluate' ? '#0d1117' : '#c9d1d9', border: '1px solid #d2a8ff', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                        Evaluation Benchmark
                    </button>
                </div>
            </header>

            {mode === 'interpolate' ? <InterpolationTab /> : <EvaluationTab />}
        </div>
    );
}

export default App;
