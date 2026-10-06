import React from 'react';
import { Clock, Cpu, Activity } from 'lucide-react';

function MetricCard({ label, value, unit, direction, accent }) {
    const color = accent || 'var(--text-primary)';
    return (
        <div style={{
            flex: '1 1 110px',
            padding: '12px 14px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            textAlign: 'center',
            minWidth: 100,
        }}>
            <div style={{
                fontSize: '0.643rem',
                fontWeight: 600,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                color: 'var(--text-secondary)',
                marginBottom: 6,
            }}>
                {label} {direction && <span style={{ opacity: 0.6 }}>{direction}</span>}
            </div>
            <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '1.25rem',
                fontWeight: 700,
                color,
                lineHeight: 1.2,
            }}>
                {value}
            </div>
            {unit && (
                <div style={{
                    fontSize: '0.643rem',
                    color: 'var(--text-muted)',
                    marginTop: 2,
                }}>
                    {unit}
                </div>
            )}
        </div>
    );
}

export default function MetricsPanel({ inferenceTime, totalTime, device, timestep, rife_metrics }) {
    return (
        <div style={{
            display: 'flex',
            gap: 6,
            flexWrap: 'wrap',
        }}>
            {rife_metrics && (
                <>
                    <MetricCard label="MAE" value={rife_metrics.mae.toFixed(3)} direction="↓" />
                    <MetricCard label="RMSE" value={rife_metrics.rmse?.toFixed(3) || '–'} direction="↓" />
                    <MetricCard label="PSNR" value={rife_metrics.psnr.toFixed(2)} unit="dB" direction="↑" accent="var(--accent)" />
                    <MetricCard label="SSIM" value={rife_metrics.ssim.toFixed(4)} direction="↑" accent="var(--accent)" />
                </>
            )}
            {inferenceTime != null && (
                <MetricCard label="RIFE Inference" value={inferenceTime.toFixed(1)} unit="ms" accent="var(--violet)" />
            )}
            {totalTime != null && (
                <MetricCard label="Total Processing" value={totalTime.toFixed(1)} unit="ms" />
            )}
            {device && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '8px 14px',
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '0.714rem',
                    color: 'var(--text-secondary)',
                    fontFamily: 'var(--font-mono)',
                }}>
                    <Cpu size={12} />
                    RIFE HDv3 · {device} · t = {timestep?.toFixed(2) || '0.50'}
                </div>
            )}
        </div>
    );
}
