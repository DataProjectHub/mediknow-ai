from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_STORE_PATH = "vector_store"


def get_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_store


def get_retriever():
    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10
        }
    )

    return retriever


if __name__ == "__main__":

    vector_store = get_vector_store()

    query = "What should patients do during an emergency?"

    print("3. Searching FAISS...")

    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=4
    )

    for i, (doc, score) in enumerate(results, start=1):

        print(f"\n--- Chunk {i} ---")
        print(f"Relevance score: {score:.4f}")
        print(doc.page_content)
        print("Metadata:", doc.metadata)