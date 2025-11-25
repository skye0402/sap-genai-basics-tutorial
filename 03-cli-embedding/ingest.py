import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from hdbcli import dbapi
from langchain_core.documents import Document
from langchain_hana import HanaDB
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model

# Load shared configuration from repo root .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_connection() -> dbapi.Connection:
    return dbapi.connect(
        address=os.getenv("HANA_DB_ADDRESS"),
        port=int(os.getenv("HANA_DB_PORT", "443")),
        user=os.getenv("HANA_DB_USER"),
        password=os.getenv("HANA_DB_PASSWORD"),
        autocommit=True,
        sslValidateCertificate=False,
    )


def main() -> None:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = Path("sample.txt")

    if not file_path.exists():
        print(f"Input file not found: {file_path}")
        sys.exit(1)

    text = file_path.read_text(encoding="utf-8")

    chunk_size = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    docs = splitter.split_documents(
        [Document(page_content=text, metadata={"source": str(file_path)})]
    )

    connection = get_connection()

    embedding_model = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")
    table_name = os.getenv("HANA_TABLE_NAME", "WORKSHOP_DOCS")

    embeddings = init_embedding_model(embedding_model)

    db = HanaDB(embedding=embeddings, connection=connection, table_name=table_name)

    # Avoid duplicates: remove existing chunks for this source file, then insert
    db.delete(filter={"source": str(file_path)})
    db.add_documents(docs)

    print(f"Ingested {len(docs)} chunks from {file_path} into table '{table_name}'.")


if __name__ == "__main__":
    main()
