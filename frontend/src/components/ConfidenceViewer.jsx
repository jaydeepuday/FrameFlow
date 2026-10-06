import React from 'react';
import { Info } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function ConfidenceViewer({ confidenceMapUrl, metrics }) {
    if (!confidenceMapUrl) return null;

    const mapSrc = `${API_BASE_URL}${confidenceMapUrl}`;

    return (
        <div className="panel" style={{ marginTop: 6 }}>
            <div className="panel-header">
                <span>Interpolation Confidence Proxy</span>
            </div>

            <div style={{
                display: 'flex',
                gap: 16,
                padding: 16,
                alignItems: 'flex-start',
                flexWrap: 'wrap',
            }}>
                {/* Heatmap */}
                <div style={{
                    flex: '1 1 280px',
                    minWidth: 200,
                    background: 'var(--bg-deep)',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'hidden',
                    border: '1px solid var(--border-subtle)',
                }}>
                    <img
                        src={mapSrc}
                        alt="Interpolation confidence heatmap"
                        style={{
                            width: '100%',
                            height: 'auto',
                            display: 'block',
                            objectFit: 'contain',
                        }}
                    />
                    {/* Legend */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '6px 12px',
                        borderTop: '1px solid var(--border-subtle)',
                    }}>
                        <span style={{ fontSize: '0.643rem', color: 'var(--text-muted)' }}>Low</span>
                        <div style={{
                            flex: 1,
                            margin: '0 10px',
                            height: 6,
                            borderRadius: 3,
                            background: 'linear-gradient(to right, #1a0530, #8b0000, #ff4500, #ffa500, #ffff00)',
                            alignSelf: 'center',
                        }} />
                        <span style={{ fontSize: '0.643rem', color: 'var(--text-muted)' }}>High</span>
                    </div>
                </div>

                {/* Metrics + Disclaimer */}
                <div style={{ flex: '1 1 200px', minWidth: 160 }}>
                    {metrics && (
                        <div style={{
                            padding: '14px 16px',
                            background: 'var(--violet-dim)',
                            border: '1px solid var(--violet-border)',
                            borderRadius: 'var(--radius-md)',
                            marginBottom: 12,
                            textAlign: 'center',
                        }}>
                            <div style={{
                                fontFamily: 'var(--font-mono)',
                                fontSize: '1.5rem',
                                fontWeight: 700,
                                color: 'var(--violet)',
                            }}>
                                {(metrics.mean_confidence * 100).toFixed(1)}%
                            </div>
                            <div style={{
                                fontSize: '0.714rem',
                                color: 'var(--text-secondary)',
                                marginTop: 4,
                            }}>
                                Mean Structural Confidence Proxy
                            </div>
                        </div>
                    )}

                    <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 8,
                        padding: '10px 12px',
                        background: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--border-subtle)',
                    }}>
                        <Info size={14} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: 1 }} />
                        <p style={{
                            fontSize: '0.714rem',
                            color: 'var(--text-muted)',
                            lineHeight: 1.5,
                            margin: 0,
                        }}>
                            Structural consistency estimate; not a calibrated probability.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
