import React, { useState } from 'react';

const PDFList = ({ pdfs }) => {
  const [sortBy, setSortBy] = useState('upload_date');
  const [sortOrder, setSortOrder] = useState('desc');

  if (!pdfs || pdfs.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        padding: '20px',
        color: '#666',
        fontSize: '14px'
      }}>
        📄 No PDFs uploaded yet
      </div>
    );
  }

  // Sort PDFs
  const sortedPdfs = [...pdfs].sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];

    // Handle date sorting
    if (sortBy === 'upload_date') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }

    // Handle string sorting
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown date';
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown size';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  return (
    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
      {/* Sorting controls */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '10px',
        fontSize: '12px'
      }}>
        <button
          onClick={() => handleSort('filename')}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '4px 8px',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          Name {getSortIcon('filename')}
        </button>
        
        <button
          onClick={() => handleSort('upload_date')}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '4px 8px',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          Date {getSortIcon('upload_date')}
        </button>
        
        <button
          onClick={() => handleSort('chunk_count')}
          style={{
            background: 'none',
            border: '1px solid #ddd',
            padding: '4px 8px',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          Chunks {getSortIcon('chunk_count')}
        </button>
      </div>

      {/* PDF list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {sortedPdfs.map((pdf, index) => (
          <div key={pdf.id || index} style={{
            padding: '12px',
            border: '1px solid #e0e0e0',
            borderRadius: '6px',
            backgroundColor: pdf.is_confidential ? '#fff3e0' : '#f9f9f9',
            fontSize: '13px'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              marginBottom: '5px'
            }}>
              <div style={{
                fontWeight: '500',
                color: '#2c3e50',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '60%'
              }}>
                📄 {pdf.filename}
              </div>
              
              <div style={{ display: 'flex', gap: '5px', flexShrink: 0 }}>
                {pdf.is_confidential && (
                  <span style={{
                    background: '#ff9800',
                    color: 'white',
                    padding: '2px 6px',
                    borderRadius: '10px',
                    fontSize: '10px',
                    fontWeight: 'bold'
                  }}>
                    🔒 CONFIDENTIAL
                  </span>
                )}
                
                <span style={{
                  background: '#4caf50',
                  color: 'white',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  fontSize: '10px'
                }}>
                  {pdf.chunk_count} chunks
                </span>
              </div>
            </div>

            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              color: '#666',
              fontSize: '11px'
            }}>
              <span>
                📅 {formatDate(pdf.upload_date)}
              </span>
              
              {pdf.file_size && (
                <span>
                  💾 {formatFileSize(pdf.file_size)}
                </span>
              )}
            </div>

            {pdf.is_confidential && (
              <div style={{
                marginTop: '5px',
                fontSize: '10px',
                color: '#e65100',
                fontStyle: 'italic'
              }}>
                ⚠️ Not included in AI analysis for privacy protection
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div style={{
        marginTop: '10px',
        padding: '8px',
        backgroundColor: '#f0f0f0',
        borderRadius: '4px',
        fontSize: '11px',
        color: '#666',
        textAlign: 'center'
      }}>
        📋 Total: {pdfs.length} PDFs • 
        🔒 Confidential: {pdfs.filter(p => p.is_confidential).length} • 
        🧠 Analyzed: {pdfs.filter(p => !p.is_confidential).length}
      </div>
    </div>
  );
};

export default PDFList;