# System Patterns

## Architecture Overview

The Investor Q&A Assistant follows a modular client-server architecture with clear separation between backend AI processing and frontend user interface.

- Backend: Python-based API server handling AI model interfaces, embedding stores, PDF processing, and query engines.
- Frontend: React-based SPA providing user interaction, document upload, and question submission.

## Key Components

- AI Interface Modules: Abstract interfaces for different AI providers (e.g., OpenAI, Claude, Gemini).
- Embedding Store Modules: Manage vector embeddings for document content to enable semantic search.
- PDF Processor: Extracts and preprocesses text from uploaded PDF documents.
- Query Engine: Coordinates retrieval and AI model querying to generate answers.
- Frontend Components: UI elements for question input, answer display, document management, and settings.

## Design Patterns

- Adapter Pattern: Used for AI and embedding store interfaces to allow easy swapping of providers.
- Factory Pattern: For creating AI interface instances based on configuration.
- Observer Pattern: Frontend components update reactively based on state changes.
- Singleton Pattern: For shared resources like embedding stores and configuration.

## Component Relationships

- Frontend communicates with backend API endpoints.
- Backend AI interfaces interact with external AI services.
- Embedding stores are queried by the backend query engine.
- PDF processor feeds data into embedding stores.

## Critical Implementation Paths

- Upload PDF → Process PDF → Store embeddings → Submit question → Retrieve relevant embeddings → Query AI model → Return answer to frontend.

## Extensibility

- New AI providers can be added by implementing the AI interface.
- Additional embedding stores can be integrated similarly.
- Frontend components designed for easy addition of new features.
