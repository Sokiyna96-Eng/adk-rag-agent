"""
Configuration settings for the RAG Agent.

These settings are used by the various RAG tools.
Vertex AI initialization is performed in the package's __init__.py
"""

import os

from dotenv import load_dotenv

# # Load environment variables (this is redundant if __init__.py is imported first,
# # but included for safety when importing config directly)

# # Vertex AI settings (support both standard and ADK keys)
# PROJECT_ID = os.environ.get("PROJECT_ID") 
# LOCATION = os.environ.get("LOCATION") 

# print("✅ PROJECT_ID:", os.environ.get("PROJECT_ID"))
# print("✅ LOCATION:", os.environ.get("LOCATION"))


from dotenv import load_dotenv
from pathlib import Path

# Load from the rag_agent/.env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

PROJECT_ID = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("LOCATION") or os.getenv("GOOGLE_CLOUD_LOCATION")

print("✅ FINAL PROJECT_ID:", PROJECT_ID)
print("✅ FINAL LOCATION:", LOCATION)


# RAG settings
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_TOP_K = 3
DEFAULT_DISTANCE_THRESHOLD = 0.5
DEFAULT_EMBEDDING_MODEL = "publishers/google/models/text-embedding-005"
DEFAULT_EMBEDDING_REQUESTS_PER_MIN = 1000
