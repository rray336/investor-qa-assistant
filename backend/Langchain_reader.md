Here is a code template that shows how to read a pdf file using langchain

# # OPENAI

#if not os.environ.get("OPENAI_API_KEY"):

# os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# Import langchain

from langchain.chat_models import init_chat_model
llm_model = init_chat_model("gpt-4o-mini", model_provider="openai")

import base64
from pathlib import Path

# path = Path(r"C:\Users\rahul\OneDrive\IMP_DOCS\AI\langchain-multimodal-data\test.pdf")

# Read the pdf file

path = Path(r"C:\Users\rahul\OneDrive\IMP_DOCS\AI\langchain-multimodal-data\3Q25-Earnings-Call-Transcript.pdf")
pdf_data = base64.b64encode(path.read_bytes()).decode("utf-8")

#Create the prompt
prompt = f"""
What are the top 3 questions asked by analysts ranked by length of management response. List a cleaned up version of the question. Provide management's response in paragraph form - insert ... to connect points
"""

message = {
"role": "user",
"content": [
{
"type": "text",
"text": prompt,
},
{
"type": "file",
"source_type": "base64",
"data": pdf_data,
"mime_type": "application/pdf",
"filename": "my-file",
},
],
}

# Call the LLM via langchain

response = llm_model.invoke([message])
