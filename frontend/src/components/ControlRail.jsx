import React from 'react';
import FrameUploader from './FrameUploader';
import TimestepControl from './TimestepControl';
import { Play, Layers } from 'lucide-react';

export default function ControlRail({
    frame0,
    frame1,
    timestep,
    loading,
    hasResult,
    onFrame0Change,
    onFrame1Change,
    onTimestepChange,
    onGenerate,
}) {
    const canGenerate = frame0 && frame1 && !loading;

    return (
        <aside style={{
            width: 'var(--rail-width)',
            flexShrink: 0,
            background: 'var(--bg-primary)',
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
        }}>
            {/* Scrollable content */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '16px',
            }}>
                {/* Section: Input Observations */}
                <div style={{ marginBottom: 20 }}>
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
                        Input Observations
                    </div>

                    <FrameUploader
                        label="Frame T₀"
                        file={frame0}
                        onFileChange={onFrame0Change}
                    />

                    {/* Connection line */}
                    {frame0 && frame1 && (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            padding: '4px 0',
                            margin: '-4px 0',
                        }}>
                            <span style={{ fontSize: '0.643rem', color: 'var(--text-muted)' }}>T₀</span>
                            <div style={{
                                flex: 1,
                                height: 1,
                                background: 'var(--border-default)',
                            }} />
                            <span style={{ fontSize: '0.643rem', color: 'var(--text-muted)' }}>T₂</span>
                        </div>
                    )}

                    <FrameUploader
                        label="Frame T₂"
                        file={frame1}
                        onFileChange={onFrame1Change}
                    />
                </div>

                {/* Section: Interpolation */}
                <div style={{ marginBottom: 20 }}>
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
                        <Activity size={11} />
                        Interpolation
                    </div>

                    <TimestepControl
                        value={timestep}
                        onChange={onTimestepChange}
                        disabled={loading}
                    />
                </div>
            </div>

            {/* Generate button */}
            <div style={{
                padding: '12px 16px',
                borderTop: '1px solid var(--border-subtle)',
            }}>
                <button
                    className="btn-primary"
                    onClick={onGenerate}
                    disabled={!canGenerate}
                    aria-label="Generate intermediate frame"
                >
                    {loading ? (
                        <>
                            <span className="spinner" />
                            Running RIFE HDv3…
                        </>
                    ) : (
                        <>
                            <Play size={15} />
                            Generate Intermediate Frame
                        </>
                    )}
                </button>

                {hasResult && !loading && (
                    <div className="success-banner" style={{ marginTop: 8 }}>
                        ✓ Interpolation complete
                    </div>
                )}
            </div>
        </aside>
    );
}

function Activity(props) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width={props.size || 24} height={props.size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
    );
}
