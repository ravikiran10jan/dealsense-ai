import React, { useState } from 'react';
import './styles/globals.css';
import styles from './App.module.css';
import Header from './components/Header/Header';
import TabNavigation from './components/Navigation/TabNavigation';
import BeforeCall from './components/BeforeCall/BeforeCall';
import DuringCall from './components/DuringCall/DuringCall';
import AfterCall from './components/AfterCall/AfterCall';

/**
 * Main App Component
 * Orchestrates tab navigation and displays appropriate content
 * 
 * LAYOUT:
 * ├─ Header (Fixed)
 * ├─ TabNavigation (Fixed)
 * └─ Tab Content (Dynamic)
 *    ├─ BeforeCall
 *    ├─ DuringCall
 *    └─ AfterCall
 */
function App() {
  const [activeTab, setActiveTab] = useState('before');

  // Render active tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'before':
        return <BeforeCall />;
      case 'during':
        return <DuringCall />;
      case 'after':
        return <AfterCall />;
      default:
        return <BeforeCall />;
    }
  };

  return (
    <div className={styles.appContainer}>
      <Header />
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className={styles.mainContent}>
        {renderTabContent()}
      </main>
      <footer className={styles.footer}>
        <p>&copy; 2026 DealSense AI - Sales Intelligence Platform</p>
      </footer>
    </div>
  );
}

export default App;
