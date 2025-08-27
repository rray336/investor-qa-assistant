# Summary of Identified LLM Prompts in the Project

This document summarizes all the LLM prompts identified in the project files analyzed.

## 1. OpenAI Interface (backend/openai_interface.py)

- The prompt is built in the `_build_prompt` method.
- It includes a context section listing document chunks with filenames and relevance scores.
- The question is appended after the context.
- Instructions specify the response format with sections: ANSWER, CONFIDENCE, REASONING.
- Guidelines emphasize professionalism, conciseness, bullet points, and referencing document sources.
- The prompt is passed as the "content" of a "user" role message in the OpenAI chat completions API.

## 2. Gemini Interface (backend/gemini_interface.py)

- The prompt is built in the `_build_prompt` method.
- Similar structure to OpenAI prompt: context from documents, question, response format instructions.
- The prompt starts with a role description as a professional corporate investor relations assistant.
- The prompt is passed as a string to the Gemini generative model's `generate_content` method.

## 3. Claude Interface (backend/claude_interface.py)

- The prompt is built in the `_build_prompt` method.
- Similar structure and instructions as OpenAI and Gemini prompts.
- The prompt is passed as the "content" of a "user" role message in the Claude API's messages.create method.

---

All three interfaces follow a consistent prompt pattern designed to instruct the LLM to answer investor relations questions based on provided document context, with a structured response format including answer, confidence, and reasoning.
