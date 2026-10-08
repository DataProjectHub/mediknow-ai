from retrieve import get_retriever
from langchain_ollama import ChatOllama
from knowledge_gap import (
    is_healthcare_query,
    has_sufficient_evidence,
    log_knowledge_gap
)

retriever = get_retriever()

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_predict=256
)


def build_context(documents):
    return "\n\n".join(
        doc.page_content for doc in documents
    )


def answer_question(query):

    # Step 1: Check whether the query belongs to MediKnow's domain
    if not is_healthcare_query(query):
        return "This question is outside MediKnow's healthcare scope."

    # Step 2: Retrieve evidence
    documents = retriever.invoke(query)

    print("\n--- RETRIEVED EVIDENCE ---")

    for i, doc in enumerate(documents, start=1):
        print(f"\nChunk {i}:")
        print(doc.page_content[:500])

    if not documents:
        log_knowledge_gap(query)

        return (
            "This is a relevant healthcare question, "
            "but the information is not currently available "
            "in the MediKnow knowledge base."
        )

    # Step 3: Check whether retrieved evidence actually answers the question
    evidence_found = has_sufficient_evidence(
        query,
        documents
    )

    if not evidence_found:
        log_knowledge_gap(query)

        return (
            "This is a relevant healthcare question, "
            "but sufficient information could not be found "
            "in the MediKnow knowledge base."
        )
    documents = retriever.invoke(query)

    if not documents:
        return "Relevant information could not be found in the knowledge base."

    context = build_context(documents)

    prompt = f"""
You are MediKnow AI, a healthcare knowledge assistant.

Answer the user's question using only the information provided in the context.

Do not add information from your own knowledge.

If the answer cannot be found in the context, say:
"Relevant information could not be found in the knowledge base."

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content