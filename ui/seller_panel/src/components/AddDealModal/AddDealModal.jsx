import React, { useState } from 'react';
import styles from './AddDealModal.module.css';

const stageOptions = ['Discovery', 'Proposal', 'Negotiation', 'Closed'];
const industryOptions = [
  'Banking - Trade Finance',
  'Banking - Retail',
  'Banking - Corporate',
  'Insurance',
  'Capital Markets',
  'Fintech',
];

const AddDealModal = ({ isOpen, onClose, onAddDeal }) => {
  const [formData, setFormData] = useState({
    accountName: '',
    stage: 'Discovery',
    nextCallDate: '',
    nextCallTime: '',
    dealAmount: '',
    contactName: '',
    contactRole: '',
    industry: 'Banking - Trade Finance',
    description: '',
    notes: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/api/deals/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          additionalContacts: [],
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create deal: ${response.statusText}`);
      }

      const newDeal = await response.json();
      onAddDeal(newDeal);
      
      // Reset form
      setFormData({
        accountName: '',
        stage: 'Discovery',
        nextCallDate: '',
        nextCallTime: '',
        dealAmount: '',
        contactName: '',
        contactRole: '',
        industry: 'Banking - Trade Finance',
        description: '',
        notes: '',
      });
      
      onClose();
    } catch (err) {
      console.error('Error creating deal:', err);
      setError(err.message || 'Failed to create deal. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>Add New Deal</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}
          
          <div className={styles.formGrid}>
            <div className={styles.formGroup}>
              <label className={styles.label}>Account Name *</label>
              <input
                type="text"
                name="accountName"
                value={formData.accountName}
                onChange={handleChange}
                className={styles.input}
                placeholder="e.g., ANZ Bank"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Industry *</label>
              <select
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                className={styles.select}
                required
              >
                {industryOptions.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Stage *</label>
              <select
                name="stage"
                value={formData.stage}
                onChange={handleChange}
                className={styles.select}
                required
              >
                {stageOptions.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Deal Amount *</label>
              <input
                type="text"
                name="dealAmount"
                value={formData.dealAmount}
                onChange={handleChange}
                className={styles.input}
                placeholder="e.g., $4.5M"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Next Call Date *</label>
              <input
                type="date"
                name="nextCallDate"
                value={formData.nextCallDate}
                onChange={handleChange}
                className={styles.input}
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Next Call Time *</label>
              <input
                type="time"
                name="nextCallTime"
                value={formData.nextCallTime}
                onChange={handleChange}
                className={styles.input}
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Contact Name *</label>
              <input
                type="text"
                name="contactName"
                value={formData.contactName}
                onChange={handleChange}
                className={styles.input}
                placeholder="e.g., David Chen"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Contact Role *</label>
              <input
                type="text"
                name="contactRole"
                value={formData.contactRole}
                onChange={handleChange}
                className={styles.input}
                placeholder="e.g., Head of Trade Finance"
                required
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Description *</label>
            <input
              type="text"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className={styles.input}
              placeholder="e.g., Trade Finance Transformation Journey"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>
              Notes / Context
              <span className={styles.labelHint}>(will be indexed for RAG search)</span>
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              className={styles.textarea}
              placeholder="Add any relevant context, requirements, or notes about this deal. This information will be stored in the knowledge base for future reference."
              rows={4}
            />
          </div>

          <div className={styles.footer}>
            <button type="button" className={styles.cancelBtn} onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <span className={styles.spinner}></span>
                  Creating...
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                  Add Deal
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddDealModal;
