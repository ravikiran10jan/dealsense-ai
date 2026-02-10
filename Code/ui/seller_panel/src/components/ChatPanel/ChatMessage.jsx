import React from 'react';
import styles from './ChatMessage.module.css';

const ChatMessage = ({ message }) => {
  const { type, content, timestamp, metadata } = message;

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Render markdown-like content (simplified)
  const renderContent = (text) => {
    // Handle headers
    let processed = text.replace(/^### (.+)$/gm, '<h4 class="' + styles.h4 + '">$1</h4>');
    processed = processed.replace(/^## (.+)$/gm, '<h3 class="' + styles.h3 + '">$1</h3>');
    
    // Handle bold
    processed = processed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Handle italic
    processed = processed.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Handle inline code
    processed = processed.replace(/`(.+?)`/g, '<code class="' + styles.inlineCode + '">$1</code>');
    
    // Handle horizontal rules
    processed = processed.replace(/^---$/gm, '<hr class="' + styles.hr + '" />');
    
    // Handle bullet points
    processed = processed.replace(/^- (.+)$/gm, '<li>$1</li>');
    processed = processed.replace(/(<li>.*<\/li>\n?)+/gs, '<ul class="' + styles.list + '">$&</ul>');
    
    // Handle numbered lists
    processed = processed.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    
    // Handle simple tables (basic support)
    if (processed.includes('|')) {
      const lines = processed.split('\n');
      let inTable = false;
      let tableHtml = '';
      let newLines = [];
      
      lines.forEach((line, idx) => {
        if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
          if (!inTable) {
            inTable = true;
            tableHtml = '<table class="' + styles.table + '"><thead>';
          }
          
          const cells = line.split('|').filter(c => c.trim());
          const isHeader = idx === 0 || (lines[idx + 1] && lines[idx + 1].includes('---'));
          const isSeparator = line.includes('---');
          
          if (isSeparator) {
            tableHtml += '</thead><tbody>';
          } else if (isHeader && !tableHtml.includes('</thead>')) {
            tableHtml += '<tr>' + cells.map(c => `<th>${c.trim()}</th>`).join('') + '</tr>';
          } else {
            tableHtml += '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
          }
        } else {
          if (inTable) {
            tableHtml += '</tbody></table>';
            newLines.push(tableHtml);
            tableHtml = '';
            inTable = false;
          }
          newLines.push(line);
        }
      });
      
      if (inTable) {
        tableHtml += '</tbody></table>';
        newLines.push(tableHtml);
      }
      
      processed = newLines.join('\n');
    }
    
    // Handle line breaks
    processed = processed.replace(/\n\n/g, '</p><p>');
    processed = processed.replace(/\n/g, '<br />');
    
    return processed;
  };

  const getSourceBadge = () => {
    if (!metadata?.source && !metadata?.badge) return null;
    
    const badge = metadata.badge || metadata.source;
    let className = styles.badge;
    
    if (badge === 'RAG' || badge === 'rag') {
      className += ' ' + styles.badgeRag;
    } else if (badge === 'AI' || badge === 'ai' || badge === 'llm') {
      className += ' ' + styles.badgeAi;
    } else if (badge === 'RAG+AI' || badge === 'rag+ai') {
      className += ' ' + styles.badgeRagAi;
    }
    
    return <span className={className}>{badge.toUpperCase()}</span>;
  };

  if (type === 'system') {
    return (
      <div className={`${styles.message} ${styles.system}`}>
        <div className={styles.systemContent}>
          {metadata?.status === 'processing' && (
            <span className={styles.spinner}></span>
          )}
          {metadata?.status === 'live' && (
            <span className={styles.liveDot}></span>
          )}
          <span>{content}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.message} ${styles[type]}`}>
      {type === 'assistant' && (
        <div className={styles.avatar}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M8 14s1.5 2 4 2 4-2 4-2" />
            <line x1="9" y1="9" x2="9.01" y2="9" />
            <line x1="15" y1="9" x2="15.01" y2="9" />
          </svg>
        </div>
      )}
      <div className={styles.bubble}>
        <div className={styles.bubbleHeader}>
          <span className={styles.sender}>
            {type === 'assistant' ? 'Sales Copilot' : 'You'}
          </span>
          {getSourceBadge()}
          <span className={styles.time}>{formatTime(timestamp)}</span>
        </div>
        <div 
          className={styles.content}
          dangerouslySetInnerHTML={{ __html: renderContent(content) }}
        />
        {type === 'assistant' && (
          <div className={styles.actions}>
            <button className={styles.actionBtn} title="Copy">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
              </svg>
            </button>
            <button className={styles.actionBtn} title="Mark as follow-up">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
              </svg>
            </button>
          </div>
        )}
      </div>
      {type === 'user' && (
        <div className={styles.avatar}>
          <span>RK</span>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
