import React, { useState } from 'react';
import styles from './DuringCall.module.css';
import DealSelector from './DealSelector';
import DealDetailsPanel from './DealDetailsPanel';
import LiveNotes from './LiveNotes';
import { mockDeals } from '../../data/mockData';

/**
 * DuringCall Tab Component
 * Live assistance during sales call with deal reference and note-taking
 */
const DuringCall = () => {
  const [selectedDeal, setSelectedDeal] = useState(mockDeals[0]);

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <h1>📞 During Call: Live Assistance</h1>
        <p>
          Reference deal insights, track objections, and capture call notes in real-time.
        </p>
      </div>

      <div className={styles.mainContent}>
        <div className={styles.leftPanel}>
          <DealSelector
            deals={mockDeals}
            selectedDeal={selectedDeal}
            onDealChange={setSelectedDeal}
          />
          <DealDetailsPanel deal={selectedDeal} />
        </div>

        <div className={styles.rightPanel}>
          <LiveNotes />
        </div>
      </div>
    </div>
  );
};

export default DuringCall;
