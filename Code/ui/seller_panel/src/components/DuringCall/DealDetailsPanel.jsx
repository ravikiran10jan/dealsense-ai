import React from 'react';
import styles from './DealDetailsPanel.module.css';

/**
 * DealDetailsPanel Component
 * Displays comprehensive deal information for reference during call
 */
const DealDetailsPanel = ({ deal }) => {
  if (!deal) {
    return (
      <div className={styles.placeholder}>
        <p>👈 Select a deal to view details</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2>{deal.title}</h2>
          <p className={styles.industry}>{deal.industry}</p>
        </div>
        <div className={styles.badge}>{deal.dealValue}</div>
      </div>

      <div className={styles.section}>
        <h3>Case Study Overview</h3>
        <p>{deal.caseStudy}</p>
      </div>

      <div className={styles.metricsGrid}>
        <div className={styles.metricBox}>
          <span className={styles.metricLabel}>Timeline</span>
          <span className={styles.metricValue}>{deal.duration}</span>
        </div>
        <div className={styles.metricBox}>
          <span className={styles.metricLabel}>Team Deployed</span>
          <span className={styles.metricValue}>{deal.teamSize}</span>
        </div>
        <div className={styles.metricBox}>
          <span className={styles.metricLabel}>Budget</span>
          <span className={styles.metricValue}>{deal.dealValue}</span>
        </div>
      </div>

      <div className={styles.section}>
        <h3>✓ Key Highlights</h3>
        <ul className={styles.highlightsList}>
          {deal.keyHighlights.map((highlight, idx) => (
            <li key={idx}>{highlight}</li>
          ))}
        </ul>
      </div>

      <div className={styles.section}>
        <h3>⚠️ Deal Breakers</h3>
        <ul className={styles.warningList}>
          {deal.dealBreakers.map((breaker, idx) => (
            <li key={idx}>{breaker}</li>
          ))}
        </ul>
      </div>

      <div className={styles.section}>
        <h3>Success Criteria</h3>
        <div className={styles.criteriaList}>
          {deal.successCriteria?.map((criteria, idx) => (
            <div key={idx} className={styles.criteriaItem}>
              <span className={styles.checkmark}>✓</span>
              <span>{criteria}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DealDetailsPanel;
