import os
from pathlib import Path

from dotenv import load_dotenv
from gen_ai_hub.proxy.langchain.init_models import init_llm
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Load shared credentials and LLM_* config from repo root .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "5000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
SYSTEM_PROMPT = os.getenv("LLM_SYSTEM_PROMPT", "You are a helpful assistant.")


def main() -> None:
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    history = [SystemMessage(content=SYSTEM_PROMPT)]

    while True:
        user = input("You: ")
        if not user.strip():
            break

        history.append(HumanMessage(content=user))
        print("Assistant: ", end="", flush=True)

        ai_content = ""
        for chunk in llm.stream(history):
            text = getattr(chunk, "content", str(chunk))
            print(text, end="", flush=True)
            ai_content += text

        print()
        history.append(AIMessage(content=ai_content))


if __name__ == "__main__":
    main()
