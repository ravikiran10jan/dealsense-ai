import React from 'react';
import styles from './Sidebar.module.css';
import logo from '../../assets/dxc-mark.svg';

const navItems = [
  { id: 'inbox', label: 'Inbox', icon: 'inbox' },
  { id: 'calls', label: 'My Calls', icon: 'phone' },
  { id: 'templates', label: 'Templates', icon: 'document' },
];

const stageColors = {
  Discovery: '#5B8DEF',
  Proposal: '#E8854A',
  Negotiation: '#0D9488',
  Closed: '#10B981',
};

const Sidebar = ({ deals, selectedDeal, onDealSelect, collapsed, onToggleCollapse, onAddDealClick, activeNav, onNavChange }) => {
  const handleNavClick = (navId) => {
    if (onNavChange) {
      onNavChange(navId);
    }
  };

  const renderIcon = (iconName) => {
    switch (iconName) {
      case 'inbox':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 12h-6l-2 3h-4l-2-3H2" />
            <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
          </svg>
        );
      case 'phone':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
        );
      case 'document':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      {/* Header / Logo */}
      <div className={styles.header}>
        <div className={styles.logoContainer}>
          <img src={logo} alt="DealSense AI" className={styles.logo} />
          {!collapsed && (
            <div className={styles.brandText}>
              <span className={styles.brandName}>DealSense AI</span>
              <span className={styles.brandTagline}>Sales Copilot</span>
            </div>
          )}
        </div>
        <button className={styles.collapseBtn} onClick={onToggleCollapse} title={collapsed ? 'Expand' : 'Collapse'}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {collapsed ? (
              <polyline points="9 18 15 12 9 6" />
            ) : (
              <polyline points="15 18 9 12 15 6" />
            )}
          </svg>
        </button>
      </div>

      {/* Navigation */}
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`${styles.navItem} ${activeNav === item.id ? styles.active : ''}`}
            onClick={() => handleNavClick(item.id)}
            title={collapsed ? item.label : undefined}
          >
            <span className={styles.navIcon}>{renderIcon(item.icon)}</span>
            {!collapsed && <span className={styles.navLabel}>{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Deals List */}
      {!collapsed && (
        <div className={styles.dealsSection}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>Active Deals</span>
            <div className={styles.sectionActions}>
              <span className={styles.dealCount}>{deals.length}</span>
              <button className={styles.addDealBtn} onClick={onAddDealClick} title="Add new deal">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </button>
            </div>
          </div>
          <div className={styles.dealsList}>
            {deals.map((deal) => (
              <button
                key={deal.id}
                className={`${styles.dealItem} ${selectedDeal?.id === deal.id ? styles.selected : ''}`}
                onClick={() => onDealSelect(deal)}
              >
                <div className={styles.dealHeader}>
                  <span className={styles.dealName}>{deal.accountName}</span>
                  <span
                    className={styles.dealStage}
                    style={{ backgroundColor: stageColors[deal.stage] || 'var(--color-text-muted)' }}
                  >
                    {deal.stage}
                  </span>
                </div>
                <div className={styles.dealMeta}>
                  <span className={styles.dealAmount}>{deal.dealAmount}</span>
                  <span className={styles.dealDate}>
                    {deal.nextCallDate} at {deal.nextCallTime}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* User Section */}
      <div className={styles.userSection}>
        <div className={styles.userAvatar}>
          <span>RK</span>
        </div>
        {!collapsed && (
          <div className={styles.userInfo}>
            <span className={styles.userName}>Ravikiran</span>
            <span className={styles.userRole}>Sales Rep</span>
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
