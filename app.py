
"""FastAPI entry point. Start with: python app.py"""

from pathlib import Path
from uuid import uuid4
import os
import traceback
import uvicorn

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend import run_rag_agent
from ingestion.indexer import index_document
from ingestion.loader import ALLOWED_EXTENSIONS


app = FastAPI(title="RAG Reliability AI Agent — LangGraph")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

MAX_SIZE = 5 * 1024 * 1024


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


# ==========================================
# FASTAPI ENDPOINT 1: HOME PAGE
# Method: GET /
# ==========================================

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")


# ==========================================
# FASTAPI ENDPOINT 2: HEALTH CHECK
# Method: GET /health
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "pinecone_key_configured": bool(os.getenv("PINECONE_API_KEY")),
        "note": "This does not test external API connectivity"
    }


# ==========================================
# FASTAPI ENDPOINT 3: ASK RAG AGENT
# Method: POST /api/ask
# Calls: backend.py -> run_rag_agent()
# ==========================================

@app.post("/api/ask")
def ask(request: AskRequest):
    try:
        return run_rag_agent(request.question)

    except Exception as error:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Agent failed: {type(error).__name__}"
        ) from error


# ==========================================
# FASTAPI ENDPOINT 4: UPLOAD DOCUMENT
# Method: POST /api/upload
# Calls: ingestion/indexer.py -> index_document()
# ==========================================

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Upload PDF, DOCX or TXT only")

    try:
        content = await file.read(MAX_SIZE + 1)

        if len(content) > MAX_SIZE:
            raise HTTPException(413, "Maximum upload size is 5 MB")

        destination = UPLOAD_DIR / f"{uuid4().hex[:10]}_{filename}"
        destination.write_bytes(content)

        try:
            return index_document(str(destination))

        except Exception as error:
            traceback.print_exc()
            destination.unlink(missing_ok=True)
            raise HTTPException(
                status_code=502,
                detail=f"Indexing failed: {type(error).__name__}"
            ) from error

    finally:
        await file.close()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
