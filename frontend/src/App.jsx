import React from 'react';

function App() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontFamily: 'Arial, sans-serif',
      background: '#f5f7fb',
      color: '#1f2937',
    }}>
      <div style={{
        maxWidth: 640,
        width: '100%',
        padding: '2rem',
        borderRadius: '1rem',
        boxShadow: '0 20px 50px rgba(0,0,0,0.08)',
        background: '#ffffff',
      }}>
        <h1>Society App</h1>
        <p>The frontend build is now working. Replace this placeholder with the real UI.</p>
      </div>
    </div>
  );
}

export default App;
