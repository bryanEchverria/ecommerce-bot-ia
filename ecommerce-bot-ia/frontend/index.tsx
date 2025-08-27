
import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './i18n';
import i18n from './i18n';

// Force Spanish language on app load
localStorage.removeItem('i18nextLng');
localStorage.setItem('i18nextLng', 'es');

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);

// Wait for i18n to be ready before rendering
const renderApp = () => {
  if (i18n.isInitialized) {
    i18n.changeLanguage('es');
    root.render(
      <React.StrictMode>
        <Suspense fallback="Loading...">
          <App />
        </Suspense>
      </React.StrictMode>
    );
  } else {
    setTimeout(renderApp, 50);
  }
};

// Start rendering process
renderApp();