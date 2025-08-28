# Technical Context

## Technologies Used

- Backend: Python 3.x, FastAPI or Flask (assumed for API server)
- Frontend: React.js, JavaScript, CSS
- AI Models: OpenAI GPT, Anthropic Claude, Gemini (Google)
- Embedding Stores: Vector databases or in-memory stores (e.g., FAISS, Pinecone)
- PDF Processing: Python libraries such as PyPDF2 or pdfplumber
- Deployment: Railway, Vercel (based on config files)

## Development Setup

- Backend and frontend are separate projects with their own dependencies.
- Backend dependencies managed via requirements.txt.
- Frontend dependencies managed via package.json and npm.
- Local development involves running backend API server and frontend React app concurrently.
- Environment variables used for API keys and configuration.

## Technical Constraints

- Must support multiple AI providers interchangeably.
- Efficient embedding storage and retrieval for fast query response.
- Secure handling of uploaded documents.
- Responsive frontend UI with real-time updates.

## Dependencies

- Python packages for AI SDKs, PDF processing, and web frameworks.
- React libraries for UI components and state management.
- Vector database or embedding store client libraries.

## Tool Usage Patterns

- Modular code structure for easy extension.
- Clear API contracts between frontend and backend.
- Use of environment variables for sensitive data.
- Automated testing and linting recommended.
