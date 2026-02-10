import React from 'react';
import styles from './Header.module.css';
import logo from '../../assets/dxc-mark.svg';

/**
 * Header Component
 * Main application header with branding and navigation
 */
const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <img src={logo} alt="DXC logo" className={styles.logoImg} />
          <div className={styles.brandText}>
            <h1 className={styles.appName}>DealSenseAI</h1>
          </div>
        </div>
        <div className={styles.info}>
          <span className={styles.user}>Sales Intelligence Team</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
