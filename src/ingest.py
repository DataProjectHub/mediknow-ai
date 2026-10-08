
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

DOCUMENT_PATH = "data/Apex_Sample.md"
VECTOR_STORE_PATH = "vector_store"

print("1. Loading document...")

loader = TextLoader(DOCUMENT_PATH, encoding="utf-8")
documents = loader.load()

print(f"Loaded {len(documents)} document(s)")

print("2. Adding metadata...")

for doc in documents:
    doc.metadata.update(
        {
            "domain": "healthcare",
            "organization": "Apex Medical Center",
            "document_type": "hospital_operations_manual",
            "version": "4.2",
        }
    )

print("3. Splitting document into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
)

chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

print("4. Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("5. Creating FAISS vector store...")

vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

print("6. Saving FAISS vector store...")

vector_store.save_local(VECTOR_STORE_PATH)

print("Done!")
print(f"FAISS database saved to: {VECTOR_STORE_PATH}")