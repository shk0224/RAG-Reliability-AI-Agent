
"""Tool 1: retrieve candidate chunks from Pinecone."""

import os
from pinecone.models.documents.score_by import DenseVectorQuery
from ingestion.indexer import get_index, get_embeddings


def search_documents(question: str) -> list[dict]:
    vector = get_embeddings().embed_query(question)

    result = get_index().documents.search(
        namespace="__default__",
        score_by=[
            DenseVectorQuery(
                values=vector,
                field="embedding"
            )
        ],
        top_k=int(os.getenv("TOP_K", "5")),
        include_fields=["chunk_text", "title"]
    )

    hits = result.matches

    return [
        {
            "id": hit.id,
            "source": hit.get("title", "unknown"),
            "text": hit.get("chunk_text", ""),
            "score": round(float(hit.score or 0), 4)
        }
        for hit in hits
    ]
