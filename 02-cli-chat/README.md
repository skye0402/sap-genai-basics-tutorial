# 02 - Streaming Chat CLI (LangChain + SAP Generative AI Hub)

This step builds on `01-hello-world` and turns it into a **stateful, streaming chat** in the terminal.

## What this example does

- Uses the **same `.env` and `LLM_*` variables at repo root**.
- Uses **LangChain** chat messages for history:
  - `SystemMessage` for the system prompt.
  - `HumanMessage` / `AIMessage` for each turn.
- On each user input:
  - Sends **full conversation history** to the LLM.
  - Prints the assistant reply **streamed token-by-token** to the terminal.

## Run it

From the repo root:

```bash
cd 02-cli-chat
uv sync
uv run main.py
```

Config is taken from the root `.env` (copy `.env.example` once if you haven’t already):

```bash
cp ../.env.example ../.env   # then edit ../.env with real values
```

## Controls

- Prompt appears as:

  ```text
  You:
  ```

- Type a message and press Enter.
- The assistant reply is streamed as it’s generated.
- Press Enter on an **empty line** to exit.

## What’s new compared to 01

- **History**: Each new call includes all previous messages, so the model has conversational context.
- **Streaming**: Output appears incrementally instead of all at once.
- **LangChain primitives**: Demonstrates `SystemMessage`, `HumanMessage`, `AIMessage`, and `.stream()`.

## Exercise: From plain chat to HANA RAG (`02a-...`)

After you understand `02-cli-chat`, you can try a third exercise before looking at the final solution in `03-cli-embedding`.

- **Step 1 – Copy this project**  
  Create a new folder next to this one, e.g.:

  ```bash
  cp -r 02-cli-chat 02a-cli-rag
  ```

- **Step 2 – Add HANA configuration**  
  In the copied folder, make sure they still load the shared `.env` from the repo root and that the `HANA_*` variables are present in `.env` (see `.env.example`).

- **Step 3 – Implement ingestion**  
  Add a small script (for example `ingest.py`) that:

  - Connects to SAP HANA Cloud using the `HANA_*` env vars.
  - Reads a text file.
  - Splits it into chunks.
  - Stores them in a HANA vector table using the HANA vector store integration.

- **Step 4 – Extend the chat to use retrieval**  
  In a second script (or by extending the existing one), you should:

  - Before calling the LLM, **retrieve relevant chunks** from HANA for the user question.
  - Build a prompt that includes both the retrieved context and the current question.
  - Call the LLM and stream the answer as in `02-cli-chat`.

- **Step 5 – Compare with the solution**  
  Once you are done (or if you get stuck), you can look at the **reference implementation** in the `03-cli-embedding` folder, which contains a minimal ingestion CLI (`ingest.py`) and a RAG chat CLI (`chat_rag.py`) based on the same ideas.
  In that step, you will also see how **RAG parameters** like top-k and chunk sizes are configured via environment variables.
