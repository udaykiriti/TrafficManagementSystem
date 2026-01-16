import React from 'react';
import styles, { m3 } from '../styles';

function HowItWorks() {
    const steps = [
        { num: '01', title: 'Stream Acquisition', desc: 'Securely ingest synchronous video feeds from 4 intersection quadrants.', icon: '' },
        { num: '02', title: 'Neural Processing', desc: 'Real-time vehicle detection using high-speed YOLOv4-tiny clusters.', icon: '' },
        { num: '03', title: 'Evolutionary GA', desc: 'Genetic Algorithms simulate timing scenarios to find the global optimum.', icon: '' },
        { num: '04', title: 'Priority Logic', desc: 'A Deep RL Agent applies overrides for heavy congestion or emergency flux.', icon: '' },
        { num: '05', title: 'Control Sync', desc: 'Deploy optimized green-time sequences to intersection controllers.', icon: '' }
    ];

    return (
        <div style={styles.howPage}>
            <h2 style={{ ...styles.pageTitle, textAlign: 'center', justifyContent: 'center' }}>
                System Architecture
            </h2>

            <div style={{ maxWidth: '850px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '3rem' }}>
                {steps.map((step, i) => (
                    <div key={i} style={{ ...styles.stepCard, border: `1px solid ${m3.outline}11`, boxShadow: '0 2px 10px rgba(0,0,0,0.03)' }}>
                        <div style={{ width: '56px', height: '56px', background: m3.primary, color: m3.onPrimary, borderRadius: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '800', fontSize: '1.25rem', flexShrink: 0, boxShadow: '0 4px 12px rgba(103, 80, 164, 0.2)' }}>
                            {step.num}
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                                <span style={{ fontSize: '1.75rem' }}>{step.icon}</span>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: m3.onSurface, margin: 0 }}>{step.title}</h3>
                            </div>
                            <p style={{ color: m3.onSurfaceVariant, fontSize: '1rem', lineHeight: '1.7', margin: 0, fontWeight: '400' }}>{step.desc}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default HowItWorks;
