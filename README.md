# MediKnow AI

### Trust-Aware Healthcare Retrieval-Augmented Generation

MediKnow AI is an independent AI engineering project exploring how Retrieval-Augmented Generation (RAG) can be made more reliable, transparent, and useful for healthcare knowledge systems.

Unlike a conventional RAG assistant, MediKnow does not assume that retrieving semantically similar text means the knowledge base actually contains a valid answer. The system is being designed to distinguish between:

1. **Healthcare questions supported by available evidence**
2. **Healthcare questions for which sufficient evidence is missing**
3. **Queries outside the healthcare domain**

When sufficient evidence is unavailable, MediKnow avoids generating an unsupported answer and instead identifies the situation as a **knowledge gap** for later review.

> **Project status:** Active development  
> **Current interface:** Command-line application  
> **Current generation model:** Llama 3.2 3B via Ollama  
> **Current vector store:** FAISS  
> **Current embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

## Why MediKnow AI?

A basic RAG application often follows a simple pattern:

```text
User Question
     ↓
Vector Search
     ↓
Top-K Chunks
     ↓
LLM
     ↓
Answer
```

That approach can fail when the retriever returns text that is semantically similar but does not actually answer the question.

MediKnow adds validation around the RAG workflow.

Its current design asks:

```text
Is the query healthcare-related?
            ↓
Did retrieval return evidence?
            ↓
Does that evidence actually answer the question?
            ↓
If YES → generate a grounded answer
If NO  → detect and log a knowledge gap
```

The long-term goal is to evolve MediKnow from a simple RAG chatbot into a **traceable healthcare knowledge platform** that can recognize missing evidence, detect conflicting or outdated guidance, support human review, and explain the basis for its responses.

---

# Current Architecture

```text
Healthcare Knowledge Documents
            ↓
       Document Ingestion
            ↓
         Text Chunking
            ↓
 Sentence Transformer Embeddings
            ↓
       FAISS Vector Store
            ↓
          User Query
            ↓
 Healthcare Scope Classification
            ↓
      Semantic Retrieval
            ↓
 Evidence Sufficiency Validation
            ↓
      ┌─────────────────────┐
      │ Is evidence enough? │
      └─────────┬───────────┘
           YES  │  NO
                │
       ┌────────┴───────────┐
       ↓                    ↓
Grounded Prompt       Knowledge Gap
       ↓                    ↓
Llama 3.2 via Ollama     Gap Logging
       ↓
     Answer
```

---

# Current Capabilities

## 1. Healthcare Document Ingestion

`src/ingest.py` loads healthcare knowledge documents, splits them into manageable chunks, generates embeddings, and stores the resulting vectors in FAISS.

Current flow:

```text
Source Document
      ↓
Text Loader
      ↓
Recursive Character Splitting
      ↓
Embeddings
      ↓
FAISS Index
```

Current chunking configuration:

```python
chunk_size = 800
chunk_overlap = 150
```

The overlap helps preserve context when a sentence or idea crosses a chunk boundary.

The current embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Generated FAISS files include:

```text
index.faiss
index.pkl
```

These are generated locally and do not need to be committed to the repository.

---

## 2. Semantic Retrieval

`src/retrieve.py` loads the FAISS vector store and retrieves chunks that are semantically related to a user query.

The current retriever supports Top-K retrieval and has also been tested with:

- similarity search
- relevance scores
- MMR-style retrieval
- retrieval debugging

A key lesson from development was that **retrieval similarity alone is not enough**.

For example, FAISS may return medical chunks for a medical query even when none of those chunks actually answer the question. MediKnow therefore adds a separate evidence validation step.

---

## 3. Healthcare Scope Classification

Before a query is treated as a knowledge-base question, MediKnow checks whether it belongs to the healthcare domain.

Example:

```text
Question:
What happens during an emergency admission?

Healthcare relevant: YES
```

Example:

```text
Question:
How do I repair a car engine?

Healthcare relevant: NO
```

Out-of-scope queries are rejected rather than incorrectly being treated as missing healthcare knowledge.

---

## 4. Evidence Sufficiency Validation

MediKnow does not assume that retrieved chunks are automatically sufficient.

After retrieval, the system checks whether the retrieved evidence actually contains enough information to answer the question.

Example:

```text
Question:
What happens during an emergency admission?

Retrieved evidence:
Emergency Admissions policy

Evidence sufficient: YES
```

Example:

```text
Question:
What is the procedure for an MRI contrast allergy?

Retrieved evidence:
Medication administration
Infection prevention
Patient complaints

Evidence sufficient: NO
```

This is important because semantically related information is not always answer-supporting information.

---

## 5. Knowledge Gap Detection

Knowledge Gap Detection is one of MediKnow's core differentiators.

A knowledge gap is created when:

