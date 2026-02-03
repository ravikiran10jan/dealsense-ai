import React, { useState } from 'react';
import styles from './SharePointLinkInput.module.css';

/**
 * SharePointLinkInput Component
 * Allows users to input SharePoint links for data extraction
 * Mock implementation - no actual SharePoint integration
 */
const SharePointLinkInput = ({ onLinkSubmit }) => {
  const [link, setLink] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!link.trim()) {
      setError('Please enter a valid SharePoint link');
      return;
    }

    if (!link.includes('sharepoint') && !link.includes('onedrive')) {
      setError('Please enter a valid SharePoint or OneDrive link');
      return;
    }

    setIsLoading(true);
    // Simulate link validation and fetching
    setTimeout(() => {
      setIsLoading(false);
      if (onLinkSubmit) {
        onLinkSubmit(link);
      }
      setLink('');
    }, 1500);
  };

  return (
    <div className={styles.container}>
      <h2>SharePoint Integration</h2>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.inputGroup}>
          <label htmlFor="sharepoint-link">SharePoint or OneDrive Link</label>
          <input
            id="sharepoint-link"
            type="text"
            placeholder="https://company.sharepoint.com/sites/sales/Shared Documents/..."
            value={link}
            onChange={(e) => setLink(e.target.value)}
            disabled={isLoading}
            className={error ? styles.errorInput : ''}
          />
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <button
          type="submit"
          className={styles.submitButton}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Import from SharePoint'}
        </button>

        <div className={styles.infoBox}>
          <p className={styles.infoLabel}>ℹ️ How it works:</p>
          <ul>
            <li>Paste your SharePoint document link above</li>
            <li>System extracts relevant sales deal information</li>
            <li>Data is integrated with other sources</li>
            <li>Pre-call insights are generated automatically</li>
          </ul>
        </div>
      </form>
    </div>
  );
};

export default SharePointLinkInput;
