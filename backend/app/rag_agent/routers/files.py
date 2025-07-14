import os
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from rag_agent.agents.upload_agent import upload_agent
from rag_agent.models.document import validate_document

router = APIRouter()

UPLOAD_DIR = "./api_data/file_locker/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global persistent session service
session_service = InMemorySessionService()

# Fixed app and user identifiers (can be extended later to support multi-user)
APP_NAME = "rag_agent"
USER_ID = "rag_user"
SESSION_ID = "upload_session_default"

@router.post("/upload/")
async def file_upload(file: UploadFile = File(...)):
    if not validate_document(file):
        raise HTTPException(status_code=400, detail="Invalid document type")

    try:
        fname = os.path.join(UPLOAD_DIR, file.filename)
        with open(fname, "wb") as f:
            while content := file.file.read(1024 * 1024):
                f.write(content)

        # Ensure session exists
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )

        runner = Runner(
            agent=upload_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        message = (
            f"I've uploaded a file named {file.filename}. "
            f"Please add it to the 'earthwork' corpus from path: {fname}."
        )

        response_events = runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=Content(role="user", parts=[Part(text=message)])
        )

        final_response = None
        for event in response_events:
            if event.is_final_response():
                final_response = event.content.parts[0].text

        return JSONResponse(content={
            "message": f"Uploaded {file.filename}",
            "agent_response": final_response
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            uploaded.append(fname)

        # Ensure session exists
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )

        runner = Runner(
            agent=upload_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        message = (
            f"I've uploaded {len(uploaded)} files. Please add them to the 'earthwork' corpus. "
            f"Files:\n" + "\n".join(uploaded)
        )

        response_events = runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=Content(role="user", parts=[Part(text=message)])
        )

        final_response = None
        for event in response_events:
            if event.is_final_response():
                final_response = event.content.parts[0].text

        return JSONResponse(content={
            "message": f"Uploaded {len(uploaded)} files",
            "agent_response": final_response
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
