import React, { useState, useCallback, useEffect, useRef } from 'react';
import './styles/globals.css';
import styles from './App.module.css';
import Sidebar from './components/Sidebar/Sidebar';
import ChatPanel from './components/ChatPanel/ChatPanel';
import ContextPanel from './components/ContextPanel/ContextPanel';
import LiveCallStrip from './components/common/LiveCallStrip';
import AddDealModal from './components/AddDealModal/AddDealModal';
import MyCalls from './components/MyCalls/MyCalls';
import CallSummaryPanel from './components/CallSummaryPanel';
import ArchitectureModal from './components/ArchitectureModal/ArchitectureModal';
import { getAudioCaptureService, ConnectionState } from './services/AudioCaptureService';

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

// Hotkey label for push-to-talk
const hotkeyLabel = 'Shift+Space';

// Trade Finance deals data for sidebar
const initialDeals = [
  {
    id: 1,
    accountName: 'ANZ Bank',
    stage: 'Discovery',
    nextCallDate: '2026-02-04',
    nextCallTime: '10:00 AM',
    dealAmount: '$4.5M',
    contactName: 'David Chen',
    contactRole: 'Head of Trade Finance Operations',
    industry: 'Banking - Trade Finance',
    description: 'Trade Finance Transformation Journey',
    additionalContacts: [
      { name: 'Sarah Mitchell', role: 'VP Technology' },
      { name: 'James Wong', role: 'Director of Digital Transformation' },
    ],
  },
  {
    id: 2,
    accountName: 'PNB (Philippine National Bank)',
    stage: 'Proposal',
    nextCallDate: '2026-02-08',
    nextCallTime: '2:00 PM',
    dealAmount: '$2.8M',
    contactName: 'Maria Santos',
    contactRole: 'SVP Operations',
    industry: 'Banking - Trade Finance',
    description: 'Trade Finance Digitization',
  },
  {
    id: 3,
    accountName: 'Westpac',
    stage: 'Discovery',
    nextCallDate: '2026-02-12',
    nextCallTime: '11:00 AM',
    dealAmount: '$3.6M',
    contactName: 'Robert Taylor',
    contactRole: 'Head of Transaction Banking',
    industry: 'Banking - Trade Finance',
    description: 'LC Processing Automation',
  },
  {
    id: 4,
    accountName: 'NAB (National Australia Bank)',
    stage: 'Discovery',
    nextCallDate: '2026-02-15',
    nextCallTime: '9:30 AM',
    dealAmount: '$3.2M',
    contactName: 'Amanda Foster',
    contactRole: 'Director Trade Services',
    industry: 'Banking - Trade Finance',
    description: 'Trade Finance Modernization',
  },
];

