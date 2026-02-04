/**
 * CallSummaryPanel - Displays post-call summary with action items
 * 
 * Features:
 * - Executive summary
 * - Key discussion points
 * - Pain points and objections
 * - Deal health score
 * - Editable action items
 * - Next steps
 */

import React, { useState } from 'react';
import styles from './CallSummaryPanel.module.css';

// Health score colors
const getHealthScoreColor = (score) => {
  if (score >= 8) return '#10b981'; // Green
  if (score >= 6) return '#f59e0b'; // Yellow
  if (score >= 4) return '#f97316'; // Orange
  return '#ef4444'; // Red
};

// Priority badge colors
const getPriorityColor = (priority) => {
  switch (priority) {
    case 'high': return '#ef4444';
    case 'medium': return '#f59e0b';
    case 'low': return '#10b981';
    default: return '#6b7280';
  }
};

function CallSummaryPanel({
  summary = null,
  actionItems = [],
  isLoading = false,
  onActionItemUpdate = null,
  onRegenerateSummary = null,
  onExport = null,
}) {
  const [expandedSections, setExpandedSections] = useState({
    keyPoints: true,
    painPoints: true,
    objections: true,
    actionItems: true,
  });
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };
  
  const handleActionItemStatusChange = (itemId, newStatus) => {
    if (onActionItemUpdate) {
      onActionItemUpdate(itemId, { status: newStatus });
    }
  };
  
  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Generating call summary...</p>
          <span className={styles.loadingSubtext}>This may take 30-60 seconds</span>
        </div>
      </div>
    );
  }
  
  if (!summary) {
    return (
      <div className={styles.container}>
        <div className={styles.empty}>
          <span className={styles.emptyIcon}>📋</span>
          <p>No summary available</p>
          <span className={styles.emptySubtext}>Summary will appear after the call ends</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.title}>Call Summary</h2>
        <div className={styles.headerActions}>
          {onRegenerateSummary && (
            <button className={styles.actionButton} onClick={onRegenerateSummary}>
              🔄 Regenerate
            </button>
          )}
          {onExport && (
            <button className={styles.actionButton} onClick={() => onExport('pdf')}>
              📥 Export PDF
            </button>
          )}
        </div>
      </div>
      
      {/* Deal Health Score */}
      <div className={styles.healthScore}>
        <div className={styles.healthScoreLabel}>Deal Health</div>
        <div 
          className={styles.healthScoreValue}
          style={{ backgroundColor: getHealthScoreColor(summary.deal_health_score) }}
        >
          {summary.deal_health_score}/10
        </div>
        <div className={styles.healthScoreReason}>{summary.deal_health_reason}</div>
      </div>
      
      {/* Executive Summary */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Executive Summary</h3>
        <p className={styles.executiveSummary}>{summary.executive_summary}</p>
      </div>
      
      {/* Key Discussion Points */}
      <div className={styles.section}>
        <div 
          className={styles.sectionHeader}
          onClick={() => toggleSection('keyPoints')}
        >
          <h3 className={styles.sectionTitle}>
            Key Discussion Points
            <span className={styles.badge}>{summary.key_points?.length || 0}</span>
          </h3>
          <span className={styles.toggleIcon}>
            {expandedSections.keyPoints ? '▼' : '▶'}
          </span>
        </div>
        {expandedSections.keyPoints && (
          <ul className={styles.bulletList}>
            {summary.key_points?.map((point, index) => (
              <li key={index} className={styles.bulletItem}>{point}</li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Pain Points */}
      {summary.pain_points?.length > 0 && (
        <div className={styles.section}>
          <div 
            className={styles.sectionHeader}
            onClick={() => toggleSection('painPoints')}
          >
            <h3 className={styles.sectionTitle}>
              Customer Pain Points
              <span className={styles.badge}>{summary.pain_points.length}</span>
            </h3>
            <span className={styles.toggleIcon}>
              {expandedSections.painPoints ? '▼' : '▶'}
            </span>
          </div>
          {expandedSections.painPoints && (
            <div className={styles.cardList}>
              {summary.pain_points.map((pp, index) => (
                <div key={index} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <span 
                      className={styles.severityBadge}
                      data-severity={pp.severity}
                    >
                      {pp.severity}
                    </span>
                  </div>
                  <p className={styles.cardContent}>{pp.description}</p>
                  {pp.context && (
                    <p className={styles.cardContext}>{pp.context}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Objections */}
      {summary.objections?.length > 0 && (
        <div className={styles.section}>
          <div 
            className={styles.sectionHeader}
            onClick={() => toggleSection('objections')}
          >
            <h3 className={styles.sectionTitle}>
              Objections Raised
              <span className={styles.badge}>{summary.objections.length}</span>
            </h3>
            <span className={styles.toggleIcon}>
              {expandedSections.objections ? '▼' : '▶'}
            </span>
          </div>
          {expandedSections.objections && (
            <div className={styles.cardList}>
              {summary.objections.map((obj, index) => (
                <div key={index} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <span className={styles.categoryBadge}>{obj.category}</span>
                  </div>
                  <p className={styles.cardContent}>{obj.description}</p>
                  {obj.response_suggested && (
                    <div className={styles.suggestedResponse}>
                      <span className={styles.suggestedLabel}>Suggested Response:</span>
                      <p>{obj.response_suggested}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Next Steps */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Next Steps</h3>
        <p className={styles.nextSteps}>{summary.next_steps}</p>
      </div>
      
      {/* Action Items */}
      <div className={styles.section}>
        <div 
          className={styles.sectionHeader}
          onClick={() => toggleSection('actionItems')}
        >
          <h3 className={styles.sectionTitle}>
            Action Items
            <span className={styles.badge}>{actionItems.length}</span>
          </h3>
          <span className={styles.toggleIcon}>
            {expandedSections.actionItems ? '▼' : '▶'}
          </span>
        </div>
        {expandedSections.actionItems && (
          <div className={styles.actionItemsList}>
            {actionItems.map((item) => (
              <div 
                key={item.id} 
                className={`${styles.actionItem} ${item.status === 'completed' ? styles.completed : ''}`}
              >
                <div className={styles.actionItemCheckbox}>
                  <input
                    type="checkbox"
                    checked={item.status === 'completed'}
                    onChange={(e) => handleActionItemStatusChange(
                      item.id, 
                      e.target.checked ? 'completed' : 'pending'
                    )}
                  />
                </div>
                <div className={styles.actionItemContent}>
                  <p className={styles.actionItemTask}>{item.task}</p>
                  <div className={styles.actionItemMeta}>
                    <span className={styles.actionItemOwner}>
                      👤 {item.owner}
                    </span>
                    {item.due_date && (
                      <span className={styles.actionItemDueDate}>
                        📅 {item.due_date}
                      </span>
                    )}
                    <span 
                      className={styles.actionItemPriority}
                      style={{ backgroundColor: getPriorityColor(item.priority) }}
                    >
                      {item.priority}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Generated timestamp */}
      {summary.generated_at && (
        <div className={styles.footer}>
          <span className={styles.timestamp}>
            Generated: {new Date(summary.generated_at).toLocaleString()}
          </span>
        </div>
      )}
    </div>
  );
}

export default CallSummaryPanel;
