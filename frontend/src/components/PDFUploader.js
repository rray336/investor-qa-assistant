import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadPDFs } from '../services/api';

const PDFUploader = ({ onUploadComplete, chunkingSettings }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [confidentialFlags, setConfidentialFlags] = useState([]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true,
    onDrop: (acceptedFiles) => {
      setSelectedFiles(acceptedFiles);
      // Initialize confidential flags to false for all files
      setConfidentialFlags(new Array(acceptedFiles.length).fill(false));
    }
  });

  const handleConfidentialToggle = (index) => {
    const newFlags = [...confidentialFlags];
    newFlags[index] = !newFlags[index];
    setConfidentialFlags(newFlags);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    try {
      const response = await uploadPDFs(
        selectedFiles, 
        confidentialFlags,
        chunkingSettings
      );
      
      if (onUploadComplete) {
        onUploadComplete(response.data.results);
      }
      
      // Clear selected files after successful upload
      setSelectedFiles([]);
      setConfidentialFlags([]);
    } catch (error) {
      console.error('Upload failed:', error);
      // Error will be handled by parent component
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = (index) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const newFlags = confidentialFlags.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    setConfidentialFlags(newFlags);
  };

  const dropzoneStyle = {
    border: '2px dashed #ccc',
    borderRadius: '8px',
    padding: '20px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: isDragActive ? '#f0f8ff' : '#fafafa',
    borderColor: isDragActive ? '#3498db' : '#ccc',
    transition: 'all 0.2s ease'
  };

  return (
    <div>
      <div {...getRootProps()} style={dropzoneStyle}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the PDFs here...</p>
        ) : (
          <div>
            <p>📁 Drag & drop PDF files here, or click to select</p>
            <p style={{ fontSize: '12px', color: '#666' }}>
              Multiple files supported
            </p>
          </div>
        )}
      </div>

      {selectedFiles.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h4>Selected Files ({selectedFiles.length})</h4>
          
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {selectedFiles.map((file, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px',
                border: '1px solid #eee',
                borderRadius: '4px',
                marginBottom: '5px',
                backgroundColor: '#f9f9f9'
              }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ 
                    fontSize: '14px', 
                    fontWeight: '500',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {file.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <label style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}>
                    <input
                      type="checkbox"
                      checked={confidentialFlags[index] || false}
                      onChange={() => handleConfidentialToggle(index)}
                      style={{ marginRight: '5px' }}
                    />
                    Confidential
                  </label>

                  <button
                    onClick={() => handleRemoveFile(index)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#e74c3c',
                      cursor: 'pointer',
                      fontSize: '16px',
                      padding: '2px'
                    }}
                    title="Remove file"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '15px', textAlign: 'center' }}>
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="btn"
              style={{ minWidth: '120px' }}
            >
              {isUploading ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </div>
      )}

      {selectedFiles.some((_, index) => confidentialFlags[index]) && (
        <div className="alert info" style={{ marginTop: '10px' }}>
          📄 Confidential files will be stored but not included in AI analysis for privacy protection.
        </div>
      )}
    </div>
  );
};

export default PDFUploader;