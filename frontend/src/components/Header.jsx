import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StatusIndicator from './StatusIndicator';
import { Activity, Cpu } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Header({ activeTab, onTabChange }) {
    const [health, setHealth] = useState(null);
    const [modelInfo, setModelInfo] = useState(null);

    useEffect(() => {
        axios.get(`${API_BASE_URL}/health`).then(r => setHealth(r.data)).catch(() => { });
        axios.get(`${API_BASE_URL}/model/info`).then(r => setModelInfo(r.data)).catch(() => { });
    }, []);

    return (
        <header style={{
            height: 'var(--header-height)',
            background: 'var(--bg-primary)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 20px',
            flexShrink: 0,
            zIndex: 100,
        }}>
            {/* Left: Brand + Nav */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                    <h1 style={{
                        fontSize: '1.15rem',
                        fontWeight: 800,
                        letterSpacing: '0.06em',
                        color: 'var(--text-primary)',
                        margin: 0,
                    }}>
                        FRAMEFLOW
                    </h1>
                    <span style={{
                        fontSize: '0.714rem',
                        color: 'var(--text-muted)',
                        letterSpacing: '0.02em',
                        display: 'none',
                    }}
                        className="header-subtitle"
                    >
                        Satellite Temporal Interpolation
                    </span>
                </div>

                <div className="tab-bar" style={{ marginLeft: 8 }}>
                    <button
                        className={`tab-btn ${activeTab === 'interpolate' ? 'active' : ''}`}
                        onClick={() => onTabChange('interpolate')}
                    >
                        Interpolate
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'evaluate' ? 'active' : ''}`}
                        onClick={() => onTabChange('evaluate')}
                    >
                        Evaluate
                    </button>
                </div>
            </div>

            {/* Right: System Status */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                {health && (
                    <StatusIndicator
                        online={health.cuda_available}
                        label={health.cuda_available ? 'CUDA' : 'CPU'}
                    />
                )}
                {modelInfo && (
                    <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        fontSize: '0.786rem',
                        color: 'var(--text-secondary)',
                        padding: '4px 10px',
                        background: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border-subtle)',
                    }}>
                        <Cpu size={12} />
                        {modelInfo.model_variant}
                    </span>
                )}
                {health && (
                    <span style={{
                        fontSize: '0.714rem',
                        color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                    }}>
                        {health.device}
                    </span>
                )}
            </div>
        </header>
    );
}
