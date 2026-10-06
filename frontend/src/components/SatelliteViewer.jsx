import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

function ImagePanel({ label, src, alt, emphasis, onFullscreen }) {
    const [zoom, setZoom] = useState(1);
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [dragging, setDragging] = useState(false);
    const lastPos = useRef({ x: 0, y: 0 });
    const containerRef = useRef(null);

    const resetView = useCallback(() => {
        setZoom(1);
        setPan({ x: 0, y: 0 });
    }, []);

    const handleWheel = useCallback((e) => {
        e.preventDefault();
        setZoom(z => Math.max(0.5, Math.min(8, z * (e.deltaY < 0 ? 1.15 : 0.87))));
    }, []);

    useEffect(() => {
        const el = containerRef.current;
        if (!el) return;
        el.addEventListener('wheel', handleWheel, { passive: false });
        return () => {
            el.removeEventListener('wheel', handleWheel, { passive: false });
        };
    }, [handleWheel]);

    const handleMouseDown = useCallback((e) => {
        if (zoom <= 1) return;
        setDragging(true);
        lastPos.current = { x: e.clientX, y: e.clientY };
    }, [zoom]);

    const handleMouseMove = useCallback((e) => {
        if (!dragging) return;
        setPan(p => ({
            x: p.x + (e.clientX - lastPos.current.x),
            y: p.y + (e.clientY - lastPos.current.y),
        }));
        lastPos.current = { x: e.clientX, y: e.clientY };
    }, [dragging]);

    const handleMouseUp = useCallback(() => setDragging(false), []);

    useEffect(() => {
        if (dragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
            return () => {
                window.removeEventListener('mousemove', handleMouseMove);
                window.removeEventListener('mouseup', handleMouseUp);
            };
        }
    }, [dragging, handleMouseMove, handleMouseUp]);

    return (
        <div style={{
            flex: 1,
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            background: 'var(--bg-surface)',
            border: emphasis ? '1px solid var(--accent-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
        }}>
            {/* Panel header */}
            <div style={{
                padding: '8px 12px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: emphasis ? 'var(--accent-dim)' : 'transparent',
                flexShrink: 0,
            }}>
                <span style={{
                    fontSize: '0.714rem',
                    fontWeight: 600,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: emphasis ? 'var(--accent)' : 'var(--text-secondary)',
                }}>
                    {label}
                </span>
                <div style={{ display: 'flex', gap: 2 }}>
                    <button
                        className="btn-ghost"
                        style={{ padding: 4, border: 'none' }}
                        onClick={() => setZoom(z => Math.min(8, z * 1.3))}
                        title="Zoom in"
                        aria-label="Zoom in"
                    >
                        <ZoomIn size={13} />
                    </button>
                    <button
                        className="btn-ghost"
                        style={{ padding: 4, border: 'none' }}
                        onClick={() => setZoom(z => Math.max(0.5, z * 0.77))}
                        title="Zoom out"
                        aria-label="Zoom out"
                    >
                        <ZoomOut size={13} />
                    </button>
                    <button
                        className="btn-ghost"
                        style={{ padding: 4, border: 'none' }}
                        onClick={resetView}
                        title="Fit to view"
                        aria-label="Reset view"
                    >
                        <RotateCcw size={13} />
                    </button>
                    {onFullscreen && (
                        <button
                            className="btn-ghost"
                            style={{ padding: 4, border: 'none' }}
                            onClick={onFullscreen}
                            title="Fullscreen"
                            aria-label="Fullscreen"
                        >
                            <Maximize2 size={13} />
                        </button>
                    )}
                </div>
            </div>

            {/* Image area */}
            <div
                ref={containerRef}
                onMouseDown={handleMouseDown}
                style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden',
                    background: 'var(--bg-deep)',
                    cursor: zoom > 1 ? (dragging ? 'grabbing' : 'grab') : 'default',
                    minHeight: 200,
                }}
            >
                {src ? (
                    <img
                        src={src}
                        alt={alt || label}
                        draggable={false}
                        style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain',
                            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                            transition: dragging ? 'none' : 'transform 0.15s ease',
                            userSelect: 'none',
                        }}
                    />
                ) : (
                    <div style={{
                        color: 'var(--text-muted)',
                        fontSize: '0.786rem',
                        textAlign: 'center',
                        padding: 20,
                    }}>
                        No observation loaded
                    </div>
                )}
            </div>

            {/* Zoom indicator */}
            {zoom !== 1 && (
                <div style={{
                    padding: '4px 12px',
                    borderTop: '1px solid var(--border-subtle)',
                    fontSize: '0.643rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    textAlign: 'right',
                }}>
                    {Math.round(zoom * 100)}%
                </div>
            )}
        </div>
    );
}

export default function SatelliteViewer({ panels }) {
    const [fullscreenIdx, setFullscreenIdx] = useState(null);

    // Filter out panels with no src in non-evaluation mode
    const activePanels = panels.filter(p => p.src || p.alwaysShow);

    if (fullscreenIdx !== null && panels[fullscreenIdx]) {
        const p = panels[fullscreenIdx];
        return (
            <div style={{
                position: 'fixed',
                inset: 0,
                zIndex: 1000,
                background: 'var(--bg-deep)',
                display: 'flex',
                flexDirection: 'column',
            }}>
                <div style={{
                    padding: '8px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderBottom: '1px solid var(--border-subtle)',
                }}>
                    <span style={{
                        fontSize: '0.857rem',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                    }}>
                        {p.label}
                    </span>
                    <button
                        className="btn-ghost"
                        onClick={() => setFullscreenIdx(null)}
                        aria-label="Exit fullscreen"
                    >
                        <Minimize2 size={14} />
                        <span>Exit</span>
                    </button>
                </div>
                <div style={{ flex: 1 }}>
                    <ImagePanel
                        label={p.label}
                        src={p.src}
                        alt={p.alt}
                        emphasis={p.emphasis}
                    />
                </div>
            </div>
        );
    }

    return (
        <div style={{
            display: 'flex',
            gap: 6,
            flex: 1,
            minHeight: 0,
        }}>
            {activePanels.map((p, i) => (
                <ImagePanel
                    key={p.key || i}
                    label={p.label}
                    src={p.src}
                    alt={p.alt}
                    emphasis={p.emphasis}
                    onFullscreen={() => {
                        const idx = panels.indexOf(p);
                        setFullscreenIdx(idx);
                    }}
                />
            ))}
        </div>
    );
}
