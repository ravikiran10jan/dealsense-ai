import React from 'react';
import styles from './TabNavigation.module.css';

/**
 * TabNavigation Component
 * Three-tab navigation for Before/During/After Call flows
 */
const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'before', label: 'Before Call', icon: '📋' },
    { id: 'during', label: 'During Call', icon: '📞' },
    { id: 'after', label: 'After Call', icon: '✓' },
  ];

  return (
    <nav className={styles.navigation}>
      <div className={styles.tabsContainer}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
            onClick={() => onTabChange(tab.id)}
            aria-selected={activeTab === tab.id}
          >
            <span className={styles.icon}>{tab.icon}</span>
            <span className={styles.label}>{tab.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};

export default TabNavigation;
