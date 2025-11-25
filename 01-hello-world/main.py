import os
from pathlib import Path

from dotenv import load_dotenv
from gen_ai_hub.proxy.langchain.init_models import init_llm

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
SYSTEM_PROMPT = "You are a helpful assistant."


def main() -> None:
    llm = init_llm(MODEL, max_tokens=300)
    while True:
        user = input("Prompt (empty to exit): ")
        if not user.strip():
            break
        text = f"{SYSTEM_PROMPT}\n\nUser: {user}"
        print("Reply:", llm.invoke(text))


if __name__ == "__main__":
    main()
