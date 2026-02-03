import React, { useState } from 'react';
import styles from './PreCallSummary.module.css';

/**
 * PreCallSummary Component
 * Displays Top 5 deals with key insights and metrics
 * Allows user to view details and download PDF
 */
const PreCallSummary = ({ deals }) => {
  const [selectedDeal, setSelectedDeal] = useState(null);

  const handleDownloadPDF = () => {
    // Mock PDF download
    alert('📄 PDF Summary Downloaded!\n\nThis is a mock implementation.\nIn production, this would generate and download a PDF file.');
  };

  const handleViewDetails = (deal) => {
    setSelectedDeal(selectedDeal?.id === deal.id ? null : deal);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Pre-Call Summary: Top 5 Deals</h2>
        <button className={styles.downloadButton} onClick={handleDownloadPDF}>
          📥 Download Summary (PDF)
        </button>
      </div>

      <div className={styles.dealsGrid}>
        {deals.map((deal) => (
          <div key={deal.id} className={styles.dealCard}>
            <div className={styles.cardHeader}>
              <div className={styles.dealInfo}>
                <h3>{deal.title}</h3>
                <p className={styles.industry}>{deal.industry}</p>
              </div>
              <div className={styles.dealValue}>{deal.dealValue}</div>
            </div>

            <p className={styles.summary}>{deal.summary}</p>

            <div className={styles.benchmarkTag}>{deal.benchmark}</div>

            <div className={styles.cardMetrics}>
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Timeline</span>
                <span className={styles.metricValue}>{deal.duration}</span>
              </div>
              <div className={styles.metric}>
                <span className={styles.metricLabel}>Team Size</span>
                <span className={styles.metricValue}>{deal.teamSize}</span>
              </div>
            </div>

            <button
              className={styles.detailsButton}
              onClick={() => handleViewDetails(deal)}
            >
              {selectedDeal?.id === deal.id ? '▼ Hide Details' : '▶ View Details'}
            </button>

            {selectedDeal?.id === deal.id && (
              <div className={styles.expandedDetails}>
                <div className={styles.section}>
                  <h4>Case Study</h4>
                  <p>{deal.caseStudy}</p>
                </div>

                <div className={styles.section}>
                  <h4>Key Highlights</h4>
                  <ul className={styles.list}>
                    {deal.keyHighlights.map((highlight, idx) => (
                      <li key={idx}>{highlight}</li>
                    ))}
                  </ul>
                </div>

                <div className={styles.section}>
                  <h4>Deal Breakers</h4>
                  <ul className={styles.listWarning}>
                    {deal.dealBreakers.map((breaker, idx) => (
                      <li key={idx}>{breaker}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PreCallSummary;
