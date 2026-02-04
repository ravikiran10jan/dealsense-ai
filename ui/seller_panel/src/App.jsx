import React, { useState, useCallback } from 'react';
import './styles/globals.css';
import styles from './App.module.css';
import Sidebar from './components/Sidebar/Sidebar';
import ChatPanel from './components/ChatPanel/ChatPanel';
import ContextPanel from './components/ContextPanel/ContextPanel';
import LiveCallStrip from './components/common/LiveCallStrip';
import AddDealModal from './components/AddDealModal/AddDealModal';

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
  const handleStartLiveCall = useCallback(() => {
    setIsLiveCall(true);
    setCallPhase('during');
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: 'system',
        content: 'Live call assistance started. I\'m listening and ready to help.',
        timestamp: new Date(),
        metadata: { status: 'live' },
      },
    ]);
  }, []);

  // Handle ending live call
  const handleEndCall = useCallback(() => {
    setIsLiveCall(false);
    setCallPhase('after');
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: 'system',
        content: 'Call ended. Would you like me to generate a summary and next steps?',
        timestamp: new Date(),
        metadata: { status: 'ended' },
      },
    ]);
  }, []);

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
      />

      {/* Main Content Area */}
      <div className={styles.mainArea}>
        {/* Live Call Strip - shown during active call */}
        {isLiveCall && (
          <LiveCallStrip
            duration={callDuration}
            onEndCall={handleEndCall}
            customerName={selectedDeal?.contactName}
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
        />
      </div>

      {/* Right Context Panel */}
      {contextPanelVisible && (
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
    </div>
  );
}

export default App;
