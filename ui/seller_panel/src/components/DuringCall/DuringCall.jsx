import React, { useState, useEffect } from 'react';
import styles from './DuringCall.module.css';
import DealSelector from './DealSelector';
import DealDetailsPanel from './DealDetailsPanel';
import LiveNotes from './LiveNotes';

/**
 * DuringCall Tab Component
 * Live assistance during sales call with deal reference and note-taking
 */
const DuringCall = () => {
  const [iterations, setIterations] = useState([]);
  const [selectedIteration, setSelectedIteration] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/during_call')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch call iterations');
        return res.json();
      })
      .then((data) => {
        setIterations(data);
        setSelectedIteration(data[0] || null);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className={styles.container}><p>Loading call iterations...</p></div>;
  }
  if (error) {
    return <div className={styles.container}><p>Error: {error}</p></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <h1>📞 During Call: Live Assistance</h1>
        <p>
          Reference deal insights, track objections, and capture call notes in real-time.
        </p>
      </div>

      <div className={styles.mainContent}>
        <div className={styles.leftPanel}>
          {/* List all iterations with selector */}
          <div style={{ marginBottom: 24 }}>
            <label htmlFor="iteration-select">Select Call Iteration:</label>
            <select
              id="iteration-select"
              value={selectedIteration?.id || ''}
              onChange={e => {
                const found = iterations.find(it => it.id === Number(e.target.value));
                setSelectedIteration(found);
              }}
              style={{ marginLeft: 12 }}
            >
              {iterations.map(it => (
                <option key={it.id} value={it.id}>
                  Iteration {it.id}: {it.status}
                </option>
              ))}
            </select>
          </div>
          <DealDetailsPanel deal={selectedIteration} />
        </div>

        <div className={styles.rightPanel}>
          <LiveNotes />
        </div>
      </div>
    </div>
  );
};

export default DuringCall;
