import React, { useState, useEffect } from 'react';

const SettingsPanel = ({ isOpen, onClose, onSettingsChange }) => {
  const [settings, setSettings] = useState({
    chunkSize: 4000,
    chunkOverlap: 400,
    maxChunks: 20,
    aiModel: 'claude',
    processingMethod: 'embeddings'
  });

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('chunkingSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chunkingSettings', JSON.stringify(settings));
    // Notify parent component of settings change
    if (onSettingsChange) {
      onSettingsChange(settings);
    }
  }, [settings, onSettingsChange]);

  const handleInputChange = (field, value) => {
    if (field === 'aiModel') {
      setSettings(prev => ({
        ...prev,
        [field]: value
      }));
    } else {
      const numValue = parseInt(value, 10);
      if (!isNaN(numValue) && numValue > 0) {
        setSettings(prev => ({
          ...prev,
          [field]: numValue
        }));
      }
    }
  };

  const resetToDefaults = () => {
    setSettings({
      chunkSize: 4000,
      chunkOverlap: 400,
      maxChunks: 20,
      aiModel: 'claude',
      processingMethod: 'embeddings'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-panel">
        <div className="settings-header">
          <h3>⚙️ AI & Chunking Settings</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="settings-content">
          <p className="settings-description">
            Choose your AI model and adjust how PDF documents are split for analysis. Larger chunks provide more context but may be less precise.
          </p>
          {/* Phase 1: Claude + OpenAI only */}

          <div className="setting-group">
            <label htmlFor="aiModel">
              <span className="setting-label">AI Model</span>
              <span className="setting-description">Choose the AI model for question answering</span>
            </label>
            <select
              id="aiModel"
              value={settings.aiModel}
              onChange={(e) => handleInputChange('aiModel', e.target.value)}
            >
              <option value="claude">Claude 3.5 Sonnet (Default)</option>
              <option value="openai-gpt4">OpenAI GPT-4</option>
              <option value="openai-gpt35">OpenAI GPT-3.5 Turbo</option>
              <option value="gemini-pro">Google Gemini 2.5 Flash</option>
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="chunkSize">
              <span className="setting-label">Chunk Size (characters)</span>
              <span className="setting-description">Size of each text chunk</span>
            </label>
            <input
              id="chunkSize"
              type="number"
              min="1000"
              max="100000"
              step="100"
              value={settings.chunkSize}
              onChange={(e) => handleInputChange('chunkSize', e.target.value)}
            />
          </div>

          <div className="setting-group">
            <label htmlFor="chunkOverlap">
              <span className="setting-label">Chunk Overlap (characters)</span>
              <span className="setting-description">Overlap between adjacent chunks</span>
            </label>
            <input
              id="chunkOverlap"
              type="number"
              min="0"
              max="1000"
              step="50"
              value={settings.chunkOverlap}
              onChange={(e) => handleInputChange('chunkOverlap', e.target.value)}
            />
          </div>

          <div className="setting-group">
            <label htmlFor="maxChunks">
              <span className="setting-label">Max Chunks Retrieved</span>
              <span className="setting-description">Maximum chunks to use for each question</span>
            </label>
            <input
              id="maxChunks"
              type="number"
              min="5"
              max="50"
              step="1"
              value={settings.maxChunks}
              onChange={(e) => handleInputChange('maxChunks', e.target.value)}
            />
          </div>

          <div className="setting-group">
            <label>
              <span className="setting-label">Processing Method</span>
              <span className="setting-description">Choose how to process PDF content</span>
            </label>
            
            <div className="toggle-group" style={{display: 'flex', gap: '20px', marginTop: '8px'}}>
              <label className="toggle-option" style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
                <input 
                  type="radio" 
                  name="processingMethod"
                  value="embeddings"
                  checked={settings.processingMethod === 'embeddings'}
                  onChange={(e) => handleInputChange('processingMethod', e.target.value)}
                />
                <span>all-MiniLM-L12-v2</span>
              </label>
              
              <label className="toggle-option" style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
                <input 
                  type="radio" 
                  name="processingMethod" 
                  value="langchain"
                  checked={settings.processingMethod === 'langchain'}
                  onChange={(e) => handleInputChange('processingMethod', e.target.value)}
                />
                <span>LangChain</span>
              </label>
            </div>
          </div>

          <div className="settings-info">
            <h4>Current Configuration:</h4>
            <ul>
              <li>Context Window: ~{Math.round(settings.chunkSize * settings.maxChunks / 1000)}K characters</li>
              <li>Estimated Tokens: ~{Math.round(settings.chunkSize * settings.maxChunks / 4)}</li>
              <li>Typical 25-page PDF: {settings.chunkSize * settings.maxChunks >= 60000 ? '✅ Full coverage' : '⚠️ Partial coverage'}</li>
            </ul>
          </div>
        </div>

        <div className="settings-actions">
          <button className="btn-secondary" onClick={resetToDefaults}>
            Reset to Defaults
          </button>
          <button className="btn-primary" onClick={onClose}>
            Apply Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;