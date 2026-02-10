import React, { useState } from 'react';
import styles from './LiveNotes.module.css';

/**
 * LiveNotes Component
 * Textarea for capturing notes during the sales call
 * Mock save implementation
 */
const LiveNotes = () => {
  const [notes, setNotes] = useState('');
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    // Mock save
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
    }, 3000);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3>Live Call Notes</h3>
        <span className={styles.wordCount}>{notes.length} characters</span>
      </div>

      <textarea
        className={styles.noteInput}
        placeholder="📝 Take notes during the call...

Talking points covered:
- 
- 

Client objections:
- 

Next steps:
- "
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      />

      <div className={styles.actions}>
        <button className={styles.saveButton} onClick={handleSave}>
          {isSaved ? '✓ Saved' : 'Save Notes'}
        </button>
        <p className={styles.hint}>
          Notes are auto-saved every 30 seconds
        </p>
      </div>

      {isSaved && <div className={styles.confirmMessage}>Notes saved successfully!</div>}
    </div>
  );
};

export default LiveNotes;
