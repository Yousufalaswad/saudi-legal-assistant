from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import CohereEmbeddings
from langchain_core.documents import Document
import json, os, time
from dotenv import load_dotenv

load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY not found in .env file")

print("Initializing embeddings...")
embeddings = CohereEmbeddings(
    cohere_api_key=cohere_api_key,
    model="embed-multilingual-v3.0",
    user_agent="langchain",
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", "،", " "],
)

all_docs = []

# Load PDFs
pdf_dir = "data/pdfs"
pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
print(f"\nLoading {len(pdf_files)} PDFs...")

for pdf_file in pdf_files:
    path = os.path.join(pdf_dir, pdf_file)
    try:
        loader = PyPDFLoader(path)
        pages = loader.load()
        chunks = splitter.split_documents(pages)
        for chunk in chunks:
            chunk.metadata["source"] = pdf_file
            chunk.metadata["type"] = "law"
        all_docs.extend(chunks)
        print(f"  {pdf_file}: {len(chunks)} chunks")
    except Exception as e:
        print(f"  {pdf_file}: ERROR - {e}")

# Load legal cases — only first 500 to stay within rate limit
print(f"\nLoading legal cases dataset (first 500 only)...")
with open("data/datasets/arabic_legal_cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

# Take first 500 cases only
cases = cases[:500]
case_docs = []
for i, case in enumerate(cases):
    if len(case.strip()) > 50:
        doc = Document(
            page_content=case,
            metadata={"source": "arabic_legal_cases", "type": "case", "index": i}
        )
        case_docs.append(doc)

case_chunks = splitter.split_documents(case_docs)
all_docs.extend(case_chunks)
print(f"  Legal cases: {len(case_chunks)} chunks")

print(f"\nTotal documents to index: {len(all_docs)}")
print("Building FAISS index...")

# Small batches with delay to respect rate limit
batch_size = 40
vectorstore = None
total_batches = (len(all_docs) // batch_size) + 1

for i in range(0, len(all_docs), batch_size):
    batch = all_docs[i:i+batch_size]
    batch_num = i//batch_size + 1
    print(f"  Batch {batch_num}/{total_batches}...")

    try:
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)
    except Exception as e:
        print(f"  Error on batch {batch_num}: {e}")
        print("  Waiting 60 seconds...")
        time.sleep(60)
        # Retry
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)

    # Pause between batches to avoid rate limit
    time.sleep(2)

os.makedirs("data/index", exist_ok=True)
vectorstore.save_local("data/index")
print(f"\nIndex saved to data/index/")
print("Done!")