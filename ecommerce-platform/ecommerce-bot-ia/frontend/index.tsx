
import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './i18n';

// Force Spanish language on app load
localStorage.removeItem('i18nextLng');
localStorage.setItem('i18nextLng', 'es');

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);

// Render immediately with fallback
root.render(
  <React.StrictMode>
    <Suspense fallback={
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh', 
        fontSize: '18px' 
      }}>
        Loading...
      </div>
    }>
      <App />
    </Suspense>
  </React.StrictMode>
);