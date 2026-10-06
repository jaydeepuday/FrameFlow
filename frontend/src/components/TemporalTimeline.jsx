import React from 'react';

export default function TemporalTimeline({ timestep, hasResult }) {
    const pct = ((timestep - 0.1) / 0.8) * 100;

    return (
        <div style={{
            padding: '12px 16px',
            background: 'var(--bg-surface)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: 16,
        }}>
            {/* T0 */}
            <span style={{
                fontSize: '0.714rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                letterSpacing: '0.04em',
                flexShrink: 0,
            }}>
                T₀
            </span>

            {/* Timeline bar */}
            <div style={{ flex: 1, position: 'relative', height: 20 }}>
                {/* Track */}
                <div style={{
                    position: 'absolute',
                    top: 9,
                    left: 0,
                    right: 0,
                    height: 2,
                    background: 'var(--border-default)',
                    borderRadius: 1,
                }} />

                {/* Predicted marker */}
                <div style={{
                    position: 'absolute',
                    left: `${pct}%`,
                    top: 0,
                    transform: 'translateX(-50%)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}>
                    <div style={{
                        width: 12,
                        height: 12,
                        borderRadius: '2px',
                        transform: 'rotate(45deg)',
                        background: hasResult ? 'var(--accent)' : 'var(--border-strong)',
                        border: `2px solid ${hasResult ? 'var(--accent)' : 'var(--border-strong)'}`,
                        boxShadow: hasResult ? '0 0 8px var(--accent-glow)' : 'none',
                    }} />
                </div>

                {/* Endpoint dots */}
                <div style={{
                    position: 'absolute',
                    left: 0,
                    top: 6,
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: 'var(--text-muted)',
                }} />
                <div style={{
                    position: 'absolute',
                    right: 0,
                    top: 6,
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: 'var(--text-muted)',
                }} />
            </div>

            {/* T2 */}
            <span style={{
                fontSize: '0.714rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                letterSpacing: '0.04em',
                flexShrink: 0,
            }}>
                T₂
            </span>

            {/* Label */}
            <span style={{
                fontSize: '0.643rem',
                color: hasResult ? 'var(--accent)' : 'var(--text-muted)',
                fontFamily: 'var(--font-mono)',
                whiteSpace: 'nowrap',
                flexShrink: 0,
            }}>
                t = {timestep.toFixed(2)}
            </span>
        </div>
    );
}
