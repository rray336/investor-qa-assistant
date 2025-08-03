import React, { useState, useEffect } from 'react';
import PDFUploader from './components/PDFUploader';
import QuestionBox from './components/QuestionBox';
import PDFList from './components/PDFList';
import AnswerCard from './components/AnswerCard';
import ClearDataButton from './components/ClearDataButton';
import api from './services/api';

function App() {
  const [pdfs, setPdfs] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load PDFs on component mount
  useEffect(() => {
    loadPDFs();
  }, []);

  const loadPDFs = async () => {
    try {
      const response = await api.get('/pdfs');
      setPdfs(response.data.pdfs || []);
    } catch (error) {
      console.error('Failed to load PDFs:', error);
      setError('Failed to load PDF list');
    }
  };

  const handlePDFsUploaded = (uploadResults) => {
    // Refresh PDF list after upload
    loadPDFs();
    
    // Show success message
    const successCount = uploadResults.filter(r => r.status === 'success').length;
    const totalCount = uploadResults.length;
    
    if (successCount === totalCount) {
      setError(null);
    } else {
      setError(`${successCount}/${totalCount} PDFs uploaded successfully`);
    }
  };

  const handleQuestionSubmit = async (question) => {
    setIsLoading(true);
    setError(null);
    setCurrentAnswer(null);

    try {
      const response = await api.post('/ask-question', { question });
      setCurrentAnswer(response.data);
    } catch (error) {
      console.error('Failed to get answer:', error);
      setError('Failed to process question. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearData = async () => {
    try {
      await api.delete('/clear-all');
      setPdfs([]);
      setCurrentAnswer(null);
      setError(null);
    } catch (error) {
      console.error('Failed to clear data:', error);
      setError('Failed to clear data. Please try again.');
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Investor Q&A Assistant</h1>
        <p>AI-powered document analysis for investor relations</p>
      </header>

      {error && (
        <div className={`alert ${error.includes('success') ? 'info' : 'error'}`}>
          {error}
        </div>
      )}

      <div className="main-content">
        <div className="card">
          <h2>📂 Upload Documents</h2>
          <PDFUploader onUploadComplete={handlePDFsUploaded} />
          
          <div style={{ marginTop: '20px' }}>
            <h3>Uploaded PDFs ({pdfs.length})</h3>
            <PDFList pdfs={pdfs} />
          </div>

          <div style={{ marginTop: '20px' }}>
            <ClearDataButton onClear={handleClearData} />
          </div>
        </div>

        <div className="card">
          <h2>❓ Ask a Question</h2>
          <QuestionBox 
            onSubmit={handleQuestionSubmit} 
            isLoading={isLoading}
            disabled={pdfs.length === 0}
          />

          {isLoading && (
            <div className="loading">
              Processing your question...
            </div>
          )}

          {currentAnswer && (
            <AnswerCard answer={currentAnswer} />
          )}
        </div>
      </div>

      <footer style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
        <p>Powered by Claude AI • Built for Investor Relations</p>
      </footer>
    </div>
  );
}

export default App;