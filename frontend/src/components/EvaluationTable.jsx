import React from 'react';

function Row({ metric, direction, rifeVal, linearVal }) {
    const rifeIsBetter = direction === '↓'
        ? rifeVal < linearVal
        : rifeVal > linearVal;

    return (
        <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
            <td style={{
                padding: '10px 14px',
                fontSize: '0.857rem',
                fontWeight: 500,
                color: 'var(--text-primary)',
                textAlign: 'left',
            }}>
                {metric} <span style={{ color: 'var(--text-muted)', fontSize: '0.714rem' }}>{direction}</span>
            </td>
            <td style={{
                padding: '10px 14px',
                fontFamily: 'var(--font-mono)',
                fontSize: '1rem',
                fontWeight: 700,
                color: rifeIsBetter ? 'var(--accent)' : 'var(--text-primary)',
                textAlign: 'center',
            }}>
                {rifeVal}
            </td>
            <td style={{
                padding: '10px 14px',
                fontFamily: 'var(--font-mono)',
                fontSize: '1rem',
                color: !rifeIsBetter ? 'var(--accent)' : 'var(--text-secondary)',
                textAlign: 'center',
            }}>
                {linearVal}
            </td>
        </tr>
    );
}

export default function EvaluationTable({ rifeMetrics, linearMetrics }) {
    if (!rifeMetrics || !linearMetrics) return null;

    return (
        <div className="panel">
            <div className="panel-header">
                RIFE HDv3 vs Linear Interpolation
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-default)' }}>
                            <th style={{
                                padding: '10px 14px',
                                fontSize: '0.714rem',
                                fontWeight: 600,
                                letterSpacing: '0.06em',
                                textTransform: 'uppercase',
                                color: 'var(--text-muted)',
                                textAlign: 'left',
                            }}>
                                Metric
                            </th>
                            <th style={{
                                padding: '10px 14px',
                                fontSize: '0.714rem',
                                fontWeight: 600,
                                letterSpacing: '0.06em',
                                textTransform: 'uppercase',
                                color: 'var(--accent)',
                                textAlign: 'center',
                            }}>
                                RIFE HDv3
                            </th>
                            <th style={{
                                padding: '10px 14px',
                                fontSize: '0.714rem',
                                fontWeight: 600,
                                letterSpacing: '0.06em',
                                textTransform: 'uppercase',
                                color: 'var(--text-secondary)',
                                textAlign: 'center',
                            }}>
                                Linear
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <Row
                            metric="Mean Absolute Error"
                            direction="↓"
                            rifeVal={rifeMetrics.mae.toFixed(3)}
                            linearVal={linearMetrics.mae.toFixed(3)}
                        />
                        {rifeMetrics.rmse != null && (
                            <Row
                                metric="Root Mean Square Error"
                                direction="↓"
                                rifeVal={rifeMetrics.rmse.toFixed(3)}
                                linearVal={linearMetrics.rmse.toFixed(3)}
                            />
                        )}
                        <Row
                            metric="PSNR"
                            direction="↑"
                            rifeVal={rifeMetrics.psnr.toFixed(2) + ' dB'}
                            linearVal={linearMetrics.psnr.toFixed(2) + ' dB'}
                        />
                        <Row
                            metric="SSIM"
                            direction="↑"
                            rifeVal={rifeMetrics.ssim.toFixed(4)}
                            linearVal={linearMetrics.ssim.toFixed(4)}
                        />
                    </tbody>
                </table>
            </div>
        </div>
    );
}
