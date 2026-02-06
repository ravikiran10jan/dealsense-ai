import React, { useState } from 'react';
import styles from './ContextPanel.module.css';

const ContextPanel = ({
  deal,
  callPhase,
  isLiveCall,
  contextData,
  onStartLiveCall,
  onClose,
}) => {
  const [expandedSections, setExpandedSections] = useState({
    callDetails: true,
    similarDeals: true,
    references: false,
    questions: true,
    talkingPoints: true,
    actions: true,
  });

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const getPhaseLabel = () => {
    if (isLiveCall) return { text: 'Live', color: 'var(--color-live)' };
    switch (callPhase) {
      case 'before': return { text: 'Before Call', color: 'var(--color-info)' };
      case 'during': return { text: 'During Call', color: 'var(--color-success)' };
      case 'after': return { text: 'After Call', color: 'var(--color-warning)' };
      default: return { text: 'Before Call', color: 'var(--color-info)' };
    }
  };

  const phase = getPhaseLabel();

  // Trade Finance sample data for demonstration
  const similarDeals = contextData.similarDeals?.length > 0 ? contextData.similarDeals : [
    { name: 'CBA - Trade Finance Platform', value: '$5.2M', industry: 'Banking', status: 'Won' },
    { name: 'SMBC - LC Automation', value: '$3.8M', industry: 'Banking', status: 'Won' },
    { name: 'SCB - Trade Digitization', value: '$4.1M', industry: 'Banking', status: 'In Progress' },
  ];

  const references = contextData.references?.length > 0 ? contextData.references : [
    { name: 'Andrew Marvin', company: 'ASX (ex-CBA)', role: 'Head of Derivatives Clearing & Clearing Risk Technology', linkedin_url: 'https://www.linkedin.com/in/andrew-marvin-2138799/' },
    { name: 'Ian Stephenson', company: 'Standard Chartered Bank', role: 'CIO, Trade and Working Capital', linkedin_url: 'https://www.linkedin.com/in/ianstephenson/' },
  ];

  const expectedQuestions = contextData.expectedQuestions?.length > 0 ? contextData.expectedQuestions : [
    { theme: 'Team & Delivery', questions: ['CBA team size?', 'Timeline?'] },
    { theme: 'Data Privacy', questions: ['SCB privacy approach?', 'Regional data?'] },
    { theme: 'AI Capabilities', questions: ['AI in production?', 'Accuracy?'] },
  ];

  const talkingPoints = contextData.talkingPoints?.length > 0 ? contextData.talkingPoints : [
    'CBA: 45-person team, 18-month timeline',
    'SMBC: Integrated 3 core systems + SWIFT',
    'SCB: Singapore-only for data privacy',
    'AI POC: 92% doc classification accuracy',
  ];

  const actionItems = contextData.actionItems?.length > 0 ? contextData.actionItems : [];

  return (
    <aside className={styles.contextPanel}>
      {/* Header */}
      <header className={styles.header}>
        <h3 className={styles.title}>Context</h3>
        <button className={styles.closeBtn} onClick={onClose}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </header>

      <div className={styles.content}>
        {/* Call Status Badge */}
        <div className={styles.statusSection}>
          <div className={styles.statusBadge} style={{ backgroundColor: phase.color }}>
            {isLiveCall && <span className={styles.livePulse}></span>}
            {phase.text}
          </div>
          {isLiveCall && (
            <span className={styles.listeningText}>Listening to call...</span>
          )}
        </div>

        {/* Call Details */}
        <div className={styles.section}>
          <button
            className={styles.sectionHeader}
            onClick={() => toggleSection('callDetails')}
          >
            <span className={styles.sectionTitle}>Call Details</span>
            <svg
              className={`${styles.chevron} ${expandedSections.callDetails ? styles.expanded : ''}`}
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {expandedSections.callDetails && deal && (
            <div className={styles.sectionContent}>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Customer</span>
                <span className={styles.detailValue}>{deal.accountName}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Contact</span>
                <span className={styles.detailValue}>{deal.contactName}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Role</span>
                <span className={styles.detailValue}>{deal.contactRole}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Stage</span>
                <span className={styles.detailValue}>{deal.stage}</span>
              </div>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Next Call</span>
                <span className={styles.detailValue}>{deal.nextCallDate} at {deal.nextCallTime}</span>
              </div>
              <button className={styles.editBtn}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
                Edit details
              </button>
            </div>
          )}
        </div>

        {/* Similar Deals */}
        <div className={styles.section}>
          <button
            className={styles.sectionHeader}
            onClick={() => toggleSection('similarDeals')}
          >
            <span className={styles.sectionTitle}>Similar Deals</span>
            <span className={styles.badge}>{similarDeals.length}</span>
            <svg
              className={`${styles.chevron} ${expandedSections.similarDeals ? styles.expanded : ''}`}
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {expandedSections.similarDeals && (
            <div className={styles.sectionContent}>
              {similarDeals.map((deal, idx) => (
                <div key={idx} className={styles.dealCard}>
                  <div className={styles.dealCardHeader}>
                    <span className={styles.dealCardName}>{deal.name}</span>
                    <span className={`${styles.dealCardStatus} ${deal.status === 'Won' ? styles.won : ''}`}>
                      {deal.status}
                    </span>
                  </div>
                  <div className={styles.dealCardMeta}>
                    <span>{deal.industry}</span>
                    <span className={styles.dealCardValue}>{deal.value}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Credible References */}
        <div className={styles.section}>
          <button
            className={styles.sectionHeader}
            onClick={() => toggleSection('references')}
          >
            <span className={styles.sectionTitle}>Credible References</span>
            <span className={styles.badge}>{references.length}</span>
            <svg
              className={`${styles.chevron} ${expandedSections.references ? styles.expanded : ''}`}
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {expandedSections.references && (
            <div className={styles.sectionContent}>
              {references.map((ref, idx) => (
                <div key={idx} className={styles.referenceCard}>
                  <div className={styles.referenceAvatar}>
                    {ref.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className={styles.referenceInfo}>
                    {ref.linkedin_url ? (
                      <a 
                        href={ref.linkedin_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className={styles.referenceName}
                        style={{ color: 'var(--color-primary)', textDecoration: 'none' }}
                      >
                        {ref.name}
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginLeft: '4px', verticalAlign: 'middle' }}>
                          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                          <polyline points="15 3 21 3 21 9" />
                          <line x1="10" y1="14" x2="21" y2="3" />
                        </svg>
                      </a>
                    ) : (
                      <span className={styles.referenceName}>{ref.name}</span>
                    )}
                    <span className={styles.referenceRole}>{ref.role} at {ref.company}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Expected Questions */}
        <div className={styles.section}>
          <button
            className={styles.sectionHeader}
            onClick={() => toggleSection('questions')}
          >
            <span className={styles.sectionTitle}>Expected Questions</span>
            <svg
              className={`${styles.chevron} ${expandedSections.questions ? styles.expanded : ''}`}
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {expandedSections.questions && (
            <div className={styles.sectionContent}>
              {expectedQuestions.map((group, idx) => (
                <div key={idx} className={styles.questionGroup}>
                  <span className={styles.questionTheme}>{group.theme}</span>
                  <ul className={styles.questionList}>
                    {group.questions.map((q, qIdx) => (
                      <li key={qIdx}>{q}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Talking Points */}
        <div className={styles.section}>
          <button
            className={styles.sectionHeader}
            onClick={() => toggleSection('talkingPoints')}
          >
            <span className={styles.sectionTitle}>Suggested Talking Points</span>
            <svg
              className={`${styles.chevron} ${expandedSections.talkingPoints ? styles.expanded : ''}`}
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {expandedSections.talkingPoints && (
            <div className={styles.sectionContent}>
              <ul className={styles.talkingPointsList}>
                {talkingPoints.map((point, idx) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Action Items (shown after call) */}
        {actionItems.length > 0 && (
          <div className={styles.section}>
            <button
              className={styles.sectionHeader}
              onClick={() => toggleSection('actions')}
            >
              <span className={styles.sectionTitle}>Action Items</span>
              <span className={styles.badge}>{actionItems.length}</span>
              <svg
                className={`${styles.chevron} ${expandedSections.actions ? styles.expanded : ''}`}
                width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            {expandedSections.actions && (
              <div className={styles.sectionContent}>
                {actionItems.map((item, idx) => (
                  <div key={idx} className={styles.actionItem}>
                    <input type="checkbox" className={styles.actionCheckbox} />
                    <div className={styles.actionInfo}>
                      <span className={styles.actionTask}>{item.task}</span>
                      <span className={styles.actionMeta}>
                        {item.owner} | Due: {item.due}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <footer className={styles.footer}>
        <button className={styles.actionBtn}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />
          </svg>
          Update Salesforce
        </button>
        <button className={styles.actionBtn}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>
          Send Email
        </button>
        <button className={styles.actionBtn}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 11 12 14 22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
          Add Task
        </button>
      </footer>
    </aside>
  );
};

export default ContextPanel;
