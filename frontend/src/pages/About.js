import React from 'react';
import styles, { m3 } from '../styles';

function About() {
    const techStack = [
        { icon: '', name: 'Python + Flask', role: 'Orchestration' },
        { icon: '', name: 'YOLOv4-tiny', role: 'Computer Vision' },
        { icon: '', name: 'C++ / OpenMP', role: 'Parallel GA' },
        { icon: '', name: 'RL Agent', role: 'Self-Learning' },
        { icon: '', name: 'React.js', role: 'M3 Interface' }
    ];

    return (
        <div style={styles.aboutPage}>
            <h2 style={{ ...styles.pageTitle, textAlign: 'center', justifyContent: 'center' }}>
                Project Vision
            </h2>

            <div style={{ ...styles.elevatedCard, padding: '4rem', marginTop: '3rem', textAlign: 'center' }}>
                <p style={{ fontSize: '1.25rem', color: m3.onSurface, lineHeight: '1.8', marginBottom: '4rem', maxWidth: '800px', marginInline: 'auto', fontWeight: '400' }}>
                    The <b>Traffic Management AI</b> is an solution designed to eliminate urban congestion.
                    By synthesizing computer vision with hybrid optimization Algorithms, we create a dynamic
                    infrastructure that breathes with the city, reducing idle times and environmental impact.
                </p>

                <h3 style={{ ...styles.statLabel, fontSize: '0.9rem', color: m3.primary, marginBottom: '2.5rem', letterSpacing: '2px' }}>CORE TECHNOLOGY STACK</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1.5rem' }}>
                    {techStack.map((tech, i) => (
                        <div key={i} style={{ background: m3.surfaceVariant + '44', padding: '2rem', borderRadius: '24px', textAlign: 'center', border: `1px solid ${m3.outline}11`, transition: 'transform 0.2s ease' }}>
                            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{tech.icon}</div>
                            <div style={{ fontWeight: '800', color: m3.onSurface, fontSize: '1rem', marginBottom: '6px' }}>{tech.name}</div>
                            <div style={{ color: m3.onSurfaceVariant, fontSize: '0.85rem', fontWeight: '600' }}>{tech.role}</div>
                        </div>
                    ))}
                </div>
            </div>

            <footer style={{ marginTop: '4rem', textAlign: 'center' }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', background: m3.primary + '11', padding: '12px 24px', borderRadius: '100px', fontSize: '0.95rem', color: m3.primary, fontWeight: '700' }}>
                    <span></span> Enterprise-Grade Security & Safety
                </div>
            </footer>
        </div>
    );
}

export default About;