function App() {
  const [deals, setDeals] = useState(initialDeals);
  const [selectedDeal, setSelectedDeal] = useState(initialDeals[0]);
  const [callPhase, setCallPhase] = useState('before'); // before, during, after
  const [isLiveCall, setIsLiveCall] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [messages, setMessages] = useState([]);
  const [contextData, setContextData] = useState({
    similarDeals: [],
    references: [],
    expectedQuestions: [],
    talkingPoints: [],
    actionItems: [],
  });
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [contextPanelVisible, setContextPanelVisible] = useState(true);
  const [isAddDealModalOpen, setIsAddDealModalOpen] = useState(false);
  const [isArchitectureModalOpen, setIsArchitectureModalOpen] = useState(false);
  const [activeNav, setActiveNav] = useState('inbox');
  
  // Live call state
  const [callId, setCallId] = useState(null);
  const [connectionState, setConnectionState] = useState(ConnectionState.DISCONNECTED);
  const [transcriptChunks, setTranscriptChunks] = useState([]);
  const [showTranscript, setShowTranscript] = useState(true);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [callSummary, setCallSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  
  // Audio capture service reference
  const audioServiceRef = useRef(null);
  const callIdRef = useRef(null);

  // Keep callIdRef in sync with callId state
  useEffect(() => {
    callIdRef.current = callId;
  }, [callId]);

  // Initialize audio service (only once on mount)
  useEffect(() => {
    audioServiceRef.current = getAudioCaptureService();
    
    // Set up event handlers
    audioServiceRef.current.setOnConnectionStateChange((state) => {
      setConnectionState(state);
    });
    
    audioServiceRef.current.setOnTranscriptChunk((chunk) => {
      setTranscriptChunks((prev) => [...prev, chunk]);
      setIsTranscribing(true);
      // Reset transcribing indicator after a delay
      setTimeout(() => setIsTranscribing(false), 2000);
    });
    
    audioServiceRef.current.setOnQueryResponse((response) => {
      // Add live answer to messages
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          metadata: { 
            source: 'live', 
            badge: 'Live Answer',
            sources: response.sources,
            confidence: response.confidence,
          },
        },
      ]);
    });
    
    audioServiceRef.current.setOnStatusUpdate((status) => {
      console.log('Call status update:', status);
      if (status.status === 'ended') {
        setSummaryLoading(true);
      }
    });
    
    audioServiceRef.current.setOnSummaryReady(async () => {
      // Fetch the summary using ref to get current callId
      const currentCallId = callIdRef.current;
      if (!currentCallId) return;
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/calls/${currentCallId}/summary`, {
          headers: {
            'X-API-Key': API_KEY,
          },
        });
        if (response.ok) {
          const summaryData = await response.json();
          setCallSummary(summaryData.summary);
          setContextData((prev) => ({
            ...prev,
            actionItems: summaryData.action_items || [],
          }));
        }
      } catch (error) {
        console.error('Failed to fetch summary:', error);
      }
      setSummaryLoading(false);
    });
    
    audioServiceRef.current.setOnError((error) => {
      console.error('Call error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: 'system',
          content: `Error: ${error.error}`,
          timestamp: new Date(),
          metadata: { status: 'error' },
        },
      ]);
    });
    
    return () => {
      // Cleanup on unmount
      if (audioServiceRef.current?.isConnected()) {
        audioServiceRef.current.disconnect();
      }
    };
  }, []);

  // Handle deal selection
  const handleDealSelect = useCallback((deal) => {
    setSelectedDeal(deal);
    setCallPhase('before');
    setIsLiveCall(false);
    setCallDuration(0);
    // Reset messages for new deal with welcome message
    setMessages([
      {
        id: Date.now(),
        type: 'assistant',
        content: `I've pulled recent deals similar to **${deal.accountName}** and prepared context for your upcoming call with **${deal.contactName}**. What would you like to focus on for this call?`,
        timestamp: new Date(),
        metadata: { source: 'system' },
      },
    ]);
    // Reset context data
    setContextData({
      similarDeals: [],
      references: [],
      expectedQuestions: [],
      talkingPoints: [],
      actionItems: [],
    });
  }, []);

  // Handle starting live call
  const handleStartLiveCall = useCallback(async () => {
    setIsLiveCall(true);
    setCallPhase('during');
    setTranscriptChunks([]);
    setCallSummary(null);
    
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: 'system',
        content: 'Connecting to call...',
        timestamp: new Date(),
        metadata: { status: 'connecting' },
      },
    ]);
    
    // Connect to WebSocket (service will create call via REST API first)
    try {
      await audioServiceRef.current.connect(null, {
        dealId: selectedDeal?.id,
        accountName: selectedDeal?.accountName,
        contactName: selectedDeal?.contactName,
      });
      
      // Get the call ID from the service (created by REST API)
      const newCallId = audioServiceRef.current.getCallId();
      setCallId(newCallId);
      
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: 'system',
          content: `Live call assistance started. Press **${hotkeyLabel}** to ask questions during the call.`,
          timestamp: new Date(),
          metadata: { status: 'live' },
        },
      ]);
    } catch (error) {
      console.error('Failed to start call:', error);
      setIsLiveCall(false);
      setCallPhase('before');
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: 'system',
          content: `Failed to connect: ${error.message}`,
          timestamp: new Date(),
          metadata: { status: 'error' },
        },
      ]);
    }
  }, [selectedDeal]);

  // Handle ending live call
  const handleEndCall = useCallback(() => {
    setIsLiveCall(false);
    setCallPhase('after');
    setSummaryLoading(true);
    
    // Send end call message and disconnect
    if (audioServiceRef.current?.isConnected()) {
      audioServiceRef.current.sendEndCall();
      audioServiceRef.current.disconnect();
    }
    
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: 'system',
        content: 'Call ended. Generating summary and extracting action items...',
        timestamp: new Date(),
        metadata: { status: 'ended' },
      },
    ]);
  }, []);

  // Handle live query from push-to-talk
  const handleLiveQuery = useCallback((query) => {
    if (!query.trim()) return;
    
    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: 'user',
        content: query,
        timestamp: new Date(),
        metadata: { source: 'live_query' },
      },
    ]);
    
    // Send query through WebSocket
    if (audioServiceRef.current?.isConnected()) {
      audioServiceRef.current.sendQuery(query, selectedDeal?.id);
    }
  }, [selectedDeal]);

  // Add message to chat
  const addMessage = useCallback((message) => {
    setMessages((prev) => [...prev, { ...message, id: Date.now(), timestamp: new Date() }]);
  }, []);

  // Update context data
  const updateContextData = useCallback((newData) => {
    setContextData((prev) => ({ ...prev, ...newData }));
  }, []);

  // Handle adding new deal
  const handleAddDeal = useCallback((newDeal) => {
    setDeals((prev) => [...prev, newDeal]);
    // Auto-select the newly added deal
    setSelectedDeal(newDeal);
    setCallPhase('before');
    setIsLiveCall(false);
    setCallDuration(0);
    // Set welcome message for new deal
    setMessages([
      {
        id: Date.now(),
        type: 'assistant',
        content: `New deal **${newDeal.accountName}** has been added. I've automatically populated context from our knowledge base including similar deals, references, and expected questions. What would you like to focus on for the upcoming call with **${newDeal.contactName}**?`,
        timestamp: new Date(),
        metadata: { source: 'system' },
      },
    ]);
    // Update context with RAG-populated data
    if (newDeal.similarDeals || newDeal.expectedQuestions) {
      setContextData({
        similarDeals: newDeal.similarDeals || [],
        references: newDeal.credibleReferences || [],
        expectedQuestions: newDeal.expectedQuestions || [],
        talkingPoints: newDeal.suggestedTalkingPoints || [],
        actionItems: [],
      });
    }
  }, []);

  return (
    <div className={styles.appContainer}>
      {/* Left Sidebar */}
      <Sidebar
        deals={deals}
        selectedDeal={selectedDeal}
        onDealSelect={handleDealSelect}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onAddDealClick={() => setIsAddDealModalOpen(true)}
        activeNav={activeNav}
        onNavChange={setActiveNav}
      />

      {/* Main Content Area */}
      <div className={styles.mainArea}>
        {activeNav === 'calls' ? (
          <MyCalls deals={deals} />
        ) : (
          <>
            {/* Live Call Strip - shown during active call */}
            {isLiveCall && (
              <LiveCallStrip
                duration={callDuration}
                onEndCall={handleEndCall}
                customerName={selectedDeal?.contactName}
                connectionState={connectionState}
                isTranscribing={isTranscribing}
                onToggleTranscript={() => setShowTranscript(!showTranscript)}
                showTranscript={showTranscript}
              />
            )}

            {/* Chat Panel */}
            <ChatPanel
              messages={messages}
              onSendMessage={addMessage}
              selectedDeal={selectedDeal}
              callPhase={callPhase}
              isLiveCall={isLiveCall}
              onStartLiveCall={handleStartLiveCall}
              onEndCall={handleEndCall}
              onUpdateContext={updateContextData}
              onToggleContextPanel={() => setContextPanelVisible(!contextPanelVisible)}
              contextPanelVisible={contextPanelVisible}
              transcriptChunks={transcriptChunks}
              showTranscript={showTranscript}
              onLiveQuery={handleLiveQuery}
            />

            {/* Call Summary Panel - shown after call ends */}
            {callPhase === 'after' && (callSummary || summaryLoading) && (
              <CallSummaryPanel
                summary={callSummary}
                actionItems={contextData.actionItems}
                isLoading={summaryLoading}
                onActionItemUpdate={(itemId, updates) => {
                  setContextData((prev) => ({
                    ...prev,
                    actionItems: prev.actionItems.map((item) =>
                      item.id === itemId ? { ...item, ...updates } : item
                    ),
                  }));
                }}
              />
            )}
          </>
        )}
      </div>

      {/* Right Context Panel */}
      {contextPanelVisible && activeNav !== 'calls' && (
        <ContextPanel
          deal={selectedDeal}
          callPhase={callPhase}
          isLiveCall={isLiveCall}
          contextData={contextData}
          onStartLiveCall={handleStartLiveCall}
          onClose={() => setContextPanelVisible(false)}
        />
      )}

      {/* Add Deal Modal */}
      <AddDealModal
        isOpen={isAddDealModalOpen}
        onClose={() => setIsAddDealModalOpen(false)}
        onAddDeal={handleAddDeal}
      />

      {/* Architecture Modal */}
      <ArchitectureModal
        isOpen={isArchitectureModalOpen}
        onClose={() => setIsArchitectureModalOpen(false)}
      />

      {/* Architecture Link Footer */}
      <button
        className={styles.architectureLink}
        onClick={() => setIsArchitectureModalOpen(true)}
        title="View Architecture Diagram"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </svg>
        Architecture
      </button>
    </div>
  );
}

export default App;
