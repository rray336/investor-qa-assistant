# Multi-Model AI Integration Guide

This document outlines the steps needed to integrate OpenAI (GPT) and Google Gemini models alongside the existing Anthropic Claude integration in the Investor Q&A Assistant.

## Overview

The current system uses:
- **Claude 3.5 Sonnet** for question answering
- **all-MiniLM-L6-v2** for embeddings

This guide shows how to add support for multiple AI providers while maintaining the existing architecture.

---

## 1. Environment Configuration

### 1.1 Environment Variables

Add the following variables to your `.env` file:

```env
# Existing
ANTHROPIC_API_KEY=your_anthropic_api_key

# New additions
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_gemini_api_key

# Optional: Default model selection
DEFAULT_AI_MODEL=claude  # Options: claude, openai, gemini
```

### 1.2 API Key Setup

**OpenAI Setup:**
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Add to environment variables

**Google Gemini Setup:**
1. Visit https://aistudio.google.com/app/apikey
2. Create new API key
3. Add to environment variables

---

## 2. Backend Dependencies

### 2.1 Update requirements.txt

Add these lines to `backend/requirements.txt`:

```txt
# Existing dependencies remain...

# OpenAI integration
openai>=1.12.0

# Google Gemini integration
google-generativeai>=0.3.2

# Optional: Model management utilities
tiktoken>=0.5.1  # For OpenAI token counting
```

### 2.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 3. New Interface Classes

### 3.1 OpenAI Interface (`backend/openai_interface.py`)

Create a new file with the following structure:

**Key Components:**
- Class: `OpenAIInterface`
- Model options: `gpt-4`, `gpt-3.5-turbo`, `gpt-4-turbo`
- Methods to implement:
  - `__init__(self, model="gpt-4")`
  - `async def initialize(self)`
  - `async def generate_answer(question, context_chunks, max_tokens=1000)`
  - `async def test_connection()`
  - `_build_prompt(question, context_chunks)`
  - `_parse_response(response_text)`

**API Integration:**
- Use `openai.AsyncOpenAI()` client
- Implement chat completions with system/user messages
- Handle rate limiting and error responses
- Parse JSON responses and extract confidence scores

### 3.2 Gemini Interface (`backend/gemini_interface.py`)

Create a new file with the following structure:

**Key Components:**
- Class: `GeminiInterface`
- Model options: `gemini-pro`, `gemini-pro-vision`
- Methods to implement:
  - `__init__(self, model="gemini-pro")`
  - `async def initialize()`
  - `async def generate_answer(question, context_chunks, max_tokens=1000)`
  - `async def test_connection()`
  - `_build_prompt(question, context_chunks)`
  - `_parse_response(response_text)`

**API Integration:**
- Use `google.generativeai` SDK
- Configure safety settings for financial content
- Handle generation config (temperature, max_tokens)
- Implement retry logic for rate limits

---

## 4. Model Factory Pattern

### 4.1 AI Model Factory (`backend/ai_model_factory.py`)

Create a factory class to manage model instantiation:

**Structure:**
```python
class AIModelFactory:
    @staticmethod
    def create_interface(model_type: str, **kwargs):
        # Returns appropriate interface instance
        
    @staticmethod
    def get_available_models():
        # Returns list of available models
        
    @staticmethod
    def validate_model_type(model_type: str):
        # Validates model availability
```

**Supported Models:**
- `claude`: Claude 3.5 Sonnet
- `openai-gpt4`: GPT-4
- `openai-gpt35`: GPT-3.5 Turbo
- `gemini-pro`: Gemini Pro

---

## 5. Query Engine Updates

### 5.1 Enhanced Query Engine (`backend/query_engine.py`)

**Modifications needed:**

1. **Constructor Updates:**
   - Accept model type parameter
   - Initialize appropriate AI interface via factory

2. **Dynamic Model Switching:**
   - Method to change AI model at runtime
   - Fallback logic if primary model fails

3. **Response Standardization:**
   - Ensure consistent response format across all models
   - Unified confidence scoring system

4. **Performance Tracking:**
   - Track response times per model
   - Log model usage statistics

### 5.2 Model Configuration

Add model-specific configurations:

```python
MODEL_CONFIGS = {
    "claude": {
        "max_tokens": 1000,
        "temperature": 0.1,
        "timeout": 30
    },
    "openai-gpt4": {
        "max_tokens": 1000, 
        "temperature": 0.1,
        "timeout": 30
    },
    "gemini-pro": {
        "max_output_tokens": 1000,
        "temperature": 0.1,
        "timeout": 30
    }
}
```

---

## 6. API Endpoint Enhancements

### 6.1 Main Application Updates (`backend/main.py`)

**Initialization Changes:**
- Initialize all AI interfaces at startup
- Add health checks for each model
- Implement graceful degradation if models are unavailable

**New Endpoints:**

