import React, { useState } from 'react';

const QuestionBox = ({ onSubmit, isLoading, disabled }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || isLoading || disabled) return;
    
    onSubmit(question.trim());
    setQuestion(''); // Clear the input after submission
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Sample questions for inspiration
  const sampleQuestions = [
    "What are the top 3 questions asked by analysts ranked by length of management response. List a cleaned up version of the question. Provide management's response in paragraph form - insert ... to connect points",
     "Summarize main points from these transcripts."
  ];

  const handleSampleClick = (sampleQuestion) => {
    setQuestion(sampleQuestion);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="question">
            Your Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={disabled 
              ? "Please upload PDFs first..." 
              : "Ask a question about your uploaded documents..."
            }
            disabled={disabled || isLoading}
            rows={3}
            style={{
              resize: 'vertical',
              minHeight: '80px'
            }}
          />
          <div style={{ 
            fontSize: '12px', 
            color: '#666', 
            marginTop: '5px' 
          }}>
            Press Enter to submit, Shift+Enter for new line
          </div>
        </div>

        <button
          type="submit"
          className="btn"
          disabled={!question.trim() || isLoading || disabled}
          style={{ width: '100%' }}
        >
          {isLoading ? 'Processing...' : 'Ask Question'}
        </button>
      </form>

      {!disabled && (
        <div style={{ marginTop: '20px' }}>
          <h4 style={{ 
            fontSize: '14px', 
            marginBottom: '10px', 
            color: '#666' 
          }}>
            💡 Sample Questions:
          </h4>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {sampleQuestions.map((sample, index) => (
              <button
                key={index}
                onClick={() => handleSampleClick(sample)}
                disabled={isLoading}
                style={{
                  background: 'none',
                  border: '1px solid #ddd',
                  padding: '8px 12px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '13px',
                  color: '#555',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isLoading) {
                    e.target.style.backgroundColor = '#f8f9fa';
                    e.target.style.borderColor = '#3498db';
                  }
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.borderColor = '#ddd';
                }}
              >
                {sample}
              </button>
            ))}
          </div>
        </div>
      )}

      {disabled && (
        <div className="alert info" style={{ marginTop: '15px' }}>
          📤 Upload some PDF documents first to start asking questions.
        </div>
      )}
    </div>
  );
};

export default QuestionBox;