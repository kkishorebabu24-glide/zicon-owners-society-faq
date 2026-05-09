import React, { useEffect, useState } from 'react';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [healthData, setHealthData] = useState(null);
  const [rootData, setRootData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refreshStatus = async () => {
    setLoading(true);
    setError(null);
    setBackendStatus('checking');

    try {
      const healthResponse = await fetch(`${apiUrl}/health`);
      if (!healthResponse.ok) {
        throw new Error(`Health endpoint returned ${healthResponse.status}`);
      }
      const healthJson = await healthResponse.json();
      setHealthData(healthJson);
      setBackendStatus('online');

      const rootResponse = await fetch(`${apiUrl}/`);
      const rootJson = rootResponse.ok ? await rootResponse.json() : null;
      setRootData(rootJson);
    } catch (err) {
      setBackendStatus('offline');
      setError(err.message || 'Unable to reach backend');
      setHealthData(null);
      setRootData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Society Owners Society</p>
          <h1>Resident community management made visible</h1>
          <p className="hero-copy">
            This frontend is now wired to the backend and can check service health, API status,
            and display the live backend response.
          </p>
        </div>
        <div className="hero-actions">
          <button className="primary-button" onClick={refreshStatus} disabled={loading}>
            {loading ? 'Refreshing…' : 'Refresh backend status'}
          </button>
          <a className="secondary-button" href={`${apiUrl}/docs`} target="_blank" rel="noreferrer">
            Open API docs
          </a>
        </div>
      </header>

      <section className="status-grid">
        <article className="status-card">
          <p className="status-title">Backend URL</p>
          <p className="status-value">{apiUrl}</p>
        </article>

        <article className="status-card">
          <p className="status-title">Backend status</p>
          <p className={`status-value status-${backendStatus}`}>
            {backendStatus}
          </p>
        </article>

        <article className="status-card">
          <p className="status-title">Last health check</p>
          <pre className="status-snippet">
            {healthData ? JSON.stringify(healthData, null, 2) : 'No health data yet'}
          </pre>
        </article>
      </section>

      {error ? <div className="alert">{error}</div> : null}

      {rootData ? (
        <section className="detail-card">
          <h2>Backend root response</h2>
          <pre>{JSON.stringify(rootData, null, 2)}</pre>
        </section>
      ) : null}

      <section className="feature-panel">
        <h2>Next frontend work</h2>
        <ul>
          <li>Build pages for auth, digests, marketplace, and Telegram integration</li>
          <li>Connect the UI to backend route data once APIs are implemented</li>
          <li>Add a login flow, user dashboard, and society notifications</li>
          <li>Enable real-time updates for requests, offers, and digest delivery</li>
        </ul>
      </section>
    </div>
  );
}

export default App;
