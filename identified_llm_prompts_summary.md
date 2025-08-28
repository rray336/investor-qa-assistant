# Identified LLM Prompts Summary

This document summarizes all the LLM prompts identified in the project files analyzed.

## Claude Interface (backend/claude_interface.py)

- The prompt is built in the `_build_prompt` method.
- It includes context from documents, question, and detailed instructions for the assistant.
- The prompt format instructs the assistant to provide an answer, confidence score, and reasoning.
- The prompt emphasizes professionalism, conciseness, and basing answers solely on provided context.

## Gemini Interface (backend/gemini_interface.py)

- The prompt is built in the `_build_prompt` method.
- Similar structure to Claude's prompt: context from documents, question, and response format.
- Instructions include providing answer, confidence, reasoning, and maintaining a corporate tone.
- Safety settings are configured for financial content.

## OpenAI Interface (backend/openai_interface.py)

- The prompt is built in the `_build_prompt` method.
- Context from documents and question are included.
- The prompt requests answer, confidence score, reasoning, and guidelines for professionalism.
- System message is used to set the assistant's role and tone.
- Token usage is tracked for prompt and completion.

---

All three interfaces follow a consistent prompt structure designed to elicit professional, concise, and context-based answers with confidence and reasoning explanations.
