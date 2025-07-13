"""
Tool for adding new data sources to a Vertex AI RAG corpus, including local PDF uploads.
"""

import os
import re
import uuid
from typing import List, Optional
from dotenv import load_dotenv

from google.cloud import storage
from google.adk.tools.tool_context import ToolContext
from vertexai import rag



from ..config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
)
from .utils import check_corpus_exists, get_corpus_resource_name

load_dotenv()
GCS_BUCKET = os.getenv("GCS_BUCKET")

def upload_file_to_gcs(local_file_path: str, bucket_name: str, destination_folder: str = "uploads") -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    file_name = os.path.basename(local_file_path)
    unique_name = f"{uuid.uuid4()}_{file_name}"
    blob_path = f"{destination_folder}/{unique_name}"
    blob = bucket.blob(blob_path)

    blob.upload_from_filename(local_file_path)
    return f"gs://{bucket.name}/{blob_path}"

def add_data(
    corpus_name: str,
    paths: Optional[List[str]],
    tool_context: ToolContext,
    local_files: Optional[List[str]] = None,
    gcs_bucket: Optional[str] = None,
) -> dict:
    gcs_bucket = gcs_bucket or GCS_BUCKET

    if local_files and not gcs_bucket:
        return {
            "status": "error",
            "message": "You must provide a GCS bucket to upload local files, either by passing it in or setting GCS_BUCKET in your .env file.",
            "corpus_name": corpus_name,
            "paths": paths or [],
        }





def add_data(
    corpus_name: str,
    paths: Optional[List[str]],
    tool_context: ToolContext,
    local_files: Optional[List[str]] = None,
    gcs_bucket: Optional[str] = None,
) -> dict:
    """
    Add new data sources (URLs or local PDFs) to a Vertex AI RAG corpus.

    Args:
        corpus_name (str): Target corpus.
        paths (List[str]): URLs or GCS paths.
        tool_context (ToolContext): Tool context for the corpus.
        local_files (List[str], optional): Paths to user-uploaded local files (e.g., PDFs).
        gcs_bucket (str, optional): Target GCS bucket for uploads.

    Returns:
        dict: Status and info on added documents.
    """
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
            "corpus_name": corpus_name,
            "paths": paths or [],
        }

    if paths is None:
        paths = []

    # Handle local PDF files (user-uploaded)
    if local_files and gcs_bucket:
        for file_path in local_files:
            try:
                gcs_path = upload_file_to_gcs(file_path, gcs_bucket)
                paths.append(gcs_path)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to upload {file_path} to GCS: {str(e)}",
                    "corpus_name": corpus_name,
                    "paths": paths,
                }

    # Validate and normalize all paths
    validated_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (Not a valid string)")
            continue

        # Convert Google Docs/Sheets/Slides URLs
        docs_match = re.match(
            r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)",
            path
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            conversions.append(f"{path} → {drive_url}")
            continue

        # Convert Google Drive URL
        drive_match = re.match(
            r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)",
            path
        )
        if drive_match:
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} → {drive_url}")
            continue

        # Accept GCS path as-is
        if path.startswith("gs://"):
            validated_paths.append(path)
            continue

        # Unknown format
        invalid_paths.append(f"{path} (Invalid format)")

    if not validated_paths:
        return {
            "status": "error",
            "message": "No valid paths provided. Please provide Drive URLs, GCS paths, or upload PDFs.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths,
        }

    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            ),
        )

        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )

        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        return {
            "status": "success",
            "message": f"Successfully added {import_result.imported_rag_files_count} file(s) to corpus '{corpus_name}'"
                       + (" (Converted Google Docs URLs to Drive format)" if conversions else ""),
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validated_paths,
            "invalid_paths": invalid_paths,
            "conversions": conversions,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error adding data to corpus: {str(e)}",
            "corpus_name": corpus_name,
            "paths": paths,
        }
