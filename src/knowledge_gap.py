import json
import os
from datetime import datetime

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


def is_healthcare_query(query):
    prompt = f"""
You are a query classifier for MediKnow AI.

Determine whether the following question is related to healthcare,
hospital operations, patient care, medical procedures, clinical services,
medications, health administration, or hospital policies.

Return only one word:

YES
or
NO

Question:
{query}
"""

    response = llm.invoke(prompt)

    result = response.content.strip().upper()

    return result.startswith("YES")

def has_sufficient_evidence(query, documents):

    numbered_context = ""

    for i, doc in enumerate(documents, start=1):
        numbered_context += f"""
CHUNK {i}:
{doc.page_content}

"""

    prompt = f"""
You are an evidence checker for MediKnow AI.

Determine whether ANY of the retrieved chunks contains enough
information to give a useful answer to the user's question.

The wording of the question and document does NOT need to match exactly.

For example:
"What happens during an emergency admission?"
is supported by a chunk describing Emergency Admissions,
ED triage, ESI, stabilization, or related admission procedures.

If one or more chunks directly support the question, return:

YES

If none of the chunks contain information that answers the question,
return:

NO

Return only YES or NO.

Question:
{query}

Retrieved evidence:
{numbered_context}
"""

    response = llm.invoke(prompt)

    result = response.content.strip().upper()

    print("Evidence checker result:", result)

    return result.startswith("YES")

def log_knowledge_gap(query):

    os.makedirs("logs", exist_ok=True)

    record = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "status": "knowledge_gap"
    }

    with open(
        "logs/knowledge_gaps.jsonl",
        "a",
        encoding="utf-8"
    ) as file:
        file.write(json.dumps(record) + "\n")