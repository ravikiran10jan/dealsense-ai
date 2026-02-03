import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

/**
 * React Application Entry Point
 * Initializes the root DOM element and renders the App component
 */
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