```text
Healthcare relevance = YES
Evidence sufficient = NO
```

Example:

```text
Question:
What is the procedure for an MRI contrast allergy?

Healthcare relevant: YES
Evidence sufficient: NO

Result:
KNOWLEDGE GAP DETECTED
```

Instead of allowing the LLM to invent an answer, MediKnow responds with:

```text
This is a relevant healthcare question, but sufficient information
could not be found in the MediKnow knowledge base.
```

The question is then logged locally for future review.

This can eventually help identify:

- missing procedures
- missing policies
- incomplete departmental knowledge
- frequently requested but undocumented information
- areas requiring content updates

---

## 6. Grounded Answer Generation

When sufficient evidence is available, MediKnow builds a prompt using only the retrieved knowledge-base context.

The current LLM is:

```text
Llama 3.2 3B
```

served locally through:

```text
Ollama
```

The model is instructed to:

- answer only from the supplied context
- avoid adding unsupported information
- explicitly state when information cannot be found

This keeps answer generation grounded in the retrieved institutional knowledge rather than relying on unrestricted model knowledge.

---

# Example Behaviours

## Example 1 — Supported Healthcare Query

**Question**

```text
What happens during an emergency admission?
```

**Retrieved evidence**

```text
Emergency Admissions:
Patients arriving via the Emergency Department are triaged using
the Emergency Severity Index (ESI). Life-threatening conditions
bypass financial clearance and are stabilized immediately under
the EMTALA guidelines.
```

**MediKnow response**

```text
Patients arriving via the Emergency Department (ED) are triaged
using the Emergency Severity Index (ESI). Life-threatening
conditions bypass financial clearance and are stabilized
immediately under the EMTALA guidelines.
```

**Classification**

```text
Healthcare relevant: YES
Evidence sufficient: YES
Knowledge gap: NO
```

---

## Example 2 — Healthcare Knowledge Gap

**Question**

```text
What is the procedure for an MRI contrast allergy?
```

**MediKnow response**

```text
This is a relevant healthcare question, but sufficient information
could not be found in the MediKnow knowledge base.
```

**Classification**

```text
Healthcare relevant: YES
Evidence sufficient: NO
Knowledge gap: YES
```

---

## Example 3 — Out-of-Scope Query

**Question**

```text
How do I repair a car engine?
```

**MediKnow response**

```text
This question is outside MediKnow's healthcare scope.
```

**Classification**

```text
Healthcare relevant: NO
Knowledge gap: NO
```

---

# Current Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| RAG framework | LangChain |
| Vector database | FAISS |
| Embeddings | Hugging Face Sentence Transformers |
| Embedding model | `all-MiniLM-L6-v2` |
| Local model runtime | Ollama |
| LLM | Llama 3.2 3B |
| Development environment | Ubuntu / WSL |
| Interface | Command-line application |

### File Responsibilities

**`ingest.py`**  
Loads documents, splits text into chunks, creates embeddings, and builds the FAISS index.

**`retrieve.py`**  
Loads the FAISS index and retrieves relevant chunks for a query.

**`knowledge_gap.py`**  
Handles healthcare relevance classification, evidence sufficiency checks, and knowledge-gap logging.

**`rag_chain.py`**  
Coordinates retrieval, validation, prompt construction, and LLM generation.

**`app.py`**  
Provides the interactive command-line interface.

# Installation

## 1. Clone the repository

```bash
git clone 
cd Mediknow_AI
```

---

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

Core dependencies currently include:

```text
langchain-community
langchain-huggingface
langchain-ollama
langchain-text-splitters
faiss-cpu
sentence-transformers
```

---

## 4. Install Ollama

Install Ollama on your machine and pull the local model:

```bash
ollama pull llama3.2:3b
```

Optional test:

```bash
ollama run llama3.2:3b
```

---

## 5. Build the FAISS vector store

Run:

```bash
python src/ingest.py
```

This creates:

```text
vector_store/index.faiss
vector_store/index.pkl
```

---

## 6. Run MediKnow AI

```bash
python src/app.py
```

You should see:

```text
MediKnow AI
Type 'exit' to quit.

Ask MediKnow:
```

---

# Sample Data

The public repository should contain **synthetic healthcare information only**.

The current sample knowledge base is intended for development and demonstration purposes.

Do not upload:

- real patient data
- protected health information
- confidential hospital policies
- internal credentials
- API keys
- passwords
- tokens
- production logs

---

# Recommended `.gitignore`

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environments
.venv/
venv/

# FAISS generated files
vector_store/
*.faiss
*.pkl

# Logs
logs/
*.log

# Environment variables
.env
.env.*

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

# Future Architecture

MediKnow is being designed to evolve beyond a conventional RAG pipeline.

