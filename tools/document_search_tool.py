"""Tool 1: retrieve candidate chunks from Pinecone."""
import os
from ingestion.indexer import get_index, get_embeddings

def search_documents(question: str) -> list[dict]:
    vector = get_embeddings().embed_query(question)
    result = get_index().query(vector=vector, top_k=int(os.getenv("TOP_K", "5")), include_metadata=True)
    return [{"id": match.id, "source": match.metadata.get("source", "unknown"),
             "text": match.metadata.get("text", ""), "score": round(float(match.score or 0), 4)}
            for match in result.matches]
