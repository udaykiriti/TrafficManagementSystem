import React, { useState } from 'react';
import styles from './styles';
import Navigation from './components/layout/Navigation';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import Analytics from './pages/Analytics';
import HowItWorks from './pages/HowItWorks';
import About from './pages/About';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  return (
    <div style={styles.app}>
      {/* Navigation */}
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content */}
      <main style={styles.main}>
        {activeTab === 'home' && (
          <Home
            selectedFiles={selectedFiles}
            setSelectedFiles={setSelectedFiles}
            loading={loading}
            setLoading={setLoading}
            progress={progress}
            setProgress={setProgress}
            result={result}
            setResult={setResult}
          />
        )}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'how it works' && <HowItWorks />}
        {activeTab === 'about' && <About />}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
