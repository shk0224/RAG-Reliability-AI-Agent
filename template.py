from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Folder structure
folders = [
    "tools",
    "ingestion",
    "templates",
    "static",
    "data/documents",
    "eval",
]

# File structure
files = [
    "app.py",
    "backend.py",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "README.md",
    "tools/__init__.py",
    "tools/document_search_tool.py",
    "tools/relevance_check_tool.py",
    "tools/answer_generation_tool.py",
    "tools/answer_verification_tool.py",
    "ingestion/__init__.py",
    "ingestion/loader.py",
    "ingestion/chunker.py",
    "ingestion/indexer.py",
    "templates/index.html",
    "static/style.css",
    "static/script.js",
    "eval/run_eval.py",
    "eval/testset.json",
]

# Create folders
for folder in folders:
    folder_path = PROJECT_ROOT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"Folder created: {folder}")

# Create files
for file in files:
    file_path = PROJECT_ROOT / file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch(exist_ok=True)
    print(f"File ready: {file}")

print("\nRAG Reliability AI Agent project structure created successfully!")
