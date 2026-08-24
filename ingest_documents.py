# ingest_documents.py
"""
Script to ingest documents into the vector store.
Run this before starting the application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.ingest import main

if __name__ == "__main__":
    main()
