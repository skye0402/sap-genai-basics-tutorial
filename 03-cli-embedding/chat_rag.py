import os
from pathlib import Path

from dotenv import load_dotenv
from hdbcli import dbapi
from langchain_hana import HanaDB
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

# Load shared configuration from repo root .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "5000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
SYSTEM_PROMPT = os.getenv("LLM_SYSTEM_PROMPT", "You are a helpful assistant.")


def get_connection() -> dbapi.Connection:
    return dbapi.connect(
        address=os.getenv("HANA_DB_ADDRESS"),
        port=int(os.getenv("HANA_DB_PORT", "443")),
        user=os.getenv("HANA_DB_USER"),
        password=os.getenv("HANA_DB_PASSWORD"),
        autocommit=True,
        sslValidateCertificate=False,
    )


def get_vector_store() -> HanaDB:
    connection = get_connection()
    embedding_model = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
    table_name = os.getenv("HANA_TABLE_NAME", "WORKSHOP_DOCS")

    embeddings = init_embedding_model(embedding_model)

    return HanaDB(embedding=embeddings, connection=connection, table_name=table_name)


def main() -> None:
    db = get_vector_store()
    top_k = int(os.getenv("RAG_TOP_K", "5"))
    retriever = db.as_retriever(search_kwargs={"k": top_k})

    llm = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)

    while True:
        question = input("You (question about the document, empty to exit): ")
        if not question.strip():
            break

        docs = retriever.invoke(question)
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

        prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

User: {question}
"""

        print("Assistant: ", end="", flush=True)
        for chunk in llm.stream(prompt):
            text = getattr(chunk, "content", str(chunk))
            print(text, end="", flush=True)
        print()


if __name__ == "__main__":
    main()
