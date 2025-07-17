"""
Tool for querying Vertex AI RAG corpora and retrieving relevant information.
"""

import logging
import traceback

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
)
from .utils import check_corpus_exists, get_corpus_resource_name


def rag_query(
    corpus_name: str,
    query: str,
    tool_context: ToolContext,
) -> dict:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.

    Args:
        corpus_name (str): The name of the corpus to query. If empty, uses the current corpus.
        query (str): The text query to search in the corpus.
        tool_context (ToolContext): Tool context, including session state.

    Returns:
        dict: Query status, message, and results.
    """
    try:
        print(f"📡 Starting RAG query: '{query}'")
        print(f"📁 Target corpus: '{corpus_name}'")

        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
                "query": query,
                "corpus_name": corpus_name,
            }

        corpus_resource_name = get_corpus_resource_name(corpus_name)

        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        print("🔍 Calling rag.retrieval_query...")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(rag_corpus=corpus_resource_name)
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": getattr(ctx_group, "source_uri", ""),
                    "source_name": getattr(ctx_group, "source_display_name", ""),
                    "text": getattr(ctx_group, "text", ""),
                    "score": getattr(ctx_group, "score", 0.0),
                }
                results.append(result)

        if not results:
            return {
                "status": "warning",
                "message": f"No relevant results found in corpus '{corpus_name}' for query: '{query}'",
                "query": query,
                "corpus_name": corpus_name,
                "results": [],
                "results_count": 0,
            }

        return {
            "status": "success",
            "message": f"Successfully queried corpus '{corpus_name}'",
            "query": query,
            "corpus_name": corpus_name,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"❌ Exception during rag_query: {str(e)}"
        logging.error(error_msg)
        traceback.print_exc()
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "corpus_name": corpus_name,
        }
