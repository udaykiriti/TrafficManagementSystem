import React from 'react';
import styles, { m3 } from '../styles';
import { getApiBase } from '../api/client';

function Home({ selectedFiles, setSelectedFiles, loading, setLoading, progress, setProgress, result, setResult }) {

    const handleFileChange = (e) => {
        setSelectedFiles(Array.from(e.target.files));
    };

    const handleSubmit = async () => {
        if (selectedFiles.length !== 4) {
            alert('Please upload exactly 4 videos.');
            return;
        }

        setLoading(true);
        setProgress(0);
        setResult(null);

        const progressInterval = setInterval(() => {
            setProgress(prev => {
                if (prev >= 90) {
                    clearInterval(progressInterval);
                    return 90;
                }
                return prev + Math.random() * 15;
            });
        }, 800);

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('videos', file));

        try {
            const apiUrl = getApiBase();
            const response = await fetch(`${apiUrl}/upload`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();

            clearInterval(progressInterval);
            setProgress(100);

            setTimeout(() => {
                setResult(data);
                setLoading(false);
            }, 500);
        } catch (error) {
            console.error('Error uploading files:', error);
            clearInterval(progressInterval);
            setLoading(false);
            setResult({ error: 'Failed to process videos. Please try again.' });
        }
    };

    const features = [
        { icon: '', title: 'Real-Time Vision', desc: 'SOTA YOLOv4 deep learning for precision vehicle detection' },
        { icon: '', title: 'Genetic Evolution', desc: 'Evolutionary optimization for optimal signal timings' },
        { icon: '', title: 'RL Intelligence', desc: 'Context-aware priority agents for dynamic flow' },
        { icon: '', title: 'C++ Compute', desc: 'High-performance parallel computation backend' }
    ];

    return (
        <>
            {/* Hero Section */}
            <div style={styles.hero}>
                <h1 style={styles.heroTitle}>
                    Intelligent Traffic
                    <span style={styles.heroAccent}> Management</span>
                </h1>
                <p style={styles.heroSubtitle}>
                    Eliminate urban gridlock with a next-generation control system powered by Vision AI and Reinforcement Learning.
                </p>
            </div>

            {/* Main Grid */}
            <div style={styles.homeGrid}>
                {/* Upload Card */}
                <div style={styles.elevatedCard}>
                    <h2 style={{ ...styles.logoText, fontSize: '1.75rem', marginBottom: '0.75rem' }}>Upload Junction Data</h2>
                    <p style={{ color: m3.onSurfaceVariant, fontSize: '1rem', marginBottom: '2rem' }}>
                        Connect 4 synchronous video feeds for real-time intersection optimization.
                    </p>

                    <div
                        style={styles.uploadZone}
                        onClick={() => document.getElementById('fileInput').click()}
                    >
                        <input
                            type="file"
                            multiple
                            accept="video/*"
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                            id="fileInput"
                        />
                        <span style={{ fontSize: '3rem', display: 'block', marginBottom: '1.5rem' }}></span>
                        <span style={{ color: m3.primary, fontWeight: '700', fontSize: '1.1rem' }}>Select 4 Video Streams</span>
                    </div>

                    {selectedFiles.length > 0 && (
                        <div style={{ marginTop: '2rem', background: m3.surfaceVariant, padding: '1.5rem', borderRadius: '20px', border: `1px solid ${m3.outline}22` }}>
                            {selectedFiles.map((file, i) => (
                                <div key={i} style={{ fontSize: '0.9rem', color: m3.onSurface, padding: '8px 0', borderBottom: i < 3 ? `1px solid ${m3.outline}22` : 'none', fontWeight: '500' }}>
                                    🎬 {file.name.substring(0, 40)}
                                </div>
                            ))}
                        </div>
                    )}

                    <button
                        onClick={handleSubmit}
                        disabled={loading || selectedFiles.length !== 4}
                        style={{
                            ...styles.primaryBtn,
                            marginTop: '2.5rem',
                            width: '100%',
                            opacity: loading || selectedFiles.length !== 4 ? 0.4 : 1
                        }}
                    >
                        {loading ? 'Processing...' : 'Analyze Network'}
                    </button>
                </div>

                {/* Results Card */}
                <div style={styles.elevatedCard}>
                    {!loading && !result && (
                        <div style={{ textAlign: 'center', padding: '4rem 0', opacity: 0.3 }}>
                            <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}></div>
                            <p style={{ color: m3.onSurfaceVariant, fontSize: '1.1rem', fontWeight: '500' }}>Waiting for junction data...</p>
                        </div>
                    )}

                    {loading && (
                        <div style={{ textAlign: 'center', padding: '3rem 0' }}>
                            <div style={{ ...styles.loaderSpinner, margin: '0 auto' }}></div>
                            <h3 style={{ color: m3.onSurface, marginTop: '2.5rem', fontSize: '1.25rem', fontWeight: '700' }}>Calculating Optimal Flow</h3>
                            <div style={{ background: m3.surfaceVariant, height: '8px', borderRadius: '4px', marginTop: '2rem', overflow: 'hidden' }}>
                                <div style={{ background: m3.primary, height: '100%', width: `${progress}%`, transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)' }}></div>
                            </div>
                            <p style={{ color: m3.onSurfaceVariant, fontSize: '0.95rem', marginTop: '1rem', fontWeight: '600' }}>{Math.round(progress)}% Optimized</p>
                        </div>
                    )}

                    {result && !result.error && (
                        <div>
                            <div style={{ display: 'inline-block', background: '#E8F5E9', color: '#2E7D32', padding: '6px 16px', borderRadius: '100px', fontSize: '0.8rem', fontWeight: '800', marginBottom: '2rem', letterSpacing: '1px' }}>
                                 SYSTEM OPTIMAL
                            </div>

                            {result.rl_recommendation && (
                                <div style={{ background: m3.primary + '0A', borderRadius: '24px', padding: '2rem', border: `1px solid ${m3.primary}22`, marginBottom: '2rem' }}>
                                    <div style={{ color: m3.primary, fontSize: '0.85rem', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1.5px' }}>AI Recommended Action</div>
                                    <div style={{ fontSize: '1.75rem', fontWeight: '800', margin: '12px 0', color: m3.onSurface }}>{result.rl_recommendation.direction}</div>
                                    <div style={{ fontSize: '4rem', fontWeight: '800', color: m3.primary, lineHeight: '1' }}>{result.rl_recommendation.timer}<span style={{ fontSize: '1.5rem', fontWeight: '500', color: m3.onSurfaceVariant }}>s</span></div>
                                    <div style={{ color: m3.onSurfaceVariant, fontSize: '0.95rem', marginTop: '12px', lineHeight: '1.5' }}>{result.rl_recommendation.reason}</div>
                                </div>
                            )}

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                                {[
                                    { dir: 'North', icon: '⬆', time: result.result?.north || result.north },
                                    { dir: 'South', icon: '⬇', time: result.result?.south || result.south },
                                    { dir: 'West', icon: '<-', time: result.result?.west || result.west },
                                    { dir: 'East', icon: '->', time: result.result?.east || result.east }
                                ].map(item => (
                                    <div key={item.dir} style={{ background: m3.surfaceVariant, padding: '1.5rem', borderRadius: '20px', textAlign: 'center', border: `1px solid ${m3.outline}11` }}>
                                        <div style={{ fontSize: '0.9rem', color: m3.onSurfaceVariant, fontWeight: '600' }}>{item.icon} {item.dir}</div>
                                        <div style={{ fontSize: '1.75rem', fontWeight: '800', marginTop: '8px', color: m3.onSurface }}>{item.time}s</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {result && result.error && (
                        <div style={{ textAlign: 'center', padding: '3rem', border: `2px solid ${m3.error}22`, borderRadius: '24px', color: m3.error, background: m3.error + '05' }}>
                            <span style={{ fontSize: '3rem' }}>⚠️</span>
                            <p style={{ marginTop: '1.5rem', fontWeight: '700', fontSize: '1.1rem' }}>{result.error}</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Features Section */}
            <div style={{ marginTop: '6rem' }}>
                <h2 style={{ ...styles.pageTitle, textAlign: 'center', justifyContent: 'center' }}> Platform Capabilities</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '2rem' }}>
                    {features.map((f, i) => (
                        <div key={i} style={{ ...styles.card, padding: '2.5rem', textAlign: 'center', background: '#FFFFFF', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1.5rem' }}>{f.icon}</div>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1rem', color: m3.primary }}>{f.title}</h3>
                            <p style={{ fontSize: '1rem', color: m3.onSurfaceVariant, lineHeight: '1.6' }}>{f.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </>
    );
}

export default Home;
