import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
    const [frame0, setFrame0] = useState(null);
    const [frame1, setFrame1] = useState(null);
    const [timestep, setTimestep] = useState(0.5);
    const [visualizeFlow, setVisualizeFlow] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e, setter) => {
        if (e.target.files && e.target.files[0]) setter(e.target.files[0]);
    };

    const handleGenerate = async () => {
        if (!frame0 || !frame1) return;
        setLoading(true);
        setError(null);
        setResult(null);
        const formData = new FormData();
        formData.append('frame0', frame0);
        formData.append('frame1', frame1);
        formData.append('timestep', timestep);
        
        try {
            const res = await axios.post(`${API_URL}/interpolate`, formData, { 
                headers: { 'Content-Type': 'multipart/form-data' } 
            });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="logo-section">
                    <div className="logo-badge">FF</div>
                    <div className="logo-text">FrameFlow</div>
                </div>
                <div className="header-badge">AI-ASSISTED · OBSERVATIONAL DEMO</div>
            </header>

            <section className="hero-section">
                <div className="hero-content">
                    <span className="hero-kicker">TEMPORAL DETAIL, MADE VISIBLE</span>
                    <h1 className="hero-title">
                        Read the moment between<br/>
                        <span className="highlight">two satellite frames.</span>
                    </h1>
                    <p className="hero-description">
                        FrameFlow uses pretrained RIFE to generate one plausible midpoint for exploratory disaster monitoring workflows. Generated images are visual aids, never real observations or predictions.
                    </p>
                </div>
                <div className="hero-graphic">
                    <div className="orbit orbit-1"></div>
                    <div className="orbit orbit-2"></div>
                    <div className="orbit orbit-3"></div>
                    <div className="planet planet-green"></div>
                    <div className="planet planet-red"></div>
                    <div className="planet planet-small"></div>
                </div>
            </section>

            <main className="main-grid">
                {/* Left Panel */}
                <div className="panel">
                    <div className="panel-header">
                        <div>
                            <span className="panel-kicker">01 · INPUT PAIR</span>
                            <h2 className="panel-title">Set the observed interval</h2>
                        </div>
                        <span className="panel-badge">T0 + T1</span>
                    </div>

                    <div className="upload-grid">
                        <div className="upload-box">
                            <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setFrame0)} />
                            {!frame0 ? (
                                <div>
                                    <span className="upload-box-kicker">FRAME T0 · EARLIER</span>
                                    <h3 className="upload-box-title">Choose a PNG or JPEG</h3>
                                    <p className="upload-box-desc">Satellite imagery or other image pairs · v1 is observational</p>
                                </div>
                            ) : (
                                <div className="file-uploaded-state">
                                    <span className="upload-box-kicker" style={{color: 'var(--text-primary)'}}>FRAME T0 · EARLIER</span>
                                    <div className="file-uploaded-name">{frame0.name}</div>
                                </div>
                            )}
                        </div>
                        <div className="upload-box">
                            <input type="file" className="file-input" accept="image/*" onChange={e => handleFileChange(e, setFrame1)} />
                            {!frame1 ? (
                                <div>
                                    <span className="upload-box-kicker">FRAME T1 · LATER</span>
                                    <h3 className="upload-box-title">Choose a PNG or JPEG</h3>
                                    <p className="upload-box-desc">Satellite imagery or other image pairs · v1 is observational</p>
                                </div>
                            ) : (
                                <div className="file-uploaded-state">
                                    <span className="upload-box-kicker" style={{color: 'var(--text-primary)'}}>FRAME T1 · LATER</span>
                                    <div className="file-uploaded-name">{frame1.name}</div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="controls-row">
                        <span className="control-label">Target timestep</span>
                        <span className="control-value">T{timestep}</span>
                    </div>
                    
                    <input 
                        type="range" 
                        min="0.1" max="0.9" step="0.1" 
                        value={timestep} 
                        onChange={e => setTimestep(parseFloat(e.target.value))} 
                    />
                    
                    <div className="timeline-labels">
                        <span>T0</span>
                        <span>T0.5 midpoint</span>
                        <span>T1</span>
                    </div>

                    <div className="actions-row">
                        <div style={{flex: 1}}></div>
                        <label className="checkbox-label" style={{flex: 1, justifyContent: 'flex-end'}}>
                            <input type="checkbox" className="checkbox-input" checked={visualizeFlow} onChange={e => setVisualizeFlow(e.target.checked)} />
                            Optical flow visualization
                        </label>
                    </div>

                    <button className="btn-primary" style={{marginTop: '1.5rem'}} onClick={handleGenerate} disabled={!frame0 || !frame1 || loading}>
                        {loading ? (
                            <><span className="spinner" style={{marginRight: '0.5rem', verticalAlign: 'middle'}}></span> Processing...</>
                        ) : 'Generate midpoint →'}
                    </button>
                    
                    {error && (
                        <div style={{marginTop: '1rem', color: 'var(--accent-red)', fontSize: '0.85rem'}}>
                            {error}
                        </div>
                    )}
                </div>

                {/* Right Panel */}
                <div className="panel">
                    <div className="panel-header" style={{marginBottom: '1rem'}}>
                        <div>
                            <span className="panel-kicker">TIME AXIS</span>
                            <h2 className="panel-title">Observed + inferred</h2>
                        </div>
                    </div>
                    
                    <div className="time-axis-graphic">
                        <div className="time-line"></div>
                        <div className="time-point" style={{left: '10%'}}>
                            <div className="time-dot real"></div>
                            <div className="time-label">T0<span>real input</span></div>
                        </div>
                        <div className="time-point" style={{left: `${timestep * 100}%`}}>
                            <div className="time-dot generated"></div>
                            <div className="time-label">T{timestep}<span>AI generated</span></div>
                        </div>
                        <div className="time-point" style={{left: '90%'}}>
                            <div className="time-dot real"></div>
                            <div className="time-label">T1<span>real input</span></div>
                        </div>
                    </div>

                    <div className="time-axis-legend">
                        <div className="legend-item">
                            <div className="legend-dot real"></div> Real input
                        </div>
                        <div className="legend-item">
                            <div className="legend-dot generated"></div> AI generated
                        </div>
                        <p className="legend-desc">
                            The midpoint is reconstructed for visual exploration and must be reviewed alongside the real frames.
                        </p>
                    </div>
                </div>
            </main>

            {/* Results Section */}
            {result && (
                <div className="results-preview-grid">
                    <div className="result-card">
                        <div className="result-header">Frame T0 (Input)</div>
                        <img src={URL.createObjectURL(frame0)} className="result-img" alt="Frame T0" />
                    </div>
                    <div className="result-card highlight">
                        <div className="result-header highlight">Generated Frame T{timestep}</div>
                        <img src={`${API_URL}${result.generated_image_url}`} className="result-img" alt="Generated" />
                        <div style={{padding: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)', textAlign: 'center'}}>
                            Confidence Proxy: {(result.confidence_metrics.mean_confidence * 100).toFixed(1)}%<br/>
                            Inference: {result.rife_inference_time_ms.toFixed(1)}ms
                        </div>
                    </div>
                    <div className="result-card">
                        <div className="result-header">Frame T1 (Input)</div>
                        <img src={URL.createObjectURL(frame1)} className="result-img" alt="Frame T1" />
                    </div>
                </div>
            )}

            <footer className="app-footer">
                <div>FrameFlow v1 · pretrained RIFE backbone</div>
                <div>Generated imagery is demonstrative only · no disaster prediction</div>
            </footer>
        </div>
    );
}

export default App;