```text
                    USER QUESTION
                         │
                         ▼
                  Role / Context
                         │
                         ▼
                   Query Analysis
                         │
              ┌──────────┴──────────┐
              │                     │
        Simple Query          Complex Query
              │                     │
              │              Query Decomposition
              │                     │
              └──────────┬──────────┘
                         ▼
                  HYBRID RETRIEVAL
                 ┌───────┴────────┐
                 │                │
             Vector Search     Keyword/BM25
                 │                │
                 └───────┬────────┘
                         ▼
                      Reranking
                         │
                         ▼
                Evidence Validation
                         │
            ┌────────────┼────────────┐
            │            │            │
         Coverage    Contradiction   Freshness
          Check         Check          Check
            │            │            │
            └────────────┼────────────┘
                         ▼
              Is evidence sufficient?
                  │                │
                 YES               NO
                  │                │
                  ▼                ▼
           Grounded Prompt     Knowledge Gap
                  │                │
                  ▼                ▼
                 LLM          Human Review
                  │
                  ▼
            Role-Aware Answer
                  │
                  ▼
             Source Citations
                  │
                  ▼
                Audit Log
```

---

# Planned Enhancements

## 1. Source Citations

Future responses will include the source used to support the answer.

Possible metadata:

```text
Document
Section
Page
Department
Version
Effective date
Expiry date
```

Example:

```text
Source:
Emergency Admission SOP
Section: Emergency Admissions
Page: 17
Version: 5.1
```

This will make answers more transparent and easier to verify.

---

## 2. Evidence Coverage Check

A complex question may contain multiple parts.

Example:

```text
What is the emergency admission process,
what patient identification is required,
and what is the medication reconciliation procedure?
```

Future MediKnow versions will evaluate evidence separately:

```text
Emergency admission          ✓
Patient identification       ✓
Medication reconciliation    ✗
```

Rather than pretending the entire question has been answered, MediKnow will explicitly identify unsupported parts.

---

## 3. Contradiction Detection

Different policies may contain conflicting guidance.

Example:

```text
Policy A:
Patient identification requires Name + Date of Birth

Policy B:
Patient identification requires Name + Medical Record Number
```

Instead of silently choosing one source, MediKnow will flag:

```text
Potential policy conflict detected
```

The conflict can then be sent for human review.

---

## 4. Document Freshness and Expiry Awareness

MediKnow will use document metadata to determine whether retrieved information is current.

Planned metadata:

```text
version
effective_date
expiry_date
department
document_type
supersedes
```

This will allow MediKnow to:

- prefer newer documents
- identify expired guidance
- recognize superseded policies
- warn users when available evidence may be outdated

---

## 5. Hybrid Retrieval

Current retrieval is based primarily on semantic embeddings.

Future retrieval will combine:

```text
Semantic Vector Search
+
Keyword / BM25 Retrieval
```

This will improve results for exact terminology such as:

- policy numbers
- procedure codes
- abbreviations
- medication names
- technical identifiers
- department-specific terminology

---

## 6. Query Decomposition

Complex questions will be broken into smaller sub-queries before retrieval.

Example:

```text
Original:
What is the emergency admission process,
required patient identification,
and medication reconciliation procedure?
```

Possible decomposition:

```text
1. What is the emergency admission process?
2. What patient identification is required?
3. What is the medication reconciliation procedure?
```

Each question can then be retrieved and validated independently before the final response is generated.

---

## 7. Role-Aware Answers

MediKnow will adapt how the same evidence is presented depending on user role.

Potential roles:

```text
Patient
Nurse
Doctor
Administrator
Front Desk
Clinical Operations
```

The underlying evidence will remain unchanged.

Only the explanation, terminology, and level of detail will vary.

---

## 8. Grounded Conversation Memory

Conversation history will help MediKnow understand follow-up questions.

Example:

```text
User:
What happens during emergency admission?

User:
What about identification?
```

The second question can be interpreted as:

```text
What identification is required during emergency admission?
```

However, conversation history will **not** be treated as medical evidence.

The design principle is:

```text
Conversation Memory
        ↓
Understand Query

Knowledge Base
        ↓
Provide Evidence
```

---

## 9. Human Review Workflow

Certain conditions will automatically create review items.

Possible triggers:

```text
Knowledge gap
Incomplete evidence coverage
Contradiction
Expired document
Low-confidence retrieval
Potentially unsafe answer
```

Possible review outcomes:

```text
Approved
Needs Document Update
Incorrect Retrieval
New Policy Required
Resolved
Escalated
```

This creates a human-in-the-loop workflow for cases where automation alone is insufficient.

---

## 10. Audit Trail

Future versions will record how each answer was produced.

Possible audit fields:

```text
Query ID
Timestamp
User role
Original question
Rewritten question
Decomposed sub-queries
Retrieved document IDs
Retrieved chunk IDs
Retrieval scores
Document versions
Evidence status
Coverage result
Contradiction result
Freshness result
Knowledge-gap status
Prompt version
LLM model
Generated answer
Sources
Human-review status
```

