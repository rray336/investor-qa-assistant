# LangChain Integration TODO List

## Overview
Add LangChain direct PDF processing as an alternative to the current embedding-based method. Both methods will share the same upload pipeline but diverge during query processing.

## High-Level Tasks

### 1. Frontend Changes
- [x] **Add Processing Method Toggle to SettingsPanel.js**
  - ✅ Add new setting: `processingMethod: 'embeddings' | 'langchain'`
  - ✅ Add radio buttons below "Max Chunks Retrieved" setting
  - ✅ Options: "all-MiniLM-L12-v2" (current) and "LangChain" (new)
  - ✅ Update localStorage handling for new setting

### 2. Backend Core Implementation
- [x] **Create langchain_query_engine.py**
  - ✅ Implement `LangchainQueryEngine` class
  - ✅ Method to retrieve PDF file paths from database
  - ✅ PDF download from Supabase storage
  - ✅ Base64 conversion of PDF files
  - ✅ Loop through each PDF and send to LLM with question
  - ✅ Consolidate multiple PDF responses into single answer
  - ✅ Maintain same response format as current method

- [x] **Add Database Support**
  - ✅ Add `get_pdf_files_for_query()` method to `database.py`
  - ✅ Return PDF metadata and file paths for LangChain processing
  - ✅ Handle Supabase storage file retrieval

### 3. API Integration
- [x] **Modify main.py**
  - ✅ Update `/ask-question` endpoint to check `processingMethod` setting
  - ✅ Route to appropriate query engine based on setting
  - ✅ Ensure backward compatibility with existing requests
  - ✅ Add LangchainQueryEngine import and initialization

### 4. Dependencies
- [x] **Update requirements.txt**
  - ✅ Add `langchain>=0.1.0` dependency
  - ✅ Add `langchain-community>=0.0.20` dependency

### 5. Testing & Validation
- [ ] **End-to-End Testing**
  - Test both processing methods with same PDFs
  - Verify response format consistency
  - Test settings persistence
  - Validate performance characteristics
  - Ensure proper error handling for both methods

## Implementation Notes

### Shared Pipeline (No Changes)
- PDF Upload → Chunk → Embed → Store
- All existing functionality remains intact
- Embeddings still generated for potential future use

### Query Divergence
- **Embeddings Method**: Similarity search → Retrieve chunks → LLM
- **LangChain Method**: Get PDFs → Download files → Send full PDFs to LLM → Consolidate

### Response Format
Both methods should return:
```json
{
  "answer": "string",
  "confidence": "number", 
  "reasoning": "string",
  "sources": "array",
  "chunks_found": "number",
  "question": "string"
}
```

## Success Criteria
- [ ] User can toggle between processing methods in settings
- [ ] Both methods work with same uploaded PDFs
- [ ] Response format is consistent between methods
- [ ] No breaking changes to existing functionality
- [ ] Settings are persisted across sessions