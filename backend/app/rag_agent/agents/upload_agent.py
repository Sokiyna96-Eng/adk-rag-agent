# backend/app/rag_agent/upload_agent.py

from google.adk.agents import Agent

# Import tools used during file ingestion
from rag_agent.tools.add_data import add_data
from rag_agent.tools.create_corpus import create_corpus
from rag_agent.tools.get_corpus_info import get_corpus_info
from rag_agent.tools.list_corpora import list_corpora
from rag_agent.tools.utils import check_corpus_exists  # if you later promote it as tool

upload_agent = Agent(
    name="upload_agent",  
    model="gemini-1.5-flash",  # Ideal for fast tool routing
    description="Handles file uploads, corpus creation, and document tracking.",
    tools=[
        list_corpora,
        create_corpus,
        add_data,
        get_corpus_info,
    ],
    instruction="""
You are the upload_agent. Your role is to manage PDF document uploads and connect them to the correct RAG corpus.

When a PDF is uploaded:
1. Check if the target corpus exists.
2. If not, create it using `create_corpus`.
3. Upload the file using `add_data`, passing the local path and GCS bucket.
4. After upload, call `get_corpus_info` to show updated file count and metadata.
5. Track `current_corpus` and `uploaded_files` in your tool_context.state:
    - state["current_corpus"] = corpus_name
    - state["uploaded_files"].append(filename)

You do not answer questions or query corpora. Your job is to prepare data for future retrieval and analysis.

You can also list available corpora using `list_corpora` if needed.
"""
)
