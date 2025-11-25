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
