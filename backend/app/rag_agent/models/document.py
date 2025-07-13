import os
import hashlib
import logging
from typing import Optional, Tuple

from pydantic import BaseModel
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from fastapi import HTTPException, UploadFile


class DocumentModel(BaseModel):
    """Document model for processing and storage."""

    page_content: str
    filename: str
    content_type: str
    metadata: Optional[dict] = {}

    def generate_digest(self):
        """Generate MD5 hash of document content."""
        hash_obj = hashlib.md5(self.page_content.encode())
        return hash_obj.hexdigest()


def validate_document(file: UploadFile) -> bool:
    """Validate if the file type is supported.

    Args:
        file: The uploaded file to validate

    Returns:
        bool: True if file type is supported, False otherwise
    """
    supported_types: set[str] = {
        "text/plain",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return file.content_type in supported_types


def get_file_extension(filename):
    """
    Gets the file extension from a given filename.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The file extension, including the leading dot (e.g., ".txt").
             If no extension is found, an empty string is returned.
    """
    return os.path.splitext(filename)[-1].lower()


def extract_text(file: str) -> Tuple[str, str]:
    """Extract text content from a file.

    Args:
        file: Path to the file

    Returns:
        Tuple[str, str]: Extracted text and content type

    Raises:
        HTTPException: If file processing fails
    """
    content_type = get_file_extension(file)
    logging.info(f"the file type is {content_type}")
    try:
        if content_type == ".txt":
            with open(file, "r", encoding="utf-8") as f:
                return f.read(), content_type

        elif content_type == ".pdf":
            with open(file, "rb") as f:
                pdf_reader = PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text, content_type

        elif content_type == ".docx":
            doc = DocxDocument(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text, content_type

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
