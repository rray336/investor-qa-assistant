import React, { useState } from 'react';

const AnswerCard = ({ answer }) => {
  const [showSources, setShowSources] = useState(false);

  if (!answer) return null;

  const getConfidenceClass = (confidence) => {
    if (confidence >= 75) return 'confidence-high';
    if (confidence >= 50) return 'confidence-medium';
    return 'confidence-low';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 75) return 'High';
    if (confidence >= 50) return 'Medium';
    return 'Low';
  };

  const formatAnswer = (answerText) => {
    if (!answerText) return '';
    
    // Split by lines and process each line
    const lines = answerText.split('\n');
    const formattedLines = lines.map((line, index) => {
      const trimmedLine = line.trim();
      
      if (!trimmedLine) {
        return <br key={index} />;
      }
      
      // Handle bullet points
      if (trimmedLine.startsWith('• ') || trimmedLine.startsWith('- ')) {
        return (
          <li key={index} style={{ marginBottom: '5px' }}>
            {trimmedLine.substring(2)}
          </li>
        );
      }
      
      // Regular paragraph
      return (
        <p key={index} style={{ margin: '10px 0' }}>
          {trimmedLine}
        </p>
      );
    });

    // Group consecutive list items
    const grouped = [];
    let currentList = [];
    
    formattedLines.forEach((element, index) => {
      if (element.type === 'li') {
        currentList.push(element);
      } else {
        if (currentList.length > 0) {
          grouped.push(
            <ul key={`list-${index}`} style={{ margin: '10px 0', paddingLeft: '20px' }}>
              {currentList}
            </ul>
          );
          currentList = [];
        }
        grouped.push(element);
      }
    });
    
    // Handle any remaining list items
    if (currentList.length > 0) {
      grouped.push(
        <ul key="final-list" style={{ margin: '10px 0', paddingLeft: '20px' }}>
          {currentList}
        </ul>
      );
    }
    
    return grouped;
  };

  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '20px',
      marginTop: '20px',
      backgroundColor: '#f9f9f9'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '15px'
      }}>
        <h3 style={{ 
          margin: 0, 
          color: '#2c3e50',
          fontSize: '18px'
        }}>
          💬 Answer
        </h3>
        
        <span className={`confidence-score ${getConfidenceClass(answer.confidence)}`}>
          {getConfidenceLabel(answer.confidence)} ({answer.confidence}%)
        </span>
      </div>

      <div style={{
        fontSize: '14px',
        lineHeight: '1.6',
        color: '#2c3e50',
        marginBottom: '15px'
      }}>
        {formatAnswer(answer.answer)}
      </div>

      {answer.reasoning && (
        <div style={{
          fontSize: '13px',
          color: '#666',
          fontStyle: 'italic',
          marginBottom: '15px',
          padding: '10px',
          backgroundColor: '#f0f0f0',
          borderRadius: '4px',
          borderLeft: '3px solid #3498db'
        }}>
          <strong>Reasoning:</strong> {answer.reasoning}
        </div>
      )}

      <div style={{
        borderTop: '1px solid #ddd',
        paddingTop: '15px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ fontSize: '12px', color: '#666' }}>
          📊 Based on {answer.chunks_found || 0} document sections
        </div>

        {answer.sources && answer.sources.length > 0 && (
          <button
            onClick={() => setShowSources(!showSources)}
            className="btn secondary"
            style={{ fontSize: '12px', padding: '5px 10px' }}
          >
            {showSources ? 'Hide Sources' : 'Show Sources'}
          </button>
        )}
      </div>

      {showSources && answer.sources && answer.sources.length > 0 && (
        <div style={{
          marginTop: '15px',
          borderTop: '1px solid #ddd',
          paddingTop: '15px'
        }}>
          <h4 style={{ 
            fontSize: '14px', 
            margin: '0 0 10px 0',
            color: '#2c3e50'
          }}>
            📑 Sources:
          </h4>
          
          {answer.sources.map((source, index) => (
            <div key={index} style={{
              padding: '10px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              marginBottom: '8px',
              fontSize: '12px'
            }}>
              <div style={{ 
                fontWeight: 'bold', 
                marginBottom: '5px',
                color: '#2c3e50'
              }}>
                📄 {source.filename}
                <span style={{ 
                  marginLeft: '10px',
                  fontWeight: 'normal',
                  color: '#666'
                }}>
                  (Relevance: {source.relevance_score}%)
                </span>
              </div>
              
              <div style={{ 
                color: '#555',
                fontStyle: 'italic',
                lineHeight: '1.4'
              }}>
                "{source.preview}"
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{
        fontSize: '11px',
        color: '#999',
        textAlign: 'center',
        marginTop: '10px'
      }}>
        🤖 Generated by Claude AI
      </div>
    </div>
  );
};

export default AnswerCard;