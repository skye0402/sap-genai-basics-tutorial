# GenAI Basics Workshop (SAP HANA + SAP Generative AI Hub)

> ## Day 1 – Quick start
> - **Morning (foundations)**: 01 – Hello World, 02 – Streaming Chat CLI, 03 – HANA Vector Store + RAG
> - **Afternoon (knowledge graph & agents)**: 04 – HANA Knowledge Graph, 05 – Agent Graph
> - **If you only run one thing**: skim 01–03, then run `05-agent-graph-complete`.
>
> **Typical flow**
> 1. Configure `.env` at the repo root (see below).
> 2. Run `01-hello-world` to verify SAP Generative AI Hub access.
> 3. Move to `02-cli-chat` for stateful, streaming chat.
> 4. Use `03-cli-embedding` to ingest a document and try RAG chat.
> 5. In the afternoon, explore `04-knowledge-graph` and then the agent in `05-agent-graph` / `05-agent-graph-complete`.

This repository contains a set of **incremental exercises** that teach how to
combine the **SAP Cloud SDK for AI (Python) – generative**, **SAP HANA Cloud**,
LangChain, and LangGraph.

Each numbered folder (`01-…`, `02-…`, …) is a self-contained step with its own
`pyproject.toml` and `README.md`.

- Use this root `README.md` as a **table of contents**.
- Use the per-step READMEs for **detailed instructions**.

---

## 0. Environment Setup

### 0.1 Python & uv

- **Python**: 3.12 recommended (repo `pyproject.toml` files use `>=3.12`).
- **uv** (fast Python package manager):

  ```bash
  # see https://github.com/astral-sh/uv for latest install instructions
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

Each exercise folder uses `uv sync` to create an **isolated virtual env**
based on its local `pyproject.toml`.

### 0.2 VS Code extensions (recommended)

For a smooth experience in VS Code:

- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Jupyter** (ms-toolsai.jupyter), if you want to run notebooks
- **EditorConfig** / **ESLint** are optional but can help keep formatting clean

No SAP-specific VS Code extension is required for this workshop; everything is
CLI-based.

### 0.3 SAP Cloud SDK for AI (Python) – generative (`sap-ai-sdk-gen`)

This SDK is already listed as a dependency in the exercises' `pyproject.toml`
files; you normally **do not need to install it manually** – `uv sync` will do
it.

**Docs & package pages:**

- Official docs:  
  https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html
- PyPI:  
  https://pypi.org/project/sap-ai-sdk-gen/

**Manual install (if needed):**

```bash
# full installation, including all providers and LangChain support
pip install "sap-ai-sdk-gen[all]"

# or minimal (OpenAI only, without LangChain support)
pip install sap-ai-sdk-gen
```

### 0.4 SAP HANA Python client (`hdbcli`)

Used in the HANA-related steps (vector store and knowledge graph). It is also
pulled in automatically via `pyproject.toml` where needed.

**Docs & package pages:**

- PyPI:  
  https://pypi.org/project/hdbcli/
- SAP Help – Python Application Programming:  
  https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/f3b8fabf34324302b123297cdbe710f0.html

Notes:

- `hdbcli` implements the Python DB API (PEP 249).
- Autocommit is **on by default** in the SAP HANA Python driver.

### 0.5 Configuration via `.env`

At the **repo root**, copy the example environment file once:

```bash
cp .env.example .env
# then edit .env with your real SAP AI Core + HANA credentials
```

Each step reads from this shared `.env` file. Typical variables include:

- SAP AI Core / Generative AI Hub:
  - `AICORE_CLIENT_ID`, `AICORE_CLIENT_SECRET`, `AICORE_AUTH_URL`,
    `AICORE_BASE_URL`, `AICORE_RESOURCE_GROUP`, …
- LLM config:
  - `LLM_MODEL` (e.g. `gpt-4.1`, `anthropic--claude-3.5-sonnet`)
  - `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`
- HANA:
  - `HANA_DB_ADDRESS`, `HANA_DB_PORT`, `HANA_DB_USER`, `HANA_DB_PASSWORD`

For details, see the docs under `documentation/sap-gen-ai-hub-sdk/` and the
per-exercise `.env` sections.

---

## 1. 01 – Hello World (SAP Generative AI Hub)

**Folder:** [`01-hello-world/`](01-hello-world/)  
**Docs:** [`01-hello-world/README.md`](01-hello-world/README.md)

Minimal "Hello LLM" example using `sap-ai-sdk-gen` and `uv`:

- Reads a single prompt from the terminal
- Sends it to a model deployed in SAP Generative AI Hub
- Prints the reply; no chat history
- Shows how to configure the model via env var (`GENAI_MODEL`)

The README also contains an **exercise** (`01a-cli-chat`) where participants
create a simple multi-turn CLI chat by copying this project.

---

## 2. 02 – Streaming Chat CLI (LangChain + SAP Generative AI Hub)

**Folder:** [`02-cli-chat/`](02-cli-chat/)  
**Docs:** [`02-cli-chat/README.md`](02-cli-chat/README.md)

Builds on `01-hello-world` and introduces:

- **Stateful chat** with LangChain message objects (`SystemMessage`,
  `HumanMessage`, `AIMessage`)
- **Streaming** responses token-by-token
- Reuse of the shared `.env` from the repo root

The README includes an **exercise** (`02a-cli-rag`) hinting at extending this
chat to use HANA-based RAG.

---

## 3. 03 – HANA Vector Store + RAG Chat

**Folder:** [`03-cli-embedding/`](03-cli-embedding/)  
**Docs:** [`03-cli-embedding/README.md`](03-cli-embedding/README.md)

Introduces **retrieval-augmented generation (RAG)** using
**SAP HANA Cloud Vector Engine** as a vector store.

Tools:

- `ingest.py` – load a text file, create embeddings, store in HANA
- `chat_rag.py` – ask questions over ingested content via retrieval + LLM

Key points:

- Uses `langchain-hana` to connect to HANA vector store
- Reads both SAP AI Core and HANA credentials from the shared `.env`
- Demonstrates tuning RAG via env vars (e.g. `RAG_TOP_K`, `RAG_CHUNK_SIZE`)

The README ends with an **exercise** that asks for a knowledge-graph-based
alternative – which is implemented in the next step.

---

## 4. 04 – HANA Knowledge Graph

**Folder:** [`04-knowledge-graph/`](04-knowledge-graph/)  
**Docs:** [`04-knowledge-graph/README.md`](04-knowledge-graph/README.md)

Shows how to use **SAP HANA Cloud's Knowledge Graph Engine** to store and query
structured knowledge extracted from unstructured text.

CLI tools:

- `ingest_kg.py` – uses an LLM to extract entities/relationships, stores them
  as RDF triples in HANA via SPARQL
- `chat_kg.py` – generates SPARQL from natural language questions and queries
  the knowledge graph

Highlights:

- Contrast between **vector-based RAG** (step 03) and **knowledge graph**
- Use of `langchain-hana`'s `HanaRdfGraph` and custom SPARQL generation
- Verbose mode to inspect ontology and generated SPARQL

The README also includes exercises:

- Extend the company knowledge graph with new data
- Improve SPARQL generation via prompt tuning
- Compare LLM-generated SPARQL with manual SPARQL

---

## 5. 05 – Agent Graph (LangGraph Agents)

There are two related folders for step 05:

- **Complete demo:** [`05-agent-graph-complete/`](05-agent-graph-complete/)  
  A fully working LangGraph agent.
- **Exercise skeleton:** [`05-agent-graph/`](05-agent-graph/)  
  What participants work on.

### 5.1 05-agent-graph-complete – Software License Procurement Agent

**Docs:** [`05-agent-graph-complete/README.md`](05-agent-graph-complete/README.md)

Shows a complete **agentic AI** example:

- Built with **LangGraph** and the SAP Generative AI Hub SDK
- Uses tools to:
  - Check software license availability (`check_software_license`)
  - Check team budget (`check_team_budget`)
  - Deduct cost from a mutable `TEAM_BUDGETS` dict (`deduct_budget`)
- Uses a small LangGraph state machine:
  - `llm_call` node – decides whether to call tools or answer
  - `tool_node` – executes requested tools
  - `should_continue` – routes between nodes or ends
- CLI loop with conversation history
- Audit log printing decisions, tool calls, tool results, and budget changes

Example scenario:

- IT / Finance / Marketing teams request SAP or Adobe licenses
- Agent checks availability + budget
- Approves or rejects with explanation
- On approval, calls `deduct_budget` so future checks see a reduced budget

### 5.2 05-agent-graph – Exercise Skeleton

**Docs:** [`05-agent-graph/README.md`](05-agent-graph/README.md)

Participants start from a skeleton that already has:

- Model + env loading via `sap-ai-sdk-gen`
- LangGraph `MessagesState`, nodes, and wiring
- CLI loop and audit log printer

They implement the key parts themselves:

1. **EXERCISE 1 – Implement tools**
   - Write the business logic for:
     - `check_software_license(software_name: str)`
     - `check_team_budget(team_name: str)`
2. **EXERCISE 2 – Routing logic**
   - Implement `should_continue` so that:
     - If the last AI message has `tool_calls` → route to `"tool_node"`
     - Otherwise → `END`
   - Optional: add a safety stop based on `llm_calls`.
3. **(Optional) EXERCISE 3 – State-changing tool**
   - Add an in-memory `TEAM_BUDGETS` dict
   - Implement a new `deduct_budget` tool
   - Update the system prompt to call `deduct_budget` when a license is
     approved, so budgets decrease over time

---

## Where to go next

- For deep dives into the SAP Cloud SDK for AI (Python) – generative:  
  https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/index.html
- For HANA Python client programming:  
  https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/f3b8fabf34324302b123297cdbe710f0.html

Use this repo as a starting point and adapt the patterns to your own
applications (different tools, data sources, or approval flows).
