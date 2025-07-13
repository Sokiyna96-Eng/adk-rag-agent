"""
RAG Tools package for interacting with Vertex AI RAG corpora.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔁 LOADED .env early in __init__.py")
print("✅ PROJECT_ID (early):", os.environ.get("PROJECT_ID"))
print("✅ LOCATION (early):", os.environ.get("LOCATION"))


from .add_data import add_data
from .create_corpus import create_corpus
from .delete_corpus import delete_corpus
from .delete_document import delete_document
from .get_corpus_info import get_corpus_info
from .list_corpora import list_corpora
from .rag_query import rag_query
from .utils import (
    check_corpus_exists,
    get_corpus_resource_name,
    set_current_corpus,
)

__all__ = [
    "add_data",
    "create_corpus",
    "list_corpora",
    "rag_query",
    "get_corpus_info",
    "delete_corpus",
    "delete_document",
    "check_corpus_exists",
    "get_corpus_resource_name",
    "set_current_corpus",
]
