import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Get backend URL - support both local dev and production (Render.com)
const BACKEND_URL = process.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Middleware
app.use(express.json());

// Simple proxy for API calls to backend (avoid CORS during local dev)
app.use('/api', async (req, res) => {
  try {
    const target = BACKEND_URL + req.originalUrl;

    const fetchOptions = {
      method: req.method,
      headers: { ...req.headers },
      // Do not forward host header
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      fetchOptions.body = JSON.stringify(req.body);
      fetchOptions.headers['content-type'] = req.get('content-type') || 'application/json';
    }

    const backendRes = await fetch(target, fetchOptions);
    const body = await backendRes.text();

    // Copy status and headers (some headers excluded)
    res.status(backendRes.status);
    backendRes.headers.forEach((value, name) => {
      if (name.toLowerCase() === 'transfer-encoding') return;
      res.setHeader(name, value);
    });
    res.send(body);
  } catch (err) {
    console.error('API proxy error', err);
    res.status(502).json({ error: 'Bad gateway', details: String(err) });
  }
});

app.use(express.static(path.join(__dirname, 'dist')));

// Serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`
  ========================================
  DealSense AI - Sales Intelligence UI
  ========================================
  Server running at http://localhost:${PORT}
  ========================================
  `);
});
