import React, { useState } from 'react';

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

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

    // Simulate progress for better UX
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
      const response = await fetch('http://localhost:5000/upload', {
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

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>
            🚦 AI Based Traffic Management
          </h1>
          <div style={styles.divider}></div>
        </div>

        {/* Main Content */}
        <div style={styles.mainGrid}>
          {/* Left Column */}
          <div style={styles.leftColumn}>
            {/* Hero Section */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <div style={styles.iconBox}>
                  ⚡
                </div>
                <h2 style={styles.cardTitle}>Optimize Traffic Flow with AI</h2>
              </div>
              <p style={styles.cardText}>
                Enhance your city's traffic management with our smart adaptive system. Our technology optimizes traffic light timings based on real-time data to reduce congestion and improve traffic flow.
              </p>
            </div>

            {/* Upload Section */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <div style={styles.iconBox}>
                  📤
                </div>
                <h2 style={styles.cardTitle}>Upload Traffic Videos</h2>
              </div>
              <p style={styles.cardText}>
                Select 4 videos showing different roads at an intersection. Our system will analyze these videos to provide optimized traffic light timings.
              </p>
              
              <div style={styles.uploadSection}>
                <input 
                  type="file" 
                  multiple 
                  accept="video/*" 
                  onChange={handleFileChange}
                  style={styles.fileInput}
                />
                {selectedFiles.length > 0 && (
                  <div style={styles.fileCount}>
                    ✓ {selectedFiles.length} file(s) selected
                  </div>
                )}
                
                <button 
                  onClick={handleSubmit}
                  disabled={loading || selectedFiles.length !== 4}
                  style={{
                    ...styles.button,
                    ...(loading || selectedFiles.length !== 4 ? styles.buttonDisabled : {})
                  }}
                >
                  {loading ? 'Processing...' : 'Run Model'}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div style={styles.resultCard}>
            {!loading && !result && (
              <div style={styles.placeholderContainer}>
                <div style={styles.placeholderIcon}>🚦</div>
                <p style={styles.placeholderText}>
                  Optimization results will appear here
                </p>
                <div style={styles.carIcons}>
                  <span style={styles.carIcon}>🚗</span>
                  <span style={styles.carIcon}>🚙</span>
                  <span style={styles.carIcon}>🚕</span>
                </div>
              </div>
            )}

            {loading && (
              <div style={styles.loaderContainer}>
                <div style={styles.trafficLightBox}>
                  <div style={{
                    ...styles.light,
                    ...(progress < 33 ? styles.lightRed : styles.lightOff)
                  }}></div>
                  <div style={{
                    ...styles.light,
                    ...(progress >= 33 && progress < 66 ? styles.lightYellow : styles.lightOff)
                  }}></div>
                  <div style={{
                    ...styles.light,
                    ...(progress >= 66 ? styles.lightGreen : styles.lightOff)
                  }}></div>
                </div>

                <h3 style={styles.loaderTitle}>
                  Analyzing Traffic Patterns
                </h3>
                
                {/* Progress Bar */}
                <div style={styles.progressBarContainer}>
                  <div style={styles.progressBarBg}>
                    <div 
                      style={{
                        ...styles.progressBarFill,
                        width: `${progress}%`
                      }}
                    ></div>
                  </div>
                  <p style={styles.progressText}>
                    {Math.round(progress)}%
                  </p>
                </div>

                <div style={styles.statusMessages}>
                  <p style={styles.statusMessage}>🎥 Processing video feeds...</p>
                  <p style={styles.statusMessage}>🤖 Running AI analysis...</p>
                  <p style={styles.statusMessage}>⚡ Optimizing timings...</p>
                </div>
              </div>
            )}

            {result && !result.error && (
              <div>
                <div style={styles.resultHeader}>
                  <div style={styles.successIcon}>
                    ✓
                  </div>
                  <h2 style={styles.resultTitle}>Optimization Complete!</h2>
                </div>
                
                <p style={styles.resultDescription}>
                  Your traffic light timings have been optimized. Here are the recommended green times for each direction:
                </p>

                <div style={styles.resultGrid}>
                  {[
                    { direction: 'North', time: result.north, icon: '⬆️', bgColor: '#EFF6FF' },
                    { direction: 'South', time: result.south, icon: '⬇️', bgColor: '#F0FDF4' },
                    { direction: 'West', time: result.west, icon: '⬅️', bgColor: '#FEFCE8' },
                    { direction: 'East', time: result.east, icon: '➡️', bgColor: '#FEF2F2' }
                  ].map((item) => (
                    <div 
                      key={item.direction}
                      style={{
                        ...styles.resultItemCard,
                        backgroundColor: item.bgColor
                      }}
                    >
                      <div style={styles.directionIcon}>{item.icon}</div>
                      <div style={styles.directionName}>{item.direction}</div>
                      <div style={styles.timeValue}>
                        {item.time}<span style={styles.timeUnit}>s</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result && result.error && (
              <div style={styles.errorContainer}>
                <div style={styles.errorIcon}>
                  ⚠️
                </div>
                <h2 style={styles.errorTitle}>Error Occurred</h2>
                <p style={styles.errorText}>{result.error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #EBF4FF 0%, #E0E7FF 100%)',
    padding: '2rem 1rem',
  },
  content: {
    maxWidth: '1400px',
    margin: '0 auto',
  },
  header: {
    textAlign: 'center',
    marginBottom: '3rem',
  },
  title: {
    fontSize: '3rem',
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: '1rem',
  },
  divider: {
    width: '120px',
    height: '4px',
    background: 'linear-gradient(90deg, #3B82F6, #6366F1)',
    margin: '0 auto',
    borderRadius: '2px',
  },
  mainGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '2rem',
    marginTop: '2rem',
  },
  leftColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '2rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    transition: 'transform 0.3s ease',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '1rem',
  },
  iconBox: {
    fontSize: '2rem',
    backgroundColor: '#DBEAFE',
    padding: '0.75rem',
    borderRadius: '12px',
  },
  cardTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1F2937',
    margin: 0,
  },
  cardText: {
    color: '#6B7280',
    lineHeight: '1.6',
    margin: 0,
  },
  uploadSection: {
    marginTop: '1.5rem',
  },
  fileInput: {
    display: 'block',
    width: '100%',
    padding: '0.75rem',
    border: '2px dashed #D1D5DB',
    borderRadius: '8px',
    backgroundColor: '#F9FAFB',
    cursor: 'pointer',
    fontSize: '0.875rem',
  },
  fileCount: {
    marginTop: '0.75rem',
    fontSize: '0.875rem',
    color: '#059669',
  },
  button: {
    width: '100%',
    padding: '1rem 1.5rem',
    marginTop: '1rem',
    fontSize: '1rem',
    fontWeight: '600',
    color: 'white',
    background: 'linear-gradient(90deg, #3B82F6, #6366F1)',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    boxShadow: '0 4px 6px rgba(59, 130, 246, 0.3)',
    transition: 'all 0.3s ease',
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  resultCard: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '2rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    minHeight: '400px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  placeholderContainer: {
    textAlign: 'center',
    padding: '2rem',
  },
  placeholderIcon: {
    fontSize: '4rem',
    marginBottom: '1rem',
    animation: 'bounce 2s infinite',
  },
  placeholderText: {
    fontSize: '1.25rem',
    color: '#9CA3AF',
    fontWeight: '500',
  },
  carIcons: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1.5rem',
    marginTop: '1.5rem',
    fontSize: '2.5rem',
  },
  carIcon: {
    animation: 'pulse 2s infinite',
  },
  loaderContainer: {
    textAlign: 'center',
    padding: '2rem',
  },
  trafficLightBox: {
    width: '120px',
    margin: '0 auto 2rem',
    backgroundColor: '#1F2937',
    borderRadius: '24px',
    padding: '1rem',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)',
  },
  light: {
    width: '100%',
    height: '30px',
    borderRadius: '50%',
    marginBottom: '0.75rem',
    transition: 'all 0.5s ease',
  },
  lightOff: {
    backgroundColor: '#374151',
  },
  lightRed: {
    backgroundColor: '#EF4444',
    boxShadow: '0 0 20px #EF4444',
  },
  lightYellow: {
    backgroundColor: '#FBBF24',
    boxShadow: '0 0 20px #FBBF24',
  },
  lightGreen: {
    backgroundColor: '#10B981',
    boxShadow: '0 0 20px #10B981',
  },
  loaderTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: '1.5rem',
  },
  progressBarContainer: {
    width: '100%',
    maxWidth: '400px',
    margin: '0 auto',
  },
  progressBarBg: {
    width: '100%',
    height: '12px',
    backgroundColor: '#E5E7EB',
    borderRadius: '999px',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #3B82F6, #6366F1)',
    transition: 'width 0.5s ease-out',
    borderRadius: '999px',
  },
  progressText: {
    textAlign: 'center',
    marginTop: '0.5rem',
    color: '#6B7280',
    fontWeight: '600',
  },
  statusMessages: {
    marginTop: '2rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  statusMessage: {
    color: '#6B7280',
    fontSize: '0.875rem',
    animation: 'pulse 2s infinite',
  },
  resultHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '1.5rem',
  },
  successIcon: {
    fontSize: '2rem',
    backgroundColor: '#D1FAE5',
    color: '#059669',
    padding: '0.75rem',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
  },
  resultTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1F2937',
    margin: 0,
  },
  resultDescription: {
    color: '#6B7280',
    marginBottom: '1.5rem',
  },
  resultGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1rem',
  },
  resultItemCard: {
    padding: '1.5rem',
    borderRadius: '12px',
    textAlign: 'center',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
    transition: 'transform 0.3s ease',
  },
  directionIcon: {
    fontSize: '2rem',
    marginBottom: '0.5rem',
  },
  directionName: {
    color: '#6B7280',
    fontWeight: '600',
    marginBottom: '0.5rem',
  },
  timeValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#1F2937',
  },
  timeUnit: {
    fontSize: '1rem',
    color: '#6B7280',
  },
  errorContainer: {
    textAlign: 'center',
    padding: '2rem',
  },
  errorIcon: {
    fontSize: '3rem',
    backgroundColor: '#FEE2E2',
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 1rem',
  },
  errorTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: '0.5rem',
  },
  errorText: {
    color: '#6B7280',
  },
};

export default App;