import React, { useRef, useCallback, useEffect, useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';

export default function FrameUploader({ label, file, onFileChange }) {
    const inputRef = useRef(null);
    const [preview, setPreview] = useState(null);
    const [dimensions, setDimensions] = useState(null);
    const [dragOver, setDragOver] = useState(false);

    useEffect(() => {
        if (!file) {
            setPreview(null);
            setDimensions(null);
            return;
        }
        const url = URL.createObjectURL(file);
        setPreview(url);
        const img = new window.Image();
        img.onload = () => setDimensions({ w: img.naturalWidth, h: img.naturalHeight });
        img.src = url;
        return () => URL.revokeObjectURL(url);
    }, [file]);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer?.files?.[0];
        if (f && f.type.startsWith('image/')) onFileChange(f);
    }, [onFileChange]);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setDragOver(true);
    }, []);

    return (
        <div style={{ marginBottom: 12 }}>
            <div style={{
                fontSize: '0.714rem',
                fontWeight: 600,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                color: 'var(--text-secondary)',
                marginBottom: 8,
            }}>
                {label}
            </div>

            {!file ? (
                <div
                    role="button"
                    tabIndex={0}
                    onClick={() => inputRef.current?.click()}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={() => setDragOver(false)}
                    onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
                    style={{
                        border: `1px dashed ${dragOver ? 'var(--accent)' : 'var(--border-default)'}`,
                        borderRadius: 'var(--radius-md)',
                        padding: '20px 12px',
                        textAlign: 'center',
                        cursor: 'pointer',
                        background: dragOver ? 'var(--accent-dim)' : 'var(--bg-elevated)',
                        transition: 'all 0.15s ease',
                    }}
                    aria-label={`Upload ${label}`}
                >
                    <Upload size={20} color="var(--text-muted)" style={{ margin: '0 auto 8px' }} />
                    <div style={{ fontSize: '0.786rem', color: 'var(--text-muted)' }}>
                        Drop image or click to browse
                    </div>
                </div>
            ) : (
                <div style={{
                    border: '1px solid var(--accent-border)',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'hidden',
                    background: 'var(--bg-elevated)',
                    position: 'relative',
                }}>
                    <div style={{
                        width: '100%',
                        height: 100,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: 'var(--bg-deep)',
                    }}>
                        <img
                            src={preview}
                            alt={label}
                            style={{
                                maxWidth: '100%',
                                maxHeight: '100%',
                                objectFit: 'contain',
                            }}
                        />
                    </div>
                    <div style={{
                        padding: '8px 10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 8,
                    }}>
                        <div style={{ minWidth: 0, flex: 1 }}>
                            <div style={{
                                fontSize: '0.714rem',
                                color: 'var(--text-primary)',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                            }}>
                                {file.name}
                            </div>
                            {dimensions && (
                                <div style={{
                                    fontSize: '0.643rem',
                                    color: 'var(--text-muted)',
                                    fontFamily: 'var(--font-mono)',
                                    marginTop: 2,
                                }}>
                                    {dimensions.w} × {dimensions.h}
                                </div>
                            )}
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); onFileChange(null); }}
                            style={{
                                padding: 4,
                                borderRadius: 'var(--radius-sm)',
                                color: 'var(--text-muted)',
                                flexShrink: 0,
                            }}
                            aria-label={`Remove ${label}`}
                            title="Remove"
                        >
                            <X size={14} />
                        </button>
                    </div>
                </div>
            )}

            <input
                ref={inputRef}
                type="file"
                accept="image/*"
                onChange={(e) => {
                    if (e.target.files?.[0]) onFileChange(e.target.files[0]);
                    e.target.value = '';
                }}
                style={{ display: 'none' }}
                aria-label={`File input for ${label}`}
            />
        </div>
    );
}
