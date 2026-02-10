import React, { useState, useRef } from 'react';
import styles from './ChatInput.module.css';

const ChatInput = ({ onSend, disabled, placeholder, isLiveCall }) => {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSend(value.trim());
      setValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInput = (e) => {
    setValue(e.target.value);
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
  };

  return (
    <form className={styles.inputContainer} onSubmit={handleSubmit}>
      <div className={styles.inputWrapper}>
        <button type="button" className={styles.attachBtn} title="Attach file">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
          </svg>
        </button>
        <textarea
          ref={textareaRef}
          className={styles.input}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
        />
        <button
          type="submit"
          className={`${styles.sendBtn} ${value.trim() ? styles.active : ''}`}
          disabled={disabled || !value.trim()}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
      {isLiveCall && (
        <div className={styles.liveIndicator}>
          <span className={styles.liveDot}></span>
          <span>Live call in progress - I'm listening and ready to help</span>
        </div>
      )}
    </form>
  );
};

export default ChatInput;
