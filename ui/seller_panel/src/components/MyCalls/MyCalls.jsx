import React from 'react';
import styles from './MyCalls.module.css';

/**
 * MyCalls Component
 * Displays call history and upcoming calls based on deals data
 */
const MyCalls = ({ deals }) => {
  // Generate dummy call data from deals
  const generateCallsFromDeals = () => {
    const calls = [];
    
    deals.forEach((deal, index) => {
      // Upcoming call
      calls.push({
        id: `upcoming-${deal.id}`,
        type: 'upcoming',
        dealName: deal.accountName,
        contactName: deal.contactName,
        contactRole: deal.contactRole,
        date: deal.nextCallDate,
        time: deal.nextCallTime,
        duration: null,
        stage: deal.stage,
        dealAmount: deal.dealAmount,
        notes: `Scheduled ${deal.stage.toLowerCase()} call`,
      });

      // Add some past calls for the first few deals
      if (index < 2) {
        const pastDates = ['2026-01-28', '2026-01-20', '2026-01-15'];
        const outcomes = ['Follow-up scheduled', 'Proposal requested', 'Discovery completed'];
        const durations = ['32 min', '45 min', '28 min'];
        
        pastDates.forEach((date, i) => {
          if (i <= index) {
            calls.push({
              id: `past-${deal.id}-${i}`,
              type: 'completed',
              dealName: deal.accountName,
              contactName: deal.contactName,
              contactRole: deal.contactRole,
              date: date,
              time: '10:00 AM',
              duration: durations[i],
              stage: deal.stage,
              dealAmount: deal.dealAmount,
              notes: outcomes[i],
            });
          }
        });
      }
    });

    // Sort by date (upcoming first, then past)
    return calls.sort((a, b) => {
      if (a.type === 'upcoming' && b.type !== 'upcoming') return -1;
      if (a.type !== 'upcoming' && b.type === 'upcoming') return 1;
      return new Date(b.date) - new Date(a.date);
    });
  };

  const calls = generateCallsFromDeals();
  const upcomingCalls = calls.filter(c => c.type === 'upcoming');
  const completedCalls = calls.filter(c => c.type === 'completed');

  const stageColors = {
    Discovery: '#5B8DEF',
    Proposal: '#E8854A',
    Negotiation: '#0D9488',
    Closed: '#10B981',
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (dateStr === today.toISOString().split('T')[0]) {
      return 'Today';
    } else if (dateStr === tomorrow.toISOString().split('T')[0]) {
      return 'Tomorrow';
    }
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>My Calls</h1>
        <p className={styles.subtitle}>Track your scheduled and completed sales calls</p>
      </div>

      <div className={styles.columnsWrapper}>
        {/* Upcoming Calls Section */}
        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>
              <span className={styles.iconUpcoming}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
              </span>
              Upcoming
            </h2>
            <span className={styles.callCount}>{upcomingCalls.length}</span>
          </div>
          
          <div className={styles.callsList}>
            {upcomingCalls.length > 0 ? (
              upcomingCalls.map((call) => (
                <div key={call.id} className={`${styles.callCard} ${styles.upcoming}`}>
                  <div className={styles.callHeader}>
                    <div className={styles.callInfo}>
                      <h3 className={styles.dealName}>{call.dealName}</h3>
                      <span 
                        className={styles.stageBadge}
                        style={{ backgroundColor: stageColors[call.stage] }}
                      >
                        {call.stage}
                      </span>
                    </div>
                    <span className={styles.dealAmount}>{call.dealAmount}</span>
                  </div>
                  
                  <div className={styles.contactInfo}>
                    <span className={styles.contactName}>{call.contactName}</span>
                    <span className={styles.contactRole}>{call.contactRole}</span>
                  </div>
                  
                  <div className={styles.callMeta}>
                    <div className={styles.dateTime}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                      </svg>
                      <span>{formatDate(call.date)}</span>
                      <span className={styles.time}>{call.time}</span>
                    </div>
                    <button className={styles.joinButton}>
                      Prepare
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className={styles.emptyState}>No upcoming calls</div>
            )}
          </div>
        </section>

        {/* Completed Calls Section */}
        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>
              <span className={styles.iconCompleted}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </span>
              Completed
            </h2>
            <span className={styles.callCount}>{completedCalls.length}</span>
          </div>
          
          <div className={styles.callsList}>
            {completedCalls.length > 0 ? (
              completedCalls.map((call) => (
                <div key={call.id} className={`${styles.callCard} ${styles.completed}`}>
                  <div className={styles.callHeader}>
                    <div className={styles.callInfo}>
                      <h3 className={styles.dealName}>{call.dealName}</h3>
                      <span 
                        className={styles.stageBadge}
                        style={{ backgroundColor: stageColors[call.stage] }}
                      >
                        {call.stage}
                      </span>
                    </div>
                    <span className={styles.dealAmount}>{call.dealAmount}</span>
                  </div>
                  
                  <div className={styles.contactInfo}>
                    <span className={styles.contactName}>{call.contactName}</span>
                    <span className={styles.contactRole}>{call.contactRole}</span>
                  </div>
                  
                  <div className={styles.callMeta}>
                    <div className={styles.dateTime}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                      </svg>
                      <span>{formatDate(call.date)}</span>
                    </div>
                    <div className={styles.duration}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <polyline points="12 6 12 12 16 14" />
                      </svg>
                      <span>{call.duration}</span>
                    </div>
                    <span className={styles.outcome}>{call.notes}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className={styles.emptyState}>No completed calls yet</div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default MyCalls;
