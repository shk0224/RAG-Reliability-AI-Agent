"""Read PDF, DOCX, and TXT documents."""
from pathlib import Path
from docx import Document
from pypdf import PdfReader

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def load_document(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    elif suffix == ".docx":
        text = "\n".join(p.text for p in Document(str(path)).paragraphs)
    elif suffix == ".txt":
        text = path.read_text(encoding="utf-8-sig")
    else:
        raise ValueError("Only PDF, DOCX and TXT are supported")
    if not text.strip():
        raise ValueError("No extractable text found (scanned PDFs require OCR)")
    return text
