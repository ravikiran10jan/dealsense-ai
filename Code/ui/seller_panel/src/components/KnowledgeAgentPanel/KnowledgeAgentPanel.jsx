import React, { useState, useEffect, useCallback } from 'react';
import styles from './KnowledgeAgentPanel.module.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

const KnowledgeAgentPanel = ({ isOpen, onClose }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [manualContent, setManualContent] = useState('');
  const [documentName, setDocumentName] = useState('');
  const [documentType, setDocumentType] = useState('text');
  const [feedbackStats, setFeedbackStats] = useState(null);

  // Fetch agent status
  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/knowledge-agent/status`, {
        headers: { 'X-API-Key': API_KEY },
      });
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch agent status:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch feedback stats
  const fetchFeedbackStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback/stats`, {
        headers: { 'X-API-Key': API_KEY },
      });
      if (response.ok) {
        const data = await response.json();
        setFeedbackStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch feedback stats:', error);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
      fetchFeedbackStats();
      // Poll for status updates every 5 seconds
      const interval = setInterval(fetchStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen, fetchStatus, fetchFeedbackStats]);

  // Start agent
  const handleStart = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/knowledge-agent/start`, {
        method: 'POST',
        headers: { 'X-API-Key': API_KEY },
      });
      fetchStatus();
    } catch (error) {
      console.error('Failed to start agent:', error);
    }
  };

  // Stop agent
  const handleStop = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/knowledge-agent/stop`, {
        method: 'POST',
        headers: { 'X-API-Key': API_KEY },
      });
      fetchStatus();
    } catch (error) {
      console.error('Failed to stop agent:', error);
    }
  };

  // Manual ingest
  const handleIngest = async () => {
    if (!manualContent.trim() || !documentName.trim()) return;
    
    setIngesting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/knowledge-agent/ingest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
        },
        body: JSON.stringify({
          content: manualContent,
          document_name: documentName,
          document_type: documentType,
        }),
      });
      
      if (response.ok) {
        setManualContent('');
        setDocumentName('');
        fetchStatus();
      }
    } catch (error) {
      console.error('Failed to ingest document:', error);
    } finally {
      setIngesting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.panel} onClick={(e) => e.stopPropagation()}>
        <header className={styles.header}>
          <div className={styles.headerTitle}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
            <h2>Knowledge Agent</h2>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </header>

        <div className={styles.content}>
          {/* Agent Status Section */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Agent Status</h3>
            {loading ? (
              <div className={styles.loading}>Loading...</div>
            ) : (
              <div className={styles.statusCard}>
                <div className={styles.statusHeader}>
                  <div className={`${styles.statusIndicator} ${status?.is_running ? styles.running : styles.stopped}`}>
                    <span className={styles.statusDot}></span>
                    <span>{status?.is_running ? 'Running' : 'Stopped'}</span>
                  </div>
                  <div className={styles.statusActions}>
                    {status?.is_running ? (
                      <button className={styles.stopBtn} onClick={handleStop}>Stop Agent</button>
                    ) : (
                      <button className={styles.startBtn} onClick={handleStart}>Start Agent</button>
                    )}
                  </div>
                </div>
                
                <div className={styles.statusStats}>
                  <div className={styles.statItem}>
                    <span className={styles.statValue}>{status?.documents_processed || 0}</span>
                    <span className={styles.statLabel}>Documents Processed</span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statValue}>{status?.total_chunks || 0}</span>
                    <span className={styles.statLabel}>Total Chunks</span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statValue}>{status?.sources_configured?.length || 0}</span>
                    <span className={styles.statLabel}>Sources</span>
                  </div>
                </div>

                {status?.last_scan && (
                  <div className={styles.lastScan}>
                    Last scan: {new Date(status.last_scan).toLocaleString()}
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Configured Sources */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Knowledge Sources</h3>
            <div className={styles.sourcesList}>
              {status?.sources_configured?.map((source) => (
                <div key={source.id} className={styles.sourceItem}>
                  <div className={styles.sourceIcon}>
                    {source.type === 'sharepoint' ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    )}
                  </div>
                  <div className={styles.sourceInfo}>
                    <span className={styles.sourceName}>{source.name}</span>
                    <span className={styles.sourcePath}>{source.path}</span>
                  </div>
                  <div className={`${styles.sourceStatus} ${source.enabled ? styles.enabled : styles.disabled}`}>
                    {source.enabled ? 'Active' : 'Disabled'}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Manual Ingestion */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Manual Document Ingestion</h3>
            <div className={styles.ingestForm}>
              <input
                type="text"
                className={styles.input}
                placeholder="Document name (e.g., CBA_Deal_Notes.txt)"
                value={documentName}
                onChange={(e) => setDocumentName(e.target.value)}
              />
              <select
                className={styles.select}
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
              >
                <option value="text">General Text</option>
                <option value="mom">Minutes of Meeting</option>
                <option value="case_study">Case Study</option>
                <option value="reference">Reference Material</option>
              </select>
              <textarea
                className={styles.textarea}
                placeholder="Paste document content here to add to the knowledge base..."
                value={manualContent}
                onChange={(e) => setManualContent(e.target.value)}
                rows={6}
              />
              <button
                className={styles.ingestBtn}
                onClick={handleIngest}
                disabled={ingesting || !manualContent.trim() || !documentName.trim()}
              >
                {ingesting ? 'Ingesting...' : 'Ingest Document'}
              </button>
            </div>
          </section>

          {/* Recent Jobs */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Recent Ingestion Jobs</h3>
            <div className={styles.jobsList}>
              {status?.recent_jobs?.length > 0 ? (
                status.recent_jobs.slice(0, 5).map((job) => (
                  <div key={job.id} className={styles.jobItem}>
                    <div className={styles.jobInfo}>
                      <span className={styles.jobName}>{job.document_name}</span>
                      <span className={styles.jobMeta}>
                        {job.chunks_created} chunks | {new Date(job.completed_at || job.started_at).toLocaleString()}
                      </span>
                    </div>
                    <div className={`${styles.jobStatus} ${styles[job.status]}`}>
                      {job.status}
                    </div>
                  </div>
                ))
              ) : (
                <div className={styles.emptyJobs}>No recent ingestion jobs</div>
              )}
            </div>
          </section>

          {/* Learning Loop / Feedback Stats */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Learning Loop Feedback</h3>
            {feedbackStats ? (
              <div className={styles.feedbackStats}>
                <div className={styles.feedbackStatCard}>
                  <div className={styles.feedbackStatValue}>{feedbackStats.total || 0}</div>
                  <div className={styles.feedbackStatLabel}>Total Feedback</div>
                </div>
                <div className={styles.feedbackStatCard}>
                  <div className={styles.feedbackStatValue} style={{ color: 'var(--color-success)' }}>
                    {feedbackStats.thumbs_up || 0}
                  </div>
                  <div className={styles.feedbackStatLabel}>Positive</div>
                </div>
                <div className={styles.feedbackStatCard}>
                  <div className={styles.feedbackStatValue} style={{ color: 'var(--color-error)' }}>
                    {feedbackStats.thumbs_down || 0}
                  </div>
                  <div className={styles.feedbackStatLabel}>Negative</div>
                </div>
                <div className={styles.feedbackStatCard}>
                  <div className={styles.feedbackStatValue} style={{ color: 'var(--color-primary)' }}>
                    {feedbackStats.satisfaction_rate || 0}%
                  </div>
                  <div className={styles.feedbackStatLabel}>Satisfaction Rate</div>
                </div>
              </div>
            ) : (
              <div className={styles.emptyJobs}>No feedback data yet</div>
            )}
            <p className={styles.feedbackNote}>
              Feedback from users helps improve agent responses over time. The learning loop 
              analyzes patterns in negative feedback to identify areas for improvement.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeAgentPanel;
