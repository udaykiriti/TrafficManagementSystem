import React, { useState, useEffect } from 'react';
import styles, { m3 } from '../styles';
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

import {
  RefreshCcw,
  Timer,
  Car,
  CheckCircle,
  BarChart3,
  Zap
} from "lucide-react";

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div style={{
                background: '#FFFFFF',
                padding: '12px 16px',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                border: `1px solid ${m3.outline}22`
            }}>
                <p style={{ margin: 0, fontWeight: '600', color: m3.onSurface }}>{`Run #${label}`}</p>
                <p style={{ margin: '4px 0 0', color: m3.primary, fontWeight: '700' }}>
                    {payload[0].value.toFixed(1)}
                </p>
            </div>
        );
    }
    return null;
};

function Analytics() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        setLoading(true);
        setError(null);
        try {
            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
            const response = await fetch(`${apiUrl}/stats`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setStats(data);
        } catch (err) {
            console.error('Failed to fetch stats:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Prepare display stats from backend data
    const getDisplayStats = () => {
        const results = stats?.results || {};
        const analytics = stats?.analytics || {};
        return [
        { icon: RefreshCcw, value: results.total_runs || 0, label: 'Total Runs' },
        { icon: Timer, value: results.avg_delay?.toFixed(1) || '0', label: 'Avg Delay' },
        { icon: Car, value: analytics.total_cars_processed || 0, label: 'Vehicles' },
        { icon: CheckCircle, value: `${analytics.success_rate || 100}%`, label: 'Success' },
        { icon: BarChart3, value: analytics.total_optimizations || 0, label: 'Optimizations' },
        { icon: Zap, value: `${results.avg_elapsed?.toFixed(1) || '0'}s`, label: 'Avg Time' }
        ];
    };

    // Chart data from recent records
    const recent = stats?.recent || [];

    // Format data for recharts
    const chartData = recent.map((d, i) => ({
        name: i + 1,
        delay: d.delay || 0,
        vehicles: d.total_cars || 0
    }));

    // Lane distribution data for pie chart
    const getLaneDistribution = () => {
        const colors = [m3.primary, '#9575CD', m3.tertiary, '#78909C'];

        if (!recent.length) {
            return [
                { name: 'North', value: 25, color: colors[0] },
                { name: 'South', value: 25, color: colors[1] },
                { name: 'West', value: 25, color: colors[2] },
                { name: 'East', value: 25, color: colors[3] }
            ];
        }

        const last = recent[recent.length - 1].cars || [0, 0, 0, 0];
        return [
            { name: 'North', value: last[0] || 1, color: colors[0] },
            { name: 'South', value: last[1] || 1, color: colors[1] },
            { name: 'West', value: last[2] || 1, color: colors[2] },
            { name: 'East', value: last[3] || 1, color: colors[3] }
        ];
    };

    const pieData = getLaneDistribution();

    return (
        <div style={styles.analyticsPage}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <h2 style={{ ...styles.pageTitle, marginBottom: 0 }}>
                    <span style={{ background: m3.primary + '15', padding: '12px', borderRadius: '16px' }}>.|.</span>
                    Network Analytics
                </h2>
                <button
                    onClick={fetchStats}
                    style={{ ...styles.secondaryBtn, padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
                >
                    .. Refresh ..
                </button>
            </header>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '5rem' }}>
                    <div style={{ ...styles.loaderSpinner, margin: '0 auto' }}></div>
                    <p style={{ color: m3.onSurfaceVariant, marginTop: '1.5rem', fontWeight: '500' }}>Loading analytics data...</p>
                </div>
            ) : error ? (
                <div style={{ textAlign: 'center', padding: '4rem', background: m3.error + '08', borderRadius: '24px', border: `1px solid ${m3.error}22` }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>Ohhh!</div>
                    <h3 style={{ color: m3.error, marginBottom: '0.5rem' }}>Failed to Load Data</h3>
                    <p style={{ color: m3.onSurfaceVariant }}>{error}</p>
                    <p style={{ color: m3.onSurfaceVariant, fontSize: '0.9rem', marginTop: '1rem' }}>
                        Make sure the backend server is running on <code>localhost:5000</code>
                    </p>
                    <button onClick={fetchStats} style={{ ...styles.primaryBtn, marginTop: '1.5rem' }}>
                        Try Again
                    </button>
                </div>
            ) : (
                <>
                    {/* Stats Grid */}
                    <div style={styles.statsGrid}>
                        {getDisplayStats().map((stat, i) => {
                            const IconComponent = stat.icon;
                            return (
                                <div key={i} style={{ ...styles.statCard, background: '#FFFFFF', boxShadow: '0 2px 8px rgba(0,0,0,0.06)', border: `1px solid ${m3.outline}11` }}>
                                    <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}><IconComponent size={24} color={m3.primary} /></div>
                                    <div style={styles.statValue}>{stat.value}</div>
                                    <div style={styles.statLabel}>{stat.label}</div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Charts Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>

                        {/* Delay Area Chart */}
                        <div style={styles.elevatedCard}>
                            <h4 style={{ color: m3.onSurfaceVariant, fontSize: '0.85rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '1.5rem' }}>
                                Delay Trend
                            </h4>
                            {chartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height={200}>
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="delayGradient" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor={m3.error} stopOpacity={0.3} />
                                                <stop offset="95%" stopColor={m3.error} stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke={m3.outline + '22'} />
                                        <XAxis dataKey="name" stroke={m3.onSurfaceVariant} fontSize={12} />
                                        <YAxis stroke={m3.onSurfaceVariant} fontSize={12} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Area type="monotone" dataKey="delay" stroke={m3.error} fillOpacity={1} fill="url(#delayGradient)" strokeWidth={3} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div style={{ textAlign: 'center', padding: '3rem', color: m3.onSurfaceVariant }}>
                                    No data yet. Process some videos first!
                                </div>
                            )}
                        </div>

                        {/* Vehicle Volume Bar Chart */}
                        <div style={styles.elevatedCard}>
                            <h4 style={{ color: m3.onSurfaceVariant, fontSize: '0.85rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '1.5rem' }}>
                                Vehicle Volume
                            </h4>
                            {chartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height={200}>
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke={m3.outline + '22'} />
                                        <XAxis dataKey="name" stroke={m3.onSurfaceVariant} fontSize={12} />
                                        <YAxis stroke={m3.onSurfaceVariant} fontSize={12} />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Bar dataKey="vehicles" fill={m3.primary} radius={[6, 6, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div style={{ textAlign: 'center', padding: '3rem', color: m3.onSurfaceVariant }}>
                                    No data yet. Process some videos first!
                                </div>
                            )}
                        </div>

                        {/* Lane Distribution Pie Chart */}
                        <div style={styles.elevatedCard}>
                            <h4 style={{ color: m3.onSurfaceVariant, fontSize: '0.85rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '1.5rem' }}>
                                Lane Distribution
                            </h4>
                            <ResponsiveContainer width="100%" height={220}>
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={50}
                                        outerRadius={80}
                                        paddingAngle={3}
                                        dataKey="value"
                                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                        labelLine={false}
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>

                        {/* AI Performance Card */}
                        <div style={{ ...styles.elevatedCard, background: m3.primary, color: m3.onPrimary }}>
                            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}></div>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.75rem' }}>AI Performance</h3>
                            <p style={{ fontSize: '0.95rem', opacity: 0.9, lineHeight: '1.6' }}>
                                The system has processed <b>{stats?.analytics?.total_cars_processed || 0}</b> vehicles
                                across <b>{stats?.results?.total_runs || 0}</b> optimization cycles with
                                a <b>{stats?.analytics?.success_rate || 100}%</b> success rate.
                            </p>
                            <div style={{ marginTop: '1.5rem', background: 'rgba(255,255,255,0.15)', padding: '1rem', borderRadius: '12px', fontSize: '0.9rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <span>Avg Processing Time</span>
                                    <b>{stats?.results?.avg_elapsed?.toFixed(2) || 0}s</b>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span>Avg Delay Reduction</span>
                                    <b>{stats?.results?.avg_delay?.toFixed(1) || 0}</b>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

            <footer style={{ marginTop: '4rem', textAlign: 'center', color: m3.onSurfaceVariant, fontSize: '0.85rem', opacity: 0.7 }}>
                Data sourced from backend CSV logs • Charts powered by Recharts
            </footer>
        </div>
    );
}

export default Analytics;
