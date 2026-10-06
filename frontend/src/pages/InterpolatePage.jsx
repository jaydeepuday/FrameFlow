import React, { useState } from 'react';
import axios from 'axios';
import { AlertCircle } from 'lucide-react';
import ControlRail from '../components/ControlRail';
import TemporalTimeline from '../components/TemporalTimeline';
import SatelliteViewer from '../components/SatelliteViewer';
import ConfidenceViewer from '../components/ConfidenceViewer';
import MetricsPanel from '../components/MetricsPanel';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function InterpolatePage() {
    const [frame0, setFrame0] = useState(null);
    const [frame1, setFrame1] = useState(null);
    const [timestep, setTimestep] = useState(0.5);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleGenerate = async () => {
        if (!frame0 || !frame1) return;
        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('frame0', frame0);
        formData.append('frame1', frame1);
        formData.append('timestep', timestep);

        console.log('--- INTERPOLATE API REQUEST START ---');
        console.log('Target URL:', `${API_BASE_URL}/interpolate`);
        console.log('FormData keys:', Array.from(formData.keys()));
        console.log('Frame 0:', frame0.name, frame0.type, frame0.size);
        console.log('Frame T+1:', frame1.name, frame1.type, frame1.size);
        console.log('Timestep:', timestep);
        console.log('Axios config:', { headers: { 'Content-Type': 'multipart/form-data' } });

        try {
            const res = await axios.post(`${API_BASE_URL}/interpolate`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            console.log('--- INTERPOLATE API RESPONSE ---');
            console.log('Status:', res.status);
            console.log('Data:', res.data);
            setResult(res.data);
        } catch (err) {
            console.error('--- INTERPOLATE API ERROR ---');
            console.error('Response Status:', err.response?.status);
            console.error('Response Data:', err.response?.data);
            console.error('Caught error object:', err);
            setError(err.response?.data?.detail || err.message || 'Interpolation request failed.');
        } finally {
            setLoading(false);
        }
    };

    const frame0PreviewUrl = frame0 ? URL.createObjectURL(frame0) : null;
    const frame1PreviewUrl = frame1 ? URL.createObjectURL(frame1) : null;

    return (
        <div style={{
            display: 'flex',
            flex: 1,
            height: 'calc(100vh - var(--header-height))',
            overflow: 'hidden',
        }}>
            <ControlRail
                frame0={frame0}
                frame1={frame1}
                timestep={timestep}
                loading={loading}
                hasResult={!!result}
                onFrame0Change={(f) => { setFrame0(f); setResult(null); setError(null); }}
                onFrame1Change={(f) => { setFrame1(f); setResult(null); setError(null); }}
                onTimestepChange={(v) => { setTimestep(v); setResult(null); }}
                onGenerate={handleGenerate}
            />

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
                            <div>
                                <strong>Error: </strong> {error}
                            </div>
                        </div>
                    </div>
                )}

                {/* Timeline Header */}
                <TemporalTimeline timestep={timestep} hasResult={!!result} />

                {/* Main Viewer Architecture */}
                <div style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    padding: 16,
                    gap: 16,
                }}>
                    {/* Main 3-panel viewer */}
                    <SatelliteViewer
                        panels={[
                            {
                                key: 't0',
                                label: 'T₀',
                                src: frame0PreviewUrl,
                                alwaysShow: true
                            },
                            {
                                key: 't1_pred',
                                label: `Predicted T+${timestep.toFixed(2)}`,
                                src: result ? `${API_BASE_URL}${result.generated_image_url}` : null,
                                emphasis: true,
                                alwaysShow: true
                            },
                            {
                                key: 't2',
                                label: 'T₂',
                                src: frame1PreviewUrl,
                                alwaysShow: true
                            }
                        ]}
                    />

                    {/* Metrics & Confidence */}
                    {result && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            <MetricsPanel
                                inferenceTime={result.rife_inference_time_ms}
                                totalTime={result.total_processing_time_ms}
                                device={result.device}
                                timestep={result.timestep}
                            />

                            <ConfidenceViewer
                                confidenceMapUrl={result.confidence_map_url}
                                metrics={result.confidence_metrics}
                            />
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
