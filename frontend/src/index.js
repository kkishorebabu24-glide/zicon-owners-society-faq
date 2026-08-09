import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import store from './store';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Provider>
  </React.StrictMode>
);

// Development-time workaround: unregister any service workers that may
// be interfering with UI interaction, and re-enable pointer events.
// This is safe for debugging — remove in production after root cause found.
if (typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations()
    .then((regs) => regs.forEach((r) => r.unregister().catch(() => {})))
    .catch(() => {});
}

window.addEventListener('load', () => {
  try {
    // ensure the main root and body accept pointer events
    const rootEl = document.getElementById('root');
    if (rootEl && rootEl.style) rootEl.style.pointerEvents = 'auto';
    if (document.body && document.body.style) document.body.style.pointerEvents = 'auto';

    // remove disabled attribute from interactive controls for quick testing
    document.querySelectorAll('[disabled]').forEach((el) => el.removeAttribute('disabled'));
  } catch (e) {
    // swallow errors — this is a temporary debug aid
    // eslint-disable-next-line no-console
    console.warn('UI debug helpers failed', e);
  }
});