This will make MediKnow more traceable and easier to evaluate.

---

## 11. Multimodal Document Ingestion

MediKnow is planned to expand beyond Markdown and text documents.

Potential inputs:

```text
PDF
DOCX
Scanned documents
Images containing text
Tables
Forms
Flowcharts
Clinical diagrams
```

Text-based images can be processed using OCR or document extraction.

More advanced versions may use multimodal models when the meaning depends on the visual itself.

---

## 12. Reranking

Future versions may retrieve a broader candidate set and then use a second model to rerank the results.

```text
Query
  ↓
Initial retrieval
  ↓
Candidate chunks
  ↓
Reranker
  ↓
Best evidence
```

This can improve precision before evidence reaches the LLM.

---

## 13. Metadata-Aware Retrieval

Retrieval can eventually be restricted or prioritized using metadata such as:

```text
Department
Specialty
Document type
Policy version
Hospital
Effective date
Expiry date
Section
```

This can reduce irrelevant matches and improve context quality.

---

## 14. Knowledge Gap Analytics

Knowledge-gap logs can eventually become an analytics layer.

Potential insights:

```text
Most common unanswered questions
Departments with the most knowledge gaps
Frequently missing procedures
Repeated low-confidence queries
Frequently retrieved outdated documents
Common contradiction patterns
```

This would allow MediKnow to contribute not only to question answering, but also to organizational knowledge management.

---

# Development Philosophy

MediKnow is being built incrementally.

The project follows a simple principle:

```text
Build a baseline
      ↓
Test it
      ↓
Identify the failure mode
      ↓
Add one improvement
      ↓
Test again
```

Features are added to solve demonstrated problems rather than simply increasing architectural complexity.

This makes it easier to understand how each component affects retrieval quality, grounding, reliability, and user trust.

---

# Current Development Roadmap

### Implemented

- [x] Healthcare document ingestion
- [x] Text chunking
- [x] Hugging Face embeddings
- [x] FAISS vector storage
- [x] Semantic retrieval
- [x] Local Llama 3.2 generation through Ollama
- [x] Grounded answer generation
- [x] Healthcare scope classification
- [x] Evidence sufficiency validation
- [x] Knowledge-gap detection
- [x] Knowledge-gap logging
- [x] Out-of-scope query handling

### Planned

- [ ] Source citations
- [ ] Evidence coverage checking
- [ ] Contradiction detection
- [ ] Document freshness / expiry awareness
- [ ] Hybrid retrieval
- [ ] Query decomposition
- [ ] Reranking
- [ ] Metadata-aware retrieval
- [ ] Role-aware answers
- [ ] Grounded conversation memory
- [ ] Human review workflow
- [ ] Audit trail
- [ ] Multimodal ingestion
- [ ] Knowledge-gap analytics

---

# Project Goals

MediKnow is intended to explore how RAG systems can become more trustworthy in knowledge-sensitive environments.

The project focuses on four areas:

### Retrieval Quality

Improve how evidence is found using semantic search, keyword search, reranking, metadata, and query decomposition.

### Evidence Trust

Validate whether retrieved information is complete, current, and internally consistent.

### User Experience

Provide grounded, role-appropriate, source-backed responses while supporting natural follow-up questions.

### Governance

Detect missing knowledge, support human review, and maintain an audit trail of how answers were produced.

---

# Safety and Disclaimer

MediKnow AI is an experimental software engineering and research project.

It is **not** intended to:

- provide medical diagnosis
- recommend medical treatment
- make clinical decisions
- replace qualified healthcare professionals
- act as a certified medical device
- process real patient data in its current form

The healthcare information included in the public repository should be synthetic and used only for development and demonstration purposes.

Any future real-world healthcare deployment would require appropriate clinical validation, privacy controls, security review, governance, regulatory assessment, and human oversight.

---

# Project Status

MediKnow AI is actively under development.

The current version demonstrates a working local healthcare RAG pipeline with:

```text
Document ingestion
→ Embeddings
→ FAISS retrieval
→ Domain classification
→ Evidence validation
→ Knowledge-gap detection
→ Grounded LLM generation
```

Future development will focus on evidence traceability, retrieval quality, knowledge governance, human oversight, multimodal ingestion, and stronger validation.

---

# Contributing

The project is currently being developed as an independent learning and engineering project.

Suggestions, technical feedback, and discussions around RAG reliability, retrieval quality, healthcare knowledge management, and trustworthy AI are welcome.

---

# License

Add the license selected for this repository here.

For example:

```text
MIT License
```

---

## Author

Independent AI engineering project.

**MediKnow AI — Building RAG systems that know not only how to answer, but also when the evidence is not enough.**
