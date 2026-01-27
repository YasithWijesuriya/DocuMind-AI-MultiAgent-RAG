import React from 'react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import documindLogo from './assets/documindLogo.png';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

const link = document.createElement('link');
link.rel = 'icon';
link.type = 'image/png';
link.href = documindLogo;
document.head.appendChild(link);
