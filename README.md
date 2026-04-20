# Saudi Legal Assistant | المساعد القانوني السعودي

A bilingual (Arabic/English) AI legal information assistant for Saudi Arabia.

## Live Demo
[Try it here](https://saudi-legal-assistant.streamlit.app)

## What it covers
- Labor disputes & end-of-service benefits
- Rental disputes & tenant rights
- Traffic fine objections
- Enforcement court filings

## Tech Stack
- LLM: Llama 3.1 via Groq API
- Embeddings: Cohere embed-multilingual-v3.0
- Vector Store: FAISS
- Framework: LangChain
- UI: Streamlit
- Data: 4,290+ Saudi commercial court cases + Saudi law PDFs

## Disclaimer
This tool provides legal information only, not legal advice.
Always consult a MOJ-licensed lawyer for your specific case.

## Setup
1. Clone the repo
2. Install: `pip install -r requirements.txt`
3. Add keys to `.env` (see `.env.example`)
4. Build index: `python build_index.py`
5. Run: `streamlit run app/main.py`