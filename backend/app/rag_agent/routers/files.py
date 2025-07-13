import os
import uuid
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from google.adk.runtime.runner import Runner
from google.adk.runtime.context import InMemorySessionService

from rag_agent.agents.upload_agent import upload_agent  # <-- Make sure this agent is defined
from rag_agent.models.document import validate_document
# from ..services.embeddings import DocumentHandler
# from ..core.threading_handler import BackgroundThread

router = APIRouter()

# Setup background processor
document_handler = DocumentHandler()
doc_bg_thread = BackgroundThread(handler=document_handler)

# Upload destination
UPLOAD_DIR = "./api_data/file_locker/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Single file upload
@router.post("/upload/")
async def file_upload(file: UploadFile = File(...)):
    if not validate_document(file):
        raise HTTPException(status_code=400, detail="Invalid document type")

    try:
        fname = os.path.join(UPLOAD_DIR, file.filename)
        with open(fname, "wb") as f:
            while content := file.file.read(1024 * 1024):
                f.write(content)
        document_handler.add_task(fname)

        # Agent logic
        runner = Runner(session_service=InMemorySessionService())
        tool_context_inputs = {
            "corpus_name": "earthwork",
            "local_files": [fname],
        }

        response = runner.run(
            agent=upload_agent,
            prompt=f"I've uploaded a file named {file.filename}. Please add it to the corpus.",
            tool_context_inputs=tool_context_inputs,
        )

        return JSONResponse(content={"message": f"Uploaded {file.filename}", "agent_response": response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Multiple file upload
@router.post("/multiupload/")
async def multi_file_upload(files: list[UploadFile] = File(...)):
    uploaded = []

    try:
        for file in files:
            if not validate_document(file):
                raise HTTPException(status_code=400, detail=f"Invalid file: {file.filename}")
            
            fname = os.path.join(UPLOAD_DIR, file.filename)
            with open(fname, "wb") as f:
                while content := file.file.read(1024 * 1024):
                    f.write(content)
            document_handler.add_task(fname)
            uploaded.append(fname)

        # Call agent with all files
        runner = Runner(session_service=InMemorySessionService())
        tool_context_inputs = {
            "corpus_name": "earthwork",
            "local_files": uploaded,
        }

        response = runner.run(
            agent=upload_agent,
            prompt=f"I've uploaded multiple files: {uploaded}. Please add them to the corpus.",
            tool_context_inputs=tool_context_inputs,
        )

        return JSONResponse(content={"message": f"Uploaded {len(uploaded)} files.", "agent_response": response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
