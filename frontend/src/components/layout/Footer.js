import React from 'react';
import styles, { m3 } from '../../styles';

function Footer() {
    return (
        <footer style={styles.footer}>
            <div style={styles.navInner}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', flexWrap: 'wrap', gap: '2rem' }}>
                    <div style={{ textAlign: 'left' }}>
                        <div style={styles.logoText}>Traffic<span style={{ color: m3.primary }}>AI</span></div>
                        <div style={{ color: m3.onSurfaceVariant, fontSize: '0.9rem', marginTop: '0.5rem', fontWeight: '500' }}>Next-gen urban infrastructure intelligence</div>
                    </div>

                    <div style={{ color: m3.onSurfaceVariant, fontSize: '0.85rem', fontWeight: '500' }}>
                        © 2026 Traffic Control Systems. Optimized with Material 3 Light.
                    </div>

                    <div style={{ display: 'flex', gap: '2rem', fontSize: '0.95rem', fontWeight: '700' }}>
                        <a href="#github" style={{ color: m3.primary, textDecoration: 'none' }}>Source</a>
                        <a href="#docs" style={{ color: m3.primary, textDecoration: 'none' }}>APIs</a>
                        <a href="#status" style={{ color: m3.primary, textDecoration: 'none' }}>System Status</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