1. **GET `/models`** - List available AI models
2. **GET `/models/{model_type}/health`** - Check specific model health
3. **POST `/ask-question`** - Enhanced with model selection

**Request Schema Updates:**
```json
{
  "question": "string",
  "model": "claude|openai-gpt4|openai-gpt35|gemini-pro",
  "chunking_settings": {
    "chunkSize": 4000,
    "chunkOverlap": 400,
    "maxChunks": 20
  }
}
```

**Response Schema Updates:**
```json
{
  "question": "string",
  "answer": "string",
  "confidence": 85,
  "sources": [...],
  "model_used": "claude",
  "response_time_ms": 1250,
  "token_usage": {
    "prompt_tokens": 450,
    "completion_tokens": 120,
    "total_tokens": 570
  }
}
```

---

## 7. Frontend Integration

### 7.1 Model Selection Component

**New Component: `ModelSelector.js`**
- Dropdown for AI model selection
- Real-time availability indicators
- Cost estimation per model

**Integration Points:**
- Add to `SettingsPanel.js`
- Include in `QuestionBox.js`
- Store selection in component state

### 7.2 API Service Updates (`frontend/src/services/api.js`)

**Enhancements:**
- Add model parameter to question requests
- Implement model availability checking
- Add retry logic with model fallback

### 7.3 UI/UX Improvements

**Answer Display:**
- Show which model generated the response
- Display response time and token usage
- Add model performance indicators

**Settings Panel:**
- Model preference configuration
- Cost tracking and budgeting
- Usage statistics per model

---

## 8. Error Handling & Fallbacks

### 8.1 Graceful Degradation

**Fallback Hierarchy:**
1. Primary selected model
2. Secondary preferred model
3. Any available model
4. Error message with retry option

**Error Scenarios:**
- API key invalid/expired
- Rate limits exceeded
- Model temporarily unavailable
- Network connectivity issues

### 8.2 Retry Logic

**Implementation Strategy:**
- Exponential backoff for rate limits
- Circuit breaker pattern for failed models
- Automatic failover to backup models

---

## 9. Cost Management

### 9.1 Usage Tracking

**Metrics to Track:**
- Tokens used per model
- API calls per model
- Cost per query
- Daily/monthly spending

**Storage:**
- Add usage tracking tables to database
- Store per-user usage statistics
- Implement cost alerts

### 9.2 Budget Controls

**Features:**
- Daily/monthly spending limits
- Model restrictions based on cost
- Usage warnings and notifications

---

## 10. Security Considerations

### 10.1 API Key Management

**Best Practices:**
- Store keys in environment variables only
- Implement key rotation procedures
- Add API key validation at startup

### 10.2 Data Privacy

**Considerations:**
- Review each provider's data retention policies
- Implement data residency controls
- Add opt-out options for specific models

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Test Coverage:**
- Each AI interface implementation
- Model factory functionality
- Error handling scenarios
- Response parsing accuracy

### 11.2 Integration Tests

**Test Scenarios:**
- End-to-end question answering
- Model fallback mechanisms
- Cost tracking accuracy
- Performance benchmarking

### 11.3 Load Testing

**Performance Metrics:**
- Response times per model
- Concurrent request handling
- Rate limit compliance
- Cost per query analysis

---

## 12. Monitoring & Analytics

### 12.1 Model Performance Metrics

**Key Metrics:**
- Response time by model
- Success/failure rates
- User satisfaction scores
- Cost efficiency analysis

### 12.2 Usage Analytics

**Tracking:**
- Most popular models
- Query patterns by model
- Peak usage times
- Geographic usage distribution

---

## 13. Deployment Considerations

### 13.1 Environment Variables

**Production Setup:**
- Secure API key storage
- Environment-specific model configurations
- Fallback model specifications

### 13.2 Scaling Considerations

**Infrastructure:**
- Load balancing across models
- Caching strategies for expensive queries
- Database optimization for usage tracking

---

## 14. Future Enhancements

### 14.1 Advanced Features

**Potential Additions:**
- Model ensemble responses
- A/B testing framework
- Custom fine-tuned models
- Real-time model performance optimization

### 14.2 Additional Providers

**Expansion Options:**
- Azure OpenAI Service
- AWS Bedrock (Claude, Titan)
- Cohere models
- Local/self-hosted models

---

## Implementation Timeline

**Phase 1 (1-2 weeks):**
- Environment setup and dependencies
- Basic OpenAI integration
- Simple model selection UI

**Phase 2 (2-3 weeks):**
- Gemini integration
- Advanced error handling
- Usage tracking implementation

**Phase 3 (1-2 weeks):**
- Cost management features
- Performance optimization
- Comprehensive testing

**Phase 4 (1 week):**
- Documentation and deployment
- Monitoring setup
- User training materials

---

## Conclusion

This multi-model integration will provide users with flexibility in AI model selection while maintaining the high-quality investor relations focus of the application. The modular architecture ensures easy addition of future AI providers and maintains system reliability through comprehensive fallback mechanisms.