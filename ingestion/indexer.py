"""Pinecone serverless index and OpenAI embeddings."""
import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from ingestion.loader import load_document
from ingestion.chunker import chunk_text

load_dotenv()

def get_index():
    name = os.getenv("PINECONE_INDEX", "rag-reliability-demo")
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    if not pc.has_index(name):
        pc.create_index(name=name, dimension=1536, metric="cosine", spec=ServerlessSpec(
            cloud=os.getenv("PINECONE_CLOUD", "aws"), region=os.getenv("PINECONE_REGION", "us-east-1")))
    return pc.Index(name)

def get_embeddings():
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    if model != "text-embedding-3-small":
        raise ValueError("This demo index requires text-embedding-3-small (1536 dimensions)")
    return OpenAIEmbeddings(model=model)

def index_document(file_path: str) -> dict:
    text = load_document(file_path)
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No document chunks")
    filename = Path(file_path).name
    doc_id = hashlib.sha256(filename.encode()).hexdigest()[:16]
    vectors = get_embeddings().embed_documents(chunks)
    index = get_index()
    # Stable IDs allow re-upload without creating duplicate chunks of the same version.
    # Remove old chunks for this document before replacing them.
    index.delete(filter={"doc_id": {"$eq": doc_id}})
    for start in range(0, len(chunks), 50):
        batch = [{"id": f"{doc_id}-{i}", "values": vectors[i],
                  "metadata": {"doc_id": doc_id, "source": filename, "chunk": i, "text": chunks[i]}}
                 for i in range(start, min(start + 50, len(chunks)))]
        index.upsert(vectors=batch)
    return {"filename": filename, "chunks": len(chunks)}
