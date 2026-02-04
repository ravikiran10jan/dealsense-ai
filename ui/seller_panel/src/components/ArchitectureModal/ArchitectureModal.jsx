import React from 'react';
import styles from './ArchitectureModal.module.css';
import architectureDiagram from '../../assets/architecture-diagram.svg';

const ArchitectureModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.overlay} onClick={handleBackdropClick}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2 className={styles.title}>DealSense AI Architecture</h2>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div className={styles.content}>
          <img 
            src={architectureDiagram} 
            alt="DealSense AI Architecture Diagram" 
            className={styles.diagram}
          />
        </div>
        <div className={styles.footer}>
          <span className={styles.badge}>Hackathon 2026</span>
          <span className={styles.techStack}>React + FastAPI + Azure OpenAI + FAISS</span>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureModal;
