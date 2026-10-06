import React, { useState } from 'react';
import axios from 'axios';
import { AlertCircle, Play, Layers } from 'lucide-react';
import FrameUploader from '../components/FrameUploader';
import TemporalTimeline from '../components/TemporalTimeline';
import SatelliteViewer from '../components/SatelliteViewer';
import ConfidenceViewer from '../components/ConfidenceViewer';
import MetricsPanel from '../components/MetricsPanel';
import EvaluationTable from '../components/EvaluationTable';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function EvaluatePage() {
    const [frame0, setFrame0] = useState(null);
    const [groundTruth, setGroundTruth] = useState(null);
    const [frame2, setFrame2] = useState(null);

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleEvaluate = async () => {
        if (!frame0 || !groundTruth || !frame2) return;
        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('frame0', frame0);
        formData.append('ground_truth', groundTruth);
        formData.append('frame2', frame2);

        try {
            const res = await axios.post(`${API_BASE_URL}/evaluate`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Evaluation request failed.');
        } finally {
            setLoading(false);
        }
    };

    const f0Url = frame0 ? URL.createObjectURL(frame0) : null;
    const gtUrl = groundTruth ? URL.createObjectURL(groundTruth) : null;
    const f2Url = frame2 ? URL.createObjectURL(frame2) : null;

    return (
        <div style={{
            display: 'flex',
            flex: 1,
            height: 'calc(100vh - var(--header-height))',
            overflow: 'hidden',
        }}>
            {/* Left Control Rail for Eval */}
            <aside style={{
                width: 'var(--rail-width)',
                flexShrink: 0,
                background: 'var(--bg-primary)',
                borderRight: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
            }}>
                <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
                    <div style={{
                        fontSize: '0.643rem',
                        fontWeight: 700,
                        letterSpacing: '0.1em',
                        textTransform: 'uppercase',
                        color: 'var(--text-muted)',
                        marginBottom: 12,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                    }}>
                        <Layers size={11} />
                        Evaluation Data
                    </div>

                    <FrameUploader label="Frame T₀" file={frame0} onFileChange={(f) => { setFrame0(f); setResult(null); }} />

                    <div style={{ margin: '16px 0', padding: '16px', background: 'var(--violet-dim)', border: '1px solid var(--violet-border)', borderRadius: 'var(--radius-md)' }}>
                        <FrameUploader label="Ground Truth T₁" file={groundTruth} onFileChange={(f) => { setGroundTruth(f); setResult(null); }} />
                    </div>

                    <FrameUploader label="Frame T₂" file={frame2} onFileChange={(f) => { setFrame2(f); setResult(null); }} />
                </div>

                <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border-subtle)' }}>
                    <button
                        className="btn-primary"
                        onClick={handleEvaluate}
                        disabled={!frame0 || !groundTruth || !frame2 || loading}
                    >
                        {loading ? (
                            <><span className="spinner" /> Evaluating...</>
                        ) : (
                            <><Play size={15} /> Run Evaluation Benchmark</>
                        )}
                    </button>
                </div>
            </aside>

            {/* Main View */}
            <main style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                minWidth: 0,
                overflowY: 'auto',
                background: 'var(--bg-deep)',
            }}>
                {error && (
                    <div style={{ padding: 16 }}>
                        <div className="error-banner">
                            <AlertCircle size={16} style={{ marginTop: 2, flexShrink: 0 }} />
                            <div><strong>Error: </strong> {error}</div>
                        </div>
                    </div>
                )}

                <TemporalTimeline timestep={0.5} hasResult={!!result} />

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 16, gap: 16 }}>

                    {/* Main 4-panel Temporal Viewer */}
                    <SatelliteViewer
                        panels={[
                            {
                                key: 't0',
                                label: 'T₀',
                                src: f0Url,
                                alwaysShow: true
                            },
                            {
                                key: 'gt',
                                label: 'Ground Truth T₁',
                                src: gtUrl,
                                alwaysShow: true
                            },
                            {
                                key: 'pred_rife',
                                label: 'Predicted T₁ (RIFE HDv3)',
                                src: result ? `${API_BASE_URL}${result.rife_image_url}` : null,
                                emphasis: true,
                                alwaysShow: true
                            },
                            {
                                key: 'pred_linear',
                                label: 'Linear Baseline T₁',
                                src: result ? `${API_BASE_URL}${result.linear_image_url}` : null,
                                alwaysShow: false
                            }
                        ]}
                    />

                    {/* Results Details */}
                    {result && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                            {/* Dataset Info Strip */}
                            {result.dataset_info && (
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 16,
                                    padding: '12px 16px',
                                    background: 'var(--accent-dim)',
                                    border: '1px solid var(--accent-border)',
                                    borderRadius: 'var(--radius-md)',
                                    fontSize: '0.786rem',
                                }}>
                                    <div style={{ color: 'var(--text-secondary)' }}>
                                        Dataset: <strong style={{ color: 'var(--text-primary)' }}>{result.dataset_info.dataset}</strong>
                                    </div>
                                    <div style={{ color: 'var(--text-secondary)' }}>
                                        Sequence: <strong style={{ color: 'var(--text-primary)' }}>{result.dataset_info.sequence}</strong>
                                    </div>
                                    <div style={{ color: 'var(--text-secondary)' }}>
                                        Type: <strong style={{ color: 'var(--accent)' }}>{result.dataset_info.type}</strong>
                                    </div>
                                </div>
                            )}

                            <MetricsPanel
                                inferenceTime={result.rife_inference_time_ms}
                                totalTime={result.total_processing_time_ms}
                                rife_metrics={result.rife_metrics}
                            />

                            <EvaluationTable
                                rifeMetrics={result.rife_metrics}
                                linearMetrics={result.linear_metrics}
                            />

                            <ConfidenceViewer
                                confidenceMapUrl={result.confidence_map_url}
                            />
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
