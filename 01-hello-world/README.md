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

## Suggested way to work through this step

You can use the following flow when you work with this example:

- **Step 1**: Clone the repo and configure your SAP AI Core access.
- **Step 2**: In `01-hello-world`, run `uv sync` and `uv run main.py` to confirm everything works.
- **Step 3**: Experiment a bit:
  - Change the **system prompt** in code.
  - Change `GENAI_MODEL` to try different models.
- **Step 4**: Reflect on prompts, roles (system vs user), and model choice.

## Exercise: Build your own CLI chat (`01a-cli-chat`)

After you understand `01-hello-world`, try this small coding exercise before looking at the full solution in `02-cli-chat`.

- **Step 1 – Copy the project**  
  Create a new folder next to this one:

  ```bash
  cp -r 01-hello-world 01a-cli-chat
  ```

- **Step 2 – Turn single-call into chat**  
  In `01a-cli-chat/main.py`, you will:

  - Keep loading config from the shared `.env` as in `01-hello-world`.
  - Introduce a simple **message history** (e.g. a Python list).
  - Add the **system prompt** as the first entry in that history.
  - On each user input:
    - Append the user message to the history.
    - Send the **full history** to the model.
    - Append the model reply back into the history.

- **Optional Step 3 – Streaming**  
  As a stretch goal, let them try to stream partial outputs to the terminal instead of printing the full reply at once.

- **Step 4 – Compare with the solution**  
  Once they are done (or if they get stuck), they can look at the **reference implementation** in the `02-cli-chat` folder, which shows a minimal streaming chat using LangChain and the same SAP Generative AI Hub setup.
