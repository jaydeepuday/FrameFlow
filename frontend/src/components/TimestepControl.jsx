import React from 'react';

export default function TimestepControl({ value, onChange, disabled }) {
    return (
        <div>
            <div style={{
                display: 'flex',
                alignItems: 'baseline',
                justifyContent: 'space-between',
                marginBottom: 10,
            }}>
                <span style={{
                    fontSize: '0.714rem',
                    fontWeight: 600,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: 'var(--text-secondary)',
                }}>
                    Timestep
                </span>
                <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '1.15rem',
                    fontWeight: 700,
                    color: 'var(--accent)',
                }}>
                    {value.toFixed(2)}
                </span>
            </div>

            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
            }}>
                <span style={{ fontSize: '0.643rem', color: 'var(--text-muted)', fontWeight: 600 }}>T₀</span>
                <input
                    type="range"
                    min="0.1"
                    max="0.9"
                    step="0.1"
                    value={value}
                    onChange={(e) => onChange(parseFloat(e.target.value))}
                    disabled={disabled}
                    style={{ flex: 1 }}
                    aria-label="Interpolation timestep"
                />
                <span style={{ fontSize: '0.643rem', color: 'var(--text-muted)', fontWeight: 600 }}>T₂</span>
            </div>
        </div>
    );
}
