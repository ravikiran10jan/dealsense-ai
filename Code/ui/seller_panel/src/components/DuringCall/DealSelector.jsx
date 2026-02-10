import React, { useState } from 'react';
import styles from './DealSelector.module.css';

/**
 * DealSelector Component
 * Dropdown to select a deal for live discussion
 */
const DealSelector = ({ deals, selectedDeal, onDealChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (deal) => {
    onDealChange(deal);
    setIsOpen(false);
  };

  return (
    <div className={styles.container}>
      <label htmlFor="deal-select" className={styles.label}>
        Select Deal for Discussion
      </label>

      <div className={styles.dropdownWrapper}>
        <button
          id="deal-select"
          className={styles.triggerButton}
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className={styles.selected}>
            {selectedDeal ? selectedDeal.title : 'Choose a deal...'}
          </span>
          <span className={`${styles.arrow} ${isOpen ? styles.open : ''}`}>
            ▼
          </span>
        </button>

        {isOpen && (
          <div className={styles.dropdownMenu}>
            {deals.map((deal) => (
              <button
                key={deal.id}
                className={`${styles.menuItem} ${
                  selectedDeal?.id === deal.id ? styles.active : ''
                }`}
                onClick={() => handleSelect(deal)}
              >
                <span className={styles.dealTitle}>{deal.title}</span>
                <span className={styles.dealValue}>{deal.dealValue}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DealSelector;
