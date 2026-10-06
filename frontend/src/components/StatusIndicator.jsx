import React from 'react';

export default function StatusIndicator({ online, label }) {
    return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span className={`pulse-dot ${online ? 'online' : 'offline'}`} />
            <span style={{ fontSize: '0.786rem', color: online ? 'var(--success)' : 'var(--error)' }}>
                {label}
            </span>
        </span>
    );
}
