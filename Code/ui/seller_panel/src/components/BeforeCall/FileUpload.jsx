import React, { useState } from 'react';
import styles from './FileUpload.module.css';

/**
 * FileUpload Component
 * Handles file and directory selection
 * Mock implementation - no actual file processing
 */
const FileUpload = ({ onFileSelect }) => {
  const [fileName, setFileName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showReport, setShowReport] = useState(false);

  const allowedExtensions = ['xlsx', 'xls', 'csv', 'pdf', 'json', 'txt', 'doc', 'docx'];

  const isSupported = (name) => {
    if (!name || !name.includes('.')) return false;
    const ext = name.split('.').pop().toLowerCase();
    return allowedExtensions.includes(ext);
  };

  const sendTelemetry = (payload) => {
    const base = {
      timestamp: new Date().toISOString(),
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
      platform: typeof navigator !== 'undefined' ? navigator.platform : 'unknown',
      url: typeof window !== 'undefined' ? window.location.href : '',
      ...payload,
    };
    try {
      if (typeof window !== 'undefined' && typeof window.__sendTelemetry === 'function') {
        // user-provided telemetry hook
        window.__sendTelemetry(base);
      } else if (typeof window !== 'undefined') {
        // emit a CustomEvent so consuming apps can listen
        window.dispatchEvent(new CustomEvent('fileUploadTelemetry', { detail: base }));
        // fallback to console for debugging
        // use debug so it can be filtered in production tooling
        // eslint-disable-next-line no-console
        console.debug('fileUploadTelemetry', base);
      } else {
        // eslint-disable-next-line no-console
        console.debug('fileUploadTelemetry', base);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.debug('Telemetry error', err);
    }
  };

  const handleFileChange = (e) => {
    setErrorMsg('');
    const file = e.target.files?.[0];
    if (file) {
      const supported = isSupported(file.name);
      // telemetry: single file selection
      sendTelemetry({ event: 'file_input_change', type: 'file', supported, file: { name: file.name, size: file.size, mime: file.type } });
      if (!supported) {
        setFileName('');
        setErrorMsg(`Unsupported file type. Supported: ${allowedExtensions.join(', ').toUpperCase()}`);
        if (onFileSelect) onFileSelect(null);
        return;
      }
      // success
      setFileName(file.name);
      if (onFileSelect) {
        onFileSelect({ name: file.name, type: 'file' });
      }
    }
  };

  const handleDirectoryChange = (e) => {
    setErrorMsg('');
    const files = Array.from(e.target.files || []);
    if (files && files.length > 0) {
      const filesWithSupport = files.map((f) => ({ name: f.name, size: f.size, mime: f.type, supported: isSupported(f.name) }));
      const supported = filesWithSupport.filter((f) => f.supported);
      // telemetry: directory selection summary
      sendTelemetry({ event: 'file_input_change', type: 'directory', totalFiles: files.length, supportedCount: supported.length, files: filesWithSupport.slice(0, 20) });
      if (supported.length === 0) {
        setFileName('');
        setErrorMsg(`No supported files found in folder. Supported: ${allowedExtensions.join(', ').toUpperCase()}`);
        if (onFileSelect) onFileSelect(null);
        return;
      }
      setFileName(`${supported.length} files selected`);
      if (onFileSelect) {
        onFileSelect({ name: `${supported.length} files selected`, type: 'directory', count: supported.length });
      }
    }
  };

  const handleAnalyze = () => {
    if (fileName) {
      setIsLoading(true);
      // Simulate loading
      setTimeout(() => {
        setIsLoading(false);
        setShowReport(true);
      }, 1500);
    }
  };

  return (
    <div className={styles.container}>
      <h2>Upload Sales Data</h2>

      <div className={styles.uploadSection}>
        <div className={styles.uploadCard}>
          <div className={styles.uploadIcon}>📁</div>
          <h3>Select File</h3>
          <p>Choose a single file to analyze</p>
          <label className={styles.fileInput}>
            <input
              type="file"
                onChange={handleFileChange}
                accept=".xlsx,.xls,.csv,.pdf,.json,.txt,.doc,.docx"
            />
            <span className={styles.buttonLabel}>Choose File</span>
          </label>
        </div>

        <div className={styles.divider}>or</div>

        <div className={styles.uploadCard}>
          <div className={styles.uploadIcon}>📂</div>
          <h3>Select Directory</h3>
          <p>Choose multiple files from a folder</p>
          <label className={styles.fileInput}>
            <input
              type="file"
              onChange={handleDirectoryChange}
              multiple
              webkitdirectory="true"
              accept=".xlsx,.xls,.csv,.pdf,.json,.txt,.doc,.docx"
            />
            <span className={styles.buttonLabel}>Choose Directory</span>
          </label>
        </div>
      </div>

      {fileName && (
        <div className={styles.selectedFile}>
          <span className={styles.fileIcon}>✓</span>
          <span className={styles.fileName}>{fileName}</span>
        </div>
      )}

      {errorMsg && (
        <div className={styles.errorMessage} role="alert">
          {errorMsg}
        </div>
      )}

      <div className={styles.actionSection}>
        <button
          className={`${styles.analyzeButton} ${!fileName || errorMsg ? styles.disabled : ''}`}
          onClick={handleAnalyze}
          disabled={!fileName || isLoading || !!errorMsg}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Data'}
        </button>
        <p className={styles.hint}>
          Supported formats: Excel, CSV, PDF, JSON, TXT, DOC/DOCX
        </p>
      </div>

      {showReport && (
        <div className={styles.reportSection}>
          <h3>📊 Analysis Report</h3>
          <div className={styles.reportContent}>
            <div className={styles.reportCard}>
              <h4>Key Insights</h4>
              <ul className={styles.keyPoints}>
                <li>✓ Total Records Analyzed: <strong>2,450</strong></li>
                <li>✓ Data Quality Score: <strong>92.5%</strong></li>
                <li>✓ Average Deal Size: <strong>$125,000</strong></li>
                <li>✓ Win Rate: <strong>68%</strong></li>
                <li>✓ Sales Cycle Duration: <strong>45 days</strong></li>
              </ul>
            </div>

            <div className={styles.reportCard}>
              <h4>Market Analysis</h4>
              <ul className={styles.keyPoints}>
                <li>✓ Top Industry Sector: <strong>Technology (34%)</strong></li>
                <li>✓ Geographic Concentration: <strong>North America (58%)</strong></li>
                <li>✓ Growth Trend: <strong>+23% YoY</strong></li>
                <li>✓ Competitor Share: <strong>12% Market Impact</strong></li>
                <li>✓ Expansion Opportunity: <strong>Europe Region</strong></li>
              </ul>
            </div>

            <div className={styles.reportCard}>
              <h4>Recommendations</h4>
              <ul className={styles.keyPoints}>
                <li>→ Focus on high-value opportunities in Tech sector</li>
                <li>→ Expand sales team in West Coast region</li>
                <li>→ Implement account-based marketing strategy</li>
                <li>→ Accelerate deal closure in healthcare vertical</li>
                <li>→ Develop strategic partnerships with key integrators</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
