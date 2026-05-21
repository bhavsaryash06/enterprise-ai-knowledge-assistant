# Enterprise AI Knowledge Assistant

A production-style enterprise AI knowledge assistant that answers company policy questions using Retrieval-Augmented Generation, Qdrant vector search, LangGraph workflow orchestration, FastAPI, Streamlit, and evidence-based escalation.

The assistant can ingest enterprise policy documents, chunk and index them into Qdrant, retrieve relevant policy evidence, generate citation-backed answers, and escalate unsupported questions when document evidence is weak.

---

## Project Overview

This project simulates an internal enterprise knowledge assistant for employees asking policy-related questions.

Example questions:

- Can I get reimbursed for a home office monitor?
- How quickly should I report a lost company laptop?
- Can I store customer data on my personal laptop?
- Does the company provide pet insurance for employees?
- What is the company policy for buying cryptocurrency?

The system is designed to avoid unsupported answers. If policy evidence is weak, it returns a low-confidence escalation response instead of hallucinating.

---

## Key Features

- Document upload and ingestion
- Text extraction from `.txt` and `.pdf` files
- Text cleaning and chunking
- SQLite document and chunk metadata storage
- OpenAI embedding generation
- Qdrant vector database indexing
- Query rewriting for better retrieval
- Metadata filtering by department and document type
- Optional reranking
- Citation-backed answer generation
- Evidence strength checking
- Weak-evidence escalation
- LangGraph workflow orchestration
- LangSmith tracing support
- Streamlit frontend
- FastAPI backend
- Docker Compose setup
- Pytest test suite
- Retrieval and answer evaluation scripts
- Structured logging and latency tracking

---

## Tech Stack

| Area | Tools |
|---|---|
| Backend API | FastAPI, Pydantic |
| Frontend | Streamlit |
| Vector Database | Qdrant |
| Database | SQLite, SQLAlchemy |
| LLM | OpenAI API |
| Embeddings | OpenAI text embeddings |
| Workflow | LangGraph |
| Tracing | LangSmith |
| Evaluation | Custom retrieval and answer evaluation scripts |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |
| Document Processing | pypdf, pdfplumber |
| Optional Reranking | Hugging Face sentence-transformers |

---

## Architecture

```text
User
↓
Streamlit UI
↓
FastAPI Backend
↓
LangGraph RAG Workflow
↓
Query Rewriting
↓
Qdrant Vector Retrieval
↓
Optional Reranking
↓
Evidence Strength Check
↓
Answer Generation OR Escalation
↓
Citation-backed Response