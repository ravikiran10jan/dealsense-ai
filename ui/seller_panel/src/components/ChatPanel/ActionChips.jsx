import React from 'react';
import styles from './ActionChips.module.css';

const actionsByPhase = {
  before: [
    { id: 'prepare', label: 'Prepare for upcoming call', icon: 'clipboard' },
    { id: 'similar', label: 'Show similar customers', icon: 'users' },
    { id: 'questions', label: 'Expected questions', icon: 'help' },
    { id: 'discovery', label: 'Draft discovery questions', icon: 'edit' },
  ],
  during: [
    { id: 'live-help', label: 'Live answer help', icon: 'zap' },
    { id: 'faqs', label: 'Product FAQs', icon: 'book' },
    { id: 'pricing', label: 'Pricing guidance', icon: 'dollar' },
    { id: 'objection', label: 'Handle objection', icon: 'shield' },
  ],
  after: [
    { id: 'summarize', label: 'Summarize this call', icon: 'file-text' },
    { id: 'email', label: 'Draft follow-up email', icon: 'mail' },
    { id: 'salesforce', label: 'Update Salesforce', icon: 'cloud' },
    { id: 'tasks', label: 'Create action items', icon: 'check-square' },
  ],
};

const ActionChips = ({ callPhase, isLiveCall, onAction }) => {
  const phase = isLiveCall ? 'during' : callPhase;
  const actions = actionsByPhase[phase] || actionsByPhase.before;

  const renderIcon = (iconName) => {
    switch (iconName) {
      case 'clipboard':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
          </svg>
        );
      case 'users':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        );
      case 'help':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        );
      case 'edit':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
        );
      case 'zap':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
        );
      case 'book':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
        );
      case 'dollar':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="1" x2="12" y2="23" />
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        );
      case 'shield':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
        );
      case 'file-text':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        );
      case 'mail':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>
        );
      case 'cloud':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />
          </svg>
        );
      case 'check-square':
        return (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 11 12 14 22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className={styles.chipsContainer}>
      <div className={styles.phaseLabel}>
        {phase === 'before' && 'Before Call'}
        {phase === 'during' && 'During Call'}
        {phase === 'after' && 'After Call'}
      </div>
      <div className={styles.chips}>
        {actions.map((action) => (
          <button
            key={action.id}
            className={styles.chip}
            onClick={() => onAction(action)}
          >
            <span className={styles.chipIcon}>{renderIcon(action.icon)}</span>
            <span className={styles.chipLabel}>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ActionChips;
