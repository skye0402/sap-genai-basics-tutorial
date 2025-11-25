# 01 - Hello World (SAP Generative AI Hub)

Minimal "Hello LLM" example in Python using the SAP Cloud SDK for AI (Python) - generative (`sap-ai-sdk-gen`) and `uv`.

## What this example does

- Reads a **single prompt** from the terminal.
- Sends it to a model deployed in **SAP Generative AI Hub**.
- Prints the **reply**.
- Repeats until you press Enter on an empty line.
- Uses a **system prompt** defined directly in the code.
- Lets you change the **model id** via environment variable.

No chat memory, no history – just prompt → reply → prompt → reply.

## Prerequisites

1. **Python 3.10+** installed.
2. **`uv`** installed.
3. SAP AI Core / Generative AI Hub credentials configured, **as in the docs in** `documentation/sap-gen-ai-hub-sdk/introduction.md`:
   - Either environment variables like `AICORE_CLIENT_ID`, `AICORE_CLIENT_SECRET`, `AICORE_AUTH_URL`, `AICORE_BASE_URL`, `AICORE_RESOURCE_GROUP`, ...
   - Or a config file referenced via `AICORE_CONFIG` / `AICORE_HOME` / `AICORE_PROFILE`.

## Configure the model

The model id is taken from the environment variable `GENAI_MODEL`.

- Default (if `GENAI_MODEL` is not set): `gpt-4o-mini`.
- To explicitly choose a model, for example Anthropic Claude or Gemini, set:

```bash
export GENAI_MODEL="anthropic--claude-3.5-sonnet"
# or
export GENAI_MODEL="gemini-2.0-flash"
```

The list of supported models is also in `documentation/sap-gen-ai-hub-sdk/introduction.md`.

## System prompt

Inside `main.py` there is a constant system prompt, e.g. “You are a helpful assistant.”

For the workshop, you can let participants **edit that one line** to see how the behavior changes (e.g. “You are a strict coding teacher”, “Answer in German only”, etc.).

## Install dependencies with uv

From the `01-hello-world` folder:

```bash
cd 01-hello-world
uv sync
```

This will read `pyproject.toml` and install `sap-ai-sdk-gen` into an isolated environment.

## Run the example

From the `01-hello-world` folder, after `uv sync`:

```bash
uv run main.py
```

You should see a prompt like:

```text
Prompt (empty to exit):
```

- **Type a question**, press Enter → the model reply is printed.
- **Press Enter on an empty line** to exit.

## How to use in the workshop

A suggested flow for this step:

- **Step 1**: Everyone clones the repo and configures SAP AI Core access.
- **Step 2**: In `01-hello-world`, they run `uv sync` and `uv run main.py` to confirm everything works.
- **Step 3**: Let them
  - Change the **system prompt** in code.
  - Change `GENAI_MODEL` to try different models.
- **Step 4**: Brief discussion of prompts, roles (system vs user), and model choice.
