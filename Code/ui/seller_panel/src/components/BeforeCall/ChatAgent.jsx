import React, { useState } from 'react';
import styles from './BeforeCall.module.css';

const ChatAgent = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setResults([]);
    try {
      const qParam = encodeURIComponent(query.trim());
      // Use relative API path so server-side proxy (server.js) forwards to backend
      const url = `/api/search?q=${qParam}&limit=10`;
      console.log('ChatAgent requesting', url);
      const res = await fetch(url, { credentials: 'same-origin' });

      const contentType = res.headers.get('content-type') || '';
      if (!res.ok) {
        const text = await res.text();
        const short = text && text.length > 200 ? text.slice(0, 200) + '...' : text;
        console.error('ChatAgent fetch failed', res.status, short);
        throw new Error(short || res.statusText || 'Network response was not ok');
      }

      if (!contentType.includes('application/json')) {
        const text = await res.text();
        console.error('ChatAgent expected JSON but got:', contentType, text && text.slice(0, 200));
        throw new Error('Expected JSON response but received HTML or plain text from ' + url + ': ' + (text ? text.slice(0, 200) : ''));
      }

      const data = await res.json();
      console.log('ChatAgent received', Array.isArray(data) ? data.length + ' items' : typeof data);
      setResults(data || []);
      setShowModal(true);
    } catch (err) {
      setError(err.message || 'Error fetching results');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className={styles.chatAgent}>
      <form onSubmit={handleSubmit} className={styles.chatForm}>
        <input
          aria-label="Ask the agent"
          className={styles.chatInput}
          placeholder="Ask about a deal or enter keywords (e.g. 'banking', 'claims')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className={styles.chatButton} disabled={loading}>
          {loading ? 'Searching…' : 'Ask'}
        </button>
        <button type="button" className={styles.printButton} disabled={loading || results.length === 0} onClick={() => setShowModal(true)}>
          View Results
        </button>
      </form>

      <div className={styles.chatResults}>
        {error && <div className={styles.error}>Error: {error}</div>}

        {results.length === 0 && !loading && <div className={styles.hint}>No results yet. Try a keyword and press Ask.</div>}

        {results.map((d) => (
          <div key={d.id} className={styles.dealCard}>
            <h3>{d.title}</h3>
            <p><strong>Summary:</strong> {d.summary}</p>
            <p><strong>Solution Area:</strong> {d.solutionArea} — <strong>Industry:</strong> {d.industry}</p>
            <p><strong>Deal Value:</strong> {d.dealValue} — <strong>Duration:</strong> {d.duration}</p>
            <details>
              <summary>Case study & highlights</summary>
              <p>{d.caseStudy}</p>
              <p><strong>Highlights:</strong></p>
              <ul>
                {d.keyHighlights && d.keyHighlights.map((h, i) => <li key={i}>{h}</li>)}
              </ul>
              <p><strong>Deal Breakers:</strong></p>
              <ul>
                {d.dealBreakers && d.dealBreakers.map((b, i) => <li key={i}>{b}</li>)}
              </ul>
            </details>
          </div>
        ))}
      </div>
      </div>

      {showModal && <ResultsModal results={results} onClose={() => setShowModal(false)} />}
    </>
  );
};

// Modal rendering is placed below to keep component logic tidy
function ResultsModal({ results, onClose }) {
  if (!results || results.length === 0) return null;
  const printableHtml = () => {
    return `
      <html>
        <head>
          <title>DealSense - Search Results</title>
          <style>body{font-family:Arial,Helvetica,sans-serif;padding:20px} h1{font-size:18px} .deal{margin-bottom:18px;border-bottom:1px solid #ddd;padding-bottom:12px}</style>
        </head>
        <body>
          <h1>Search Results</h1>
          ${results.map(d => `
            <div class="deal">
              <h2>${escapeHtml(d.title)}</h2>
              <p><strong>Summary:</strong> ${escapeHtml(d.summary)}</p>
              <p><strong>Solution Area:</strong> ${escapeHtml(d.solutionArea)} — <strong>Industry:</strong> ${escapeHtml(d.industry)}</p>
              <p><strong>Deal Value:</strong> ${escapeHtml(d.dealValue)} — <strong>Duration:</strong> ${escapeHtml(d.duration)}</p>
            </div>
          `).join('')}
        </body>
      </html>
    `;
  };

  const handlePrint = () => {
    const w = window.open('', '_blank');
    w.document.open();
    w.document.write(printableHtml());
    w.document.close();
    w.focus();
    setTimeout(() => w.print(), 300);
  };

  return (
    <div className={styles.modalOverlay} role="dialog" aria-modal="true">
      <div className={styles.modalContent}>
        <div className={styles.modalHeader}>
          <h2>Search Results</h2>
          <button onClick={onClose} className={styles.modalClose}>×</button>
        </div>
        <div className={styles.modalBody}>
          {results.map((d) => (
            <div key={d.id} className={styles.dealCard}>
              <h3>{d.title}</h3>
              <p><strong>Summary:</strong> {d.summary}</p>
              <p><strong>Deal Value:</strong> {d.dealValue} — <strong>Duration:</strong> {d.duration}</p>
            </div>
          ))}
        </div>
        <div className={styles.modalFooter}>
          <button onClick={handlePrint} className={styles.printButton}>Print</button>
          <button onClick={onClose} className={styles.chatButton}>Close</button>
        </div>
      </div>
    </div>
  );
}

// basic escaping for string interpolation into HTML
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export default ChatAgent;
