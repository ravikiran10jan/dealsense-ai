import React, { useState, useRef, useEffect, useCallback } from 'react';
import styles from './ChatPanel.module.css';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ActionChips from './ActionChips';

// Backend API base URL
const API_BASE_URL = 'http://localhost:8000';

// Query the RAG + LLM backend
async function queryRAG(query) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('RAG query failed:', error);
    return { answer: `Error querying knowledge base: ${error.message}`, sources: [] };
  }
}

const ChatPanel = ({
  messages,
  onSendMessage,
  selectedDeal,
  callPhase,
  isLiveCall,
  onStartLiveCall,
  onEndCall,
  onUpdateContext,
  onToggleContextPanel,
  contextPanelVisible,
}) => {
  const [isTyping, setIsTyping] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle action chip clicks - queries RAG backend
  const handleAction = useCallback(async (action) => {
    // Add user action as a message
    onSendMessage({
      type: 'user',
      content: action.label,
      metadata: { action: action.id },
    });

    // Show RAG search status
    setProcessingStatus('Searching knowledge base...');
    onSendMessage({
      type: 'system',
      content: 'Searching knowledge base and past deals (RAG)...',
      metadata: { status: 'processing', source: 'rag' },
    });

    // Build the query based on action type
    let query = '';
    switch (action.id) {
      case 'prepare':
        query = `Prepare a call briefing for ${selectedDeal?.accountName}. Include information about trade finance capabilities, similar implementations, team sizes, and key differentiators.`;
        break;
      case 'similar':
        query = `What are similar trade finance implementations to ${selectedDeal?.accountName}? Include details about team sizes, timelines, outcomes, and key success factors from CBA, SMBC, and SCB projects.`;
        break;
      case 'questions':
        query = `What are the expected questions in a trade finance discovery call? Include questions about team size at CBA, data privacy handling, AI capabilities status, and DXC Luxoft history.`;
        break;
      case 'discovery':
        query = `What are good discovery questions to ask ${selectedDeal?.accountName} about their trade finance transformation needs?`;
        break;
      case 'live-help':
        query = `What information is available in the knowledge base to help during a live call with ${selectedDeal?.accountName} about trade finance?`;
        break;
      case 'summarize':
        query = `Summarize the key points from the trade finance knowledge base that would be relevant for a call summary with ${selectedDeal?.accountName}.`;
        break;
      case 'email':
        query = `Draft a follow-up email for ${selectedDeal?.accountName} about trade finance transformation, referencing CBA, SMBC, and SCB implementations.`;
        break;
      case 'salesforce':
        query = `What key deal information should be captured in Salesforce for ${selectedDeal?.accountName} trade finance opportunity?`;
        break;
      default:
        query = action.label;
    }

    // Query the RAG backend
    const result = await queryRAG(query);

    // Show LLM status
    setProcessingStatus('Generating response...');
    onSendMessage({
      type: 'system',
      content: 'Blending RAG context and AI reasoning...',
      metadata: { status: 'processing', source: 'llm' },
    });

    await new Promise((resolve) => setTimeout(resolve, 500));
    setProcessingStatus(null);
    setIsTyping(true);
    await new Promise((resolve) => setTimeout(resolve, 300));
    setIsTyping(false);

    // Determine the source badge based on whether we got results from RAG
    const hasSources = result.sources && result.sources.length > 0;
    const sourceBadge = hasSources ? 'RAG+AI' : 'AI';
    
    // Format the response with sources
    let formattedResponse = result.answer;
    if (hasSources) {
      formattedResponse += `\n\n---\n**Sources:** ${result.sources.join(', ')}`;
    }

    onSendMessage({
      type: 'assistant',
      content: formattedResponse,
      metadata: { source: sourceBadge.toLowerCase().replace('+', '+'), badge: sourceBadge },
    });

    // Update context panel based on action
    if (action.id === 'prepare' || action.id === 'similar') {
      onUpdateContext({
        similarDeals: [
          { name: 'CBA - Trade Finance Platform', value: '$5.2M', industry: 'Banking', status: 'Won' },
          { name: 'SMBC - LC Automation', value: '$3.8M', industry: 'Banking', status: 'Won' },
          { name: 'SCB - Trade Digitization', value: '$4.1M', industry: 'Banking', status: 'In Progress' },
        ],
      });
    }
  }, [selectedDeal, onSendMessage, onUpdateContext]);

  // Handle text input - queries RAG backend
  const handleSendMessage = useCallback(async (text) => {
    onSendMessage({
      type: 'user',
      content: text,
    });

    // Show RAG search status
    setProcessingStatus('Searching knowledge base...');
    onSendMessage({
      type: 'system',
      content: 'Searching knowledge base and past deals (RAG)...',
      metadata: { status: 'processing', source: 'rag' },
    });

    // Query the RAG backend with context about the selected deal
    const contextualQuery = selectedDeal 
      ? `In the context of ${selectedDeal.accountName} (${selectedDeal.industry}): ${text}`
      : text;
    
    const result = await queryRAG(contextualQuery);

    // Show LLM status
    setProcessingStatus('Generating response...');
    onSendMessage({
      type: 'system',
      content: 'Blending RAG context and AI reasoning...',
      metadata: { status: 'processing', source: 'llm' },
    });

    await new Promise((resolve) => setTimeout(resolve, 500));
    setProcessingStatus(null);
    setIsTyping(true);
    await new Promise((resolve) => setTimeout(resolve, 300));
    setIsTyping(false);

    // Determine the source badge based on whether we got results from RAG
    const hasSources = result.sources && result.sources.length > 0;
    const sourceBadge = hasSources ? 'RAG+AI' : 'AI';
    
    // Format the response with sources
    let formattedResponse = result.answer;
    if (hasSources) {
      formattedResponse += `\n\n---\n**Sources:** ${result.sources.join(', ')}`;
    }

    onSendMessage({
      type: 'assistant',
      content: formattedResponse,
      metadata: { source: sourceBadge.toLowerCase().replace('+', '+'), badge: sourceBadge },
    });
  }, [selectedDeal, onSendMessage]);

  return (
    <div className={styles.chatPanel}>
      {/* Chat Header */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <h2 className={styles.title}>
            {selectedDeal ? selectedDeal.accountName : 'Select a Deal'}
          </h2>
          {selectedDeal && (
            <div className={styles.headerMeta}>
              <span className={styles.contactName}>{selectedDeal.contactName}</span>
              <span className={styles.separator}>|</span>
              <span className={styles.stage}>{selectedDeal.stage}</span>
            </div>
          )}
        </div>
        <div className={styles.headerActions}>
          {!isLiveCall && callPhase !== 'after' && (
            <button className={styles.startCallBtn} onClick={onStartLiveCall}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
              Start Live Call
            </button>
          )}
          <button
            className={`${styles.toggleContextBtn} ${contextPanelVisible ? styles.active : ''}`}
            onClick={onToggleContextPanel}
            title="Toggle context panel"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="15" y1="3" x2="15" y2="21" />
            </svg>
          </button>
        </div>
      </header>

      {/* Messages Area */}
      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <h3 className={styles.emptyTitle}>Welcome to DealSense AI</h3>
            <p className={styles.emptyText}>
              Select a deal from the sidebar to start your sales copilot session.
              I'll help you prepare for calls, assist during conversations, and follow up after.
            </p>
          </div>
        ) : (
          <div className={styles.messagesList}>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isTyping && (
              <div className={styles.typingIndicator}>
                <div className={styles.typingDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className={styles.typingText}>Sales Copilot is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Action Chips */}
      {selectedDeal && (
        <ActionChips
          callPhase={callPhase}
          isLiveCall={isLiveCall}
          onAction={handleAction}
        />
      )}

      {/* Input Area */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={!selectedDeal}
        placeholder={selectedDeal ? 'Ask your sales copilot...' : 'Select a deal to start'}
        isLiveCall={isLiveCall}
      />
    </div>
  );
};

export default ChatPanel;
