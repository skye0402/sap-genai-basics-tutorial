import json
import os
from pathlib import Path

from dotenv import load_dotenv
from gen_ai_hub.proxy.langchain.init_models import init_llm

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "50000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
SYSTEM_PROMPT = os.getenv("LLM_SYSTEM_PROMPT", "You are a helpful assistant.")


def main() -> None:
    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    while True:
        user = input("Prompt (empty to exit): ")
        if not user.strip():
            break
        text = f"{SYSTEM_PROMPT}\n\nUser: {user}"
        response = llm.invoke(text)
        data = {
            "content": getattr(response, "content", str(response)),
            "response_metadata": getattr(response, "response_metadata", None),
            "usage_metadata": getattr(response, "usage_metadata", None),
        }
        print("Reply:")
        print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
