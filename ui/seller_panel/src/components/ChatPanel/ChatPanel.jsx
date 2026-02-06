import React, { useState, useRef, useEffect, useCallback } from 'react';
import styles from './ChatPanel.module.css';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ActionChips from './ActionChips';
import { usePushToTalk } from '../../hooks/useHotkeyManager';

// Backend API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

// Query the RAG + LLM backend
async function queryRAG(query) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({ query }),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('RAG query failed:', error);
    return { answer: `Error querying knowledge base: ${error.message}`, sources: [] };
  }
}

// Web Speech API support check
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

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
  // New props for live call
  transcriptChunks = [],
  showTranscript = true,
  onLiveQuery,
  isPushToTalkActive = false,
}) => {
  const [isTyping, setIsTyping] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [liveQueryInput, setLiveQueryInput] = useState('');
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [recognitionError, setRecognitionError] = useState(null);
  const messagesEndRef = useRef(null);
  const transcriptEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const liveQueryInputRef = useRef('');

  // Keep ref in sync with state for use in callbacks
  useEffect(() => {
    liveQueryInputRef.current = liveQueryInput;
  }, [liveQueryInput]);

  // Initialize speech recognition
  useEffect(() => {
    if (SpeechRecognition && isLiveCall) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        console.log('Speech recognition started');
        setIsRecognizing(true);
        setRecognitionError(null);
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        // Update the input with recognized text
        const currentText = finalTranscript || interimTranscript;
        if (currentText) {
          setLiveQueryInput((prev) => {
            // If we have final transcript, append it
            if (finalTranscript) {
              return (prev + ' ' + finalTranscript).trim();
            }
            // For interim, show current recognition
            return (prev.split(' ').slice(0, -1).join(' ') + ' ' + interimTranscript).trim() || interimTranscript;
          });
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setRecognitionError(event.error);
        setIsRecognizing(false);
      };

      recognition.onend = () => {
        console.log('Speech recognition ended');
        setIsRecognizing(false);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Ignore errors on cleanup
        }
      }
    };
  }, [isLiveCall]);

  // Push-to-talk hook - only enabled during live call
  const { isListening, hotkeyLabel } = usePushToTalk({
    enabled: isLiveCall,
    onStart: () => {
      console.log('Push-to-talk activated');
      setLiveQueryInput('');
      setRecognitionError(null);
      // Start speech recognition
      if (recognitionRef.current && SpeechRecognition) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.error('Failed to start speech recognition:', e);
          setRecognitionError('Failed to start');
        }
      }
    },
    onEnd: () => {
      console.log('Push-to-talk deactivated');
      // Stop speech recognition
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Ignore errors
        }
      }
      // Submit the query if there's input (use ref for latest value)
      const queryText = liveQueryInputRef.current.trim();
      if (queryText && onLiveQuery) {
        console.log('Submitting voice query:', queryText);
        onLiveQuery(queryText);
        setLiveQueryInput('');
      }
    },
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-scroll transcript
  useEffect(() => {
    if (showTranscript && transcriptChunks.length > 0) {
      transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcriptChunks, showTranscript]);

  // Handle action chip clicks - queries RAG backend or transcript summarization
  const handleAction = useCallback(async (action) => {
    // Add user action as a message
    onSendMessage({
      type: 'user',
      content: action.label,
      metadata: { action: action.id },
    });

    // Check if this is a transcript-based action (after call with transcript data)
    const transcriptBasedActions = ['summarize', 'tasks', 'email'];
    const hasTranscript = transcriptChunks && transcriptChunks.length > 0;
    const isAfterCall = callPhase === 'after';
    
    if (transcriptBasedActions.includes(action.id) && hasTranscript && isAfterCall) {
      // Use transcript summarization endpoint
      setProcessingStatus('Analyzing call transcript...');
      onSendMessage({
        type: 'system',
        content: 'Analyzing your call transcript...',
        metadata: { status: 'processing', source: 'transcript' },
      });

      try {
        // Build transcript text from chunks
        const transcriptText = transcriptChunks
          .map(chunk => `${chunk.speaker}: ${chunk.text}`)
          .join('\n');

        // Map action ID to action type
        const actionTypeMap = {
          'summarize': 'summarize',
          'tasks': 'actions',
          'email': 'email',
        };

        const response = await fetch(`${API_BASE_URL}/api/summarize-transcript`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY,
          },
          body: JSON.stringify({
            transcript: transcriptText,
            action_type: actionTypeMap[action.id],
            account_name: selectedDeal?.accountName,
            contact_name: selectedDeal?.contactName,
          }),
        });

        if (!response.ok) throw new Error(`API error: ${response.status}`);
        const result = await response.json();

        setProcessingStatus(null);
        setIsTyping(true);
        await new Promise((resolve) => setTimeout(resolve, 300));
        setIsTyping(false);

        onSendMessage({
          type: 'assistant',
          content: result.answer,
          metadata: { source: 'transcript', badge: 'Transcript' },
        });
      } catch (error) {
        console.error('Transcript summarization failed:', error);
        setProcessingStatus(null);
        onSendMessage({
          type: 'assistant',
          content: `Error analyzing transcript: ${error.message}`,
          metadata: { source: 'error' },
        });
      }
      return;
    }

    // Standard RAG flow for other actions
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
  }, [selectedDeal, onSendMessage, onUpdateContext, transcriptChunks, callPhase]);

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

      {/* Main Content Area - Split when live call with transcript */}
      <div className={`${styles.mainContent} ${isLiveCall && showTranscript ? styles.split : ''}`}>
        {/* Transcript Panel - Only during live call */}
        {isLiveCall && showTranscript && (
          <div className={styles.transcriptPanel}>
            <div className={styles.transcriptHeader}>
              <span className={styles.transcriptTitle}>Live Transcript</span>
              <span className={styles.transcriptCount}>
                {transcriptChunks.length} segments
              </span>
            </div>
            <div className={styles.transcriptContent}>
              {transcriptChunks.length === 0 ? (
                <div className={styles.transcriptEmpty}>
                  <span>Waiting for audio...</span>
                  <span className={styles.transcriptHint}>
                    Transcript will appear here as the call progresses
                  </span>
                </div>
              ) : (
                <>
                  {transcriptChunks.map((chunk, index) => (
                    <div
                      key={index}
                      className={`${styles.transcriptChunk} ${
                        chunk.speaker === 'Customer' ? styles.customer : styles.seller
                      }`}
                    >
                      <span className={styles.transcriptSpeaker}>{chunk.speaker}</span>
                      <span className={styles.transcriptText}>{chunk.text}</span>
                      <span className={styles.transcriptTime}>
                        {formatTime(chunk.startTime)}
                      </span>
                    </div>
                  ))}
                  <div ref={transcriptEndRef} />
                </>
              )}
            </div>
          </div>
        )}

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
      </div>

      {/* Push-to-Talk Indicator */}
      {isLiveCall && (isListening || isPushToTalkActive) && (
        <div className={styles.pushToTalkOverlay}>
          <div className={styles.pushToTalkIndicator}>
            <div className={`${styles.micIcon} ${isRecognizing ? styles.recording : ''}`}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="23" />
                <line x1="8" y1="23" x2="16" y2="23" />
              </svg>
            </div>
            <span className={styles.pushToTalkText}>
              {recognitionError 
                ? `Error: ${recognitionError}` 
                : isRecognizing 
                  ? 'Listening... Speak your question'
                  : 'Starting voice recognition...'}
            </span>
            {liveQueryInput && (
              <div className={styles.recognizedText}>
                &quot;{liveQueryInput}&quot;
              </div>
            )}
            <input
              type="text"
              className={styles.pushToTalkInput}
              value={liveQueryInput}
              onChange={(e) => setLiveQueryInput(e.target.value)}
              placeholder={SpeechRecognition ? 'Speak or type your question...' : 'Type your question...'}
            />
            <span className={styles.pushToTalkHint}>
              Release {hotkeyLabel} to submit
              {!SpeechRecognition && ' (Voice not supported in this browser)'}
            </span>
          </div>
        </div>
      )}

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
        placeholder={
          isLiveCall
            ? `Press ${hotkeyLabel} to ask during call, or type here...`
            : selectedDeal
            ? 'Ask your sales copilot...'
            : 'Select a deal to start'
        }
        isLiveCall={isLiveCall}
      />
    </div>
  );
};

// Helper function to format time
function formatTime(seconds) {
  if (typeof seconds !== 'number') return '';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default ChatPanel;
