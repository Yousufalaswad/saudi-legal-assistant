from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import CohereEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langdetect import detect
from app.prompts import RAG_PROMPT_EN, RAG_PROMPT_AR
import os

def get_embeddings(cohere_api_key: str):
    return CohereEmbeddings(
        cohere_api_key=cohere_api_key,
        model="embed-multilingual-v3.0",
        user_agent="langchain",
    )

def load_vectorstore(cohere_api_key: str) -> FAISS:
    embeddings = get_embeddings(cohere_api_key)
    vectorstore = FAISS.load_local(
        "data/index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vectorstore

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "en"

def build_chain(vectorstore: FAISS, groq_api_key: str, language: str = "en"):
    llm = ChatGroq(
        api_key=groq_api_key,
        model="llama-3.1-8b-instant",
        temperature=0.1,
    )

    prompt_template = RAG_PROMPT_AR if language == "ar" else RAG_PROMPT_EN
    prompt = PromptTemplate.from_template(prompt_template)

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    def format_docs(docs):
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            formatted.append(f"[Source: {source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever

def ask_question(question: str, vectorstore: FAISS, groq_api_key: str):
    language = detect_language(question)
    chain, retriever = build_chain(vectorstore, groq_api_key, language)
    answer = chain.invoke(question)
    source_docs = retriever.invoke(question)
    sources = list(set(
        doc.metadata.get("source", "unknown")
        for doc in source_docs
    ))
    return answer, sources, language