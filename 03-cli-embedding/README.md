# 03 - HANA Vector Store + RAG Chat

This step builds on `02-cli-chat` and adds **retrieval-augmented generation (RAG)** using the **SAP HANA Cloud Vector Engine** as a vector store.

It consists of two small command-line tools:

- `ingest.py` – load a text file, split it into chunks, and store embeddings in HANA.
- `chat_rag.py` – ask questions about the ingested document using retrieval + LLM.

Both reuse the shared `.env` and `LLM_*` variables at the repo root, plus additional `HANA_*` variables.

## Prerequisites

- HANA Cloud instance with Vector Engine enabled.
- Root `.env` configured with both SAP AI Core and HANA credentials (see `.env.example`).

## 1. Ingest a document into HANA

From the repo root:

```bash
cd 03-cli-embedding
uv sync
```

Then run the ingest script:

```bash
uv run ingest.py path/to/your-document.txt
```

If no path is provided, the script looks for `sample.txt` in this folder.

What it does:

- Connects to HANA using `HANA_DB_ADDRESS`, `HANA_DB_PORT`, `HANA_DB_USER`, `HANA_DB_PASSWORD`.
- Uses an **embedding model from SAP Generative AI Hub** via `init_embedding_model` and `LLM_EMBEDDING_MODEL` (e.g. `text-embedding-3-small`).
- Splits the text into chunks and stores them in the table `HANA_TABLE_NAME` (default: `WORKSHOP_DOCS`).
- If you ingest the **same file path** again, existing chunks for that file (metadata `source`) are deleted first to avoid duplicates.

## 2. Chat with RAG over HANA (`chat_rag.py`)

After ingestion, start the RAG chat:

```bash
uv run chat_rag.py
```

On each question:

- Retrieves the most relevant chunks from HANA.
- Builds a prompt that includes:
  - The **system prompt** (`LLM_SYSTEM_PROMPT`).
  - The retrieved **context**.
  - The current **user question**.
- Streams the LLM answer to the terminal.

Controls:

- Prompt appears as:

  ```text
  You (question about the document, empty to exit):
  ```

- Type a question and press Enter.
- Press Enter on an empty line to exit.

## What’s new compared to 02

- **Vector store**: Introduces SAP HANA Cloud Vector Engine via `langchain-hana`.
- **Ingestion step**: Separate CLI to prepare the knowledge base.
- **RAG**: Answers are grounded in the ingested document rather than just the system prompt.

You can tune retrieval and chunking via env vars (see `.env.example`):

- `RAG_TOP_K` – number of chunks retrieved per question.
- `RAG_CHUNK_SIZE` – splitter chunk size in characters.
- `RAG_CHUNK_OVERLAP` – overlap between chunks in characters.
