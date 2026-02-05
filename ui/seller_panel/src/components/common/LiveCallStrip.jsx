import React, { useState, useEffect } from 'react';
import styles from './LiveCallStrip.module.css';

// Connection state enum
const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  ERROR: 'error',
};

const LiveCallStrip = ({
  duration: initialDuration = 0,
  onEndCall,
  customerName,
  connectionState = ConnectionState.CONNECTED,
  isTranscribing = false,
  onToggleTranscript,
  showTranscript = true,
}) => {
  const [duration, setDuration] = useState(initialDuration);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get connection status indicator
  const getConnectionStatus = () => {
    switch (connectionState) {
      case ConnectionState.CONNECTING:
        return { label: 'Connecting...', className: styles.connecting };
      case ConnectionState.CONNECTED:
        return { label: isTranscribing ? 'Transcribing' : 'Connected', className: styles.connected };
      case ConnectionState.ERROR:
        return { label: 'Connection Error', className: styles.error };
      default:
        return { label: 'Disconnected', className: styles.disconnected };
    }
  };

  const status = getConnectionStatus();

  return (
    <div className={styles.liveStrip}>
      <div className={styles.left}>
        {/* Live Indicator with Recording */}
        <div className={styles.liveIndicator}>
          <span className={`${styles.liveDot} ${isTranscribing ? styles.recording : ''}`}></span>
          <span className={styles.liveText}>LIVE</span>
        </div>
        
        {/* Duration */}
        <span className={styles.duration}>{formatDuration(duration)}</span>
        
        {/* Connection Status */}
        <div className={`${styles.connectionStatus} ${status.className}`}>
          <span className={styles.statusDot}></span>
          <span className={styles.statusText}>{status.label}</span>
        </div>
        
        <span className={styles.separator}>|</span>
        <span className={styles.customerName}>Call with {customerName}</span>
      </div>
      
      <div className={styles.right}>
        {/* Transcript Toggle Button */}
        {onToggleTranscript && (
          <button
            className={`${styles.controlBtn} ${showTranscript ? styles.active : ''}`}
            onClick={onToggleTranscript}
            title={showTranscript ? 'Hide Transcript' : 'Show Transcript'}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </button>
        )}
        
        {/* Mute Button */}
        <button
          className={`${styles.controlBtn} ${isMuted ? styles.muted : ''}`}
          onClick={() => setIsMuted(!isMuted)}
          title={isMuted ? 'Unmute' : 'Mute'}
        >
          {isMuted ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="1" y1="1" x2="23" y2="23" />
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6" />
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
          )}
        </button>
        
        {/* Hotkey Hint */}
        <div className={styles.hotkeyHint}>
          <kbd>Shift</kbd>+<kbd>Space</kbd> to ask
        </div>
        
        {/* End Call Button */}
        <button className={styles.endCallBtn} onClick={onEndCall}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
          End Call
        </button>
      </div>
    </div>
  );
};

export default LiveCallStrip;
