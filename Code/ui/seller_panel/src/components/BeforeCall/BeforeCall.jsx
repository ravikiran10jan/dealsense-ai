import React from 'react';
import styles from './BeforeCall.module.css';
import ChatAgent from './ChatAgent';
// PreCallSummary removed — results now come from ChatAgent search

/**
 * BeforeCall Tab Component
 * Pre-sales preparation with data upload and Top 5 deals insights
 */
const BeforeCall = () => {
  const handleFileSelect = (file) => {
    console.log('File selected:', file);
    // Mock: In production, would process the file
  };

  const handleSharePointLink = (link) => {
    console.log('SharePoint link submitted:', link);
    // Mock: In production, would fetch from SharePoint
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <h1>📋 Before Call: Pre-Sales Preparation</h1>
        <p>
          Prepare for your sales call by uploading customer data and reviewing insights
          from our top performing deals.
        </p>
      </div>

      <div className={styles.inputSection}>
        <ChatAgent />
      </div>
    </div>
  );
};

export default BeforeCall;
