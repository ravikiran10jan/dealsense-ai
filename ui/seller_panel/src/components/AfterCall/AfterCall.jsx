import React, { useState } from 'react';
import styles from './AfterCall.module.css';
import { mockDeals } from '../../data/mockData';

/**
 * AfterCall Tab Component
 * Post-call summary and reporting
 */
const AfterCall = () => {
  const [summary, setSummary] = useState({
    dealTitle: mockDeals[0].title,
    finalHighlights: '',
    risks: '',
    callOutcome: 'Follow-up',
    nextSteps: '',
    clientFeedback: '',
  });

  const [isGenerated, setIsGenerated] = useState(false);

  const handleInputChange = (field, value) => {
    setSummary((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleGenerateReport = () => {
    if (summary.finalHighlights && summary.risks && summary.callOutcome) {
      setIsGenerated(true);
      // Mock report generation
      setTimeout(() => {
        alert('📊 Final Report Generated!\n\nIn production, this would create a comprehensive PDF report with all call details, outcomes, and next steps.');
        setIsGenerated(false);
      }, 1500);
    } else {
      alert('⚠️ Please fill in all required fields:\n- Final Highlights\n- Risks / Deal Breakers\n- Call Outcome');
    }
  };

  const handleDownloadReport = () => {
    alert('📥 Report Downloaded!\n\nMock implementation - would download PDF in production.');
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <h1>✓ After Call: Post-Call Summary</h1>
        <p>
          Finalize outcomes, document risks, and prepare next steps from your sales call.
        </p>
      </div>

      <div className={styles.summaryForm}>
        <div className={styles.formSection}>
          <label htmlFor="deal-title" className={styles.required}>
            Deal Title
          </label>
          <select
            id="deal-title"
            value={summary.dealTitle}
            onChange={(e) => handleInputChange('dealTitle', e.target.value)}
            className={styles.select}
          >
            {mockDeals.map((deal) => (
              <option key={deal.id} value={deal.title}>
                {deal.title}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.formSection}>
          <label htmlFor="highlights" className={styles.required}>
            Final Highlights & Opportunities
          </label>
          <textarea
            id="highlights"
            value={summary.finalHighlights}
            onChange={(e) => handleInputChange('finalHighlights', e.target.value)}
            placeholder="What were the key positive points discussed? What opportunities were identified?"
            className={styles.textarea}
            rows="4"
          />
        </div>

        <div className={styles.formSection}>
          <label htmlFor="risks" className={styles.required}>
            Risks & Deal Breakers
          </label>
          <textarea
            id="risks"
            value={summary.risks}
            onChange={(e) => handleInputChange('risks', e.target.value)}
            placeholder="What concerns or objections were raised? What could prevent the deal from closing?"
            className={styles.textarea}
            rows="4"
          />
        </div>

        <div className={styles.formGrid}>
          <div className={styles.formSection}>
            <label htmlFor="outcome" className={styles.required}>
              Call Outcome
            </label>
            <select
              id="outcome"
              value={summary.callOutcome}
              onChange={(e) => handleInputChange('callOutcome', e.target.value)}
              className={styles.select}
            >
              <option value="Won">🎉 Won</option>
              <option value="Lost">❌ Lost</option>
              <option value="Follow-up">🔄 Follow-up</option>
            </select>
          </div>

          <div className={styles.formSection}>
            <label htmlFor="feedback">Client Feedback Score (1-10)</label>
            <input
              id="feedback"
              type="number"
              min="1"
              max="10"
              value={summary.clientFeedback}
              onChange={(e) => handleInputChange('clientFeedback', e.target.value)}
              placeholder="Rate client interest (1-10)"
              className={styles.input}
            />
          </div>
        </div>

        <div className={styles.formSection}>
          <label htmlFor="next-steps">Next Steps</label>
          <textarea
            id="next-steps"
            value={summary.nextSteps}
            onChange={(e) => handleInputChange('nextSteps', e.target.value)}
            placeholder="What are the agreed next steps? When is the follow-up scheduled?"
            className={styles.textarea}
            rows="3"
          />
        </div>

        <div className={styles.actions}>
          <button
            className={styles.generateButton}
            onClick={handleGenerateReport}
            disabled={isGenerated}
          >
            {isGenerated ? 'Generating...' : '📊 Generate Final Report'}
          </button>
          <button
            className={styles.downloadButton}
            onClick={handleDownloadReport}
            disabled={!isGenerated && !summary.callOutcome}
          >
            📥 Download Summary (PDF)
          </button>
        </div>
      </div>

      {summary.callOutcome && (
        <div className={`${styles.outcomeIndicator} ${styles[summary.callOutcome.toLowerCase()]}`}>
          <span className={styles.outcomeIcon}>
            {summary.callOutcome === 'Won' && '🎉'}
            {summary.callOutcome === 'Lost' && '❌'}
            {summary.callOutcome === 'Follow-up' && '🔄'}
          </span>
          <span>Call Outcome: <strong>{summary.callOutcome}</strong></span>
        </div>
      )}
    </div>
  );
};

export default AfterCall;
