import React, { useState } from 'react';

const ClearDataButton = ({ onClear }) => {
  const [isConfirming, setIsConfirming] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  const handleClick = () => {
    if (!isConfirming) {
      setIsConfirming(true);
      // Auto-cancel confirmation after 5 seconds
      setTimeout(() => {
        setIsConfirming(false);
      }, 5000);
    } else {
      handleConfirmedClear();
    }
  };

  const handleConfirmedClear = async () => {
    setIsClearing(true);
    try {
      await onClear();
      setIsConfirming(false);
    } catch (error) {
      console.error('Clear failed:', error);
    } finally {
      setIsClearing(false);
    }
  };

  const handleCancel = () => {
    setIsConfirming(false);
  };

  if (isConfirming) {
    return (
      <div style={{
        border: '2px solid #e74c3c',
        borderRadius: '8px',
        padding: '15px',
        backgroundColor: '#fdf2f2'
      }}>
        <div style={{
          marginBottom: '10px',
          fontSize: '14px',
          color: '#721c24',
          fontWeight: '500'
        }}>
          ⚠️ Are you sure?
        </div>
        
        <div style={{
          marginBottom: '15px',
          fontSize: '13px',
          color: '#721c24',
          lineHeight: '1.4'
        }}>
          This will permanently delete:
          <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
            <li>All uploaded PDF files</li>
            <li>All generated embeddings</li>
            <li>All document metadata</li>
          </ul>
          This action cannot be undone.
        </div>

        <div style={{
          display: 'flex',
          gap: '10px',
          justifyContent: 'center'
        }}>
          <button
            onClick={handleConfirmedClear}
            disabled={isClearing}
            className="btn danger"
            style={{ minWidth: '100px' }}
          >
            {isClearing ? 'Clearing...' : 'Yes, Clear All'}
          </button>
          
          <button
            onClick={handleCancel}
            disabled={isClearing}
            className="btn secondary"
            style={{ minWidth: '80px' }}
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ textAlign: 'center' }}>
      <button
        onClick={handleClick}
        className="btn danger"
        style={{
          fontSize: '13px',
          padding: '8px 16px'
        }}
      >
        🗑️ Clear All Data
      </button>
      
      <div style={{
        marginTop: '5px',
        fontSize: '11px',
        color: '#666'
      }}>
        Remove all PDFs and start fresh
      </div>
    </div>
  );
};

export default ClearDataButton;