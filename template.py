
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Folders
folders = [
    "ingestion",
    "nodes",
    "tools",
    "eval",
    "templates",
    "static",
    "data",
    "data/documents",
]

# Files
files = [
    "app.py",
    "backend.py",
    "template.py",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "README.md",

    "ingestion/__init__.py",
    "ingestion/loader.py",
    "ingestion/chunker.py",
    "ingestion/indexer.py",

    "nodes/__init__.py",
    "nodes/document_search.py",
    "nodes/relevance_check.py",
    "nodes/answer_generation.py",
    "nodes/answer_verification.py",

    "tools/__init__.py",
    "tools/document_search_tool.py",
    "tools/relevance_check_tool.py",
    "tools/answer_generation_tool.py",
    "tools/answer_verification_tool.py",

    "eval/testset.json",
    "eval/run_eval.py",

    "templates/index.html",
    "static/style.css",
    "static/script.js",
]

# Create folders
for folder in folders:
    folder_path = PROJECT_ROOT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"Folder ready: {folder}")

# Create files
for file in files:
    file_path = PROJECT_ROOT / file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch(exist_ok=True)
    print(f"File ready: {file}")

print("\nProject structure created successfully!")
