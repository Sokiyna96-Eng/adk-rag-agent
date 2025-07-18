import os
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from google.cloud import storage


from app.rag_agent.agents.upload_agent import upload_agent
from app.rag_agent.models.document import validate_document

router = APIRouter()

UPLOAD_DIR = "./api_data/file_locker/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global persistent session service
session_service = InMemorySessionService()

# Fixed app and user identifiers 
APP_NAME = "rag_agent"
USER_ID = "rag_user"
SESSION_ID = "upload_session_default"

@router.post("/upload/")
async def file_upload(file: UploadFile = File(...)):
    if not validate_document(file):
        raise HTTPException(status_code=400, detail="Invalid document type")

    try:
        # Save locally (optional)
        fname = os.path.join(UPLOAD_DIR, file.filename)
        with open(fname, "wb") as f:
            while content := file.file.read(1024 * 1024):
                f.write(content)

        # Upload to GCS
        storage_client = storage.Client()
        bucket_name = os.getenv("GCS_BUCKET", "my-rag-upload-bucket")
        gcs_path = f"uploads/{uuid.uuid4()}/{file.filename}"
        blob = storage_client.bucket(bucket_name).blob(gcs_path)

        with open(fname, "rb") as f:
            blob.upload_from_file(f, content_type="application/pdf")

        gcs_uri = f"gs://{bucket_name}/{gcs_path}"
        print(f"Uploaded to GCS: {gcs_uri}")

        # Create agent session
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
            f"Please add the following GCS file to the 'earthwork' corpus:\n"
            f"GCS URI: {gcs_uri}\n"
            f"File name: {file.filename}\n"
            f"Use the add_data tool with paths=[{gcs_uri}] and corpus_name='earthwork'"
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
            "message": f"Uploaded {file.filename} to GCS",
            "gcs_uri": gcs_uri,
            "agent_response": final_response
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multiupload/")
async def multi_file_upload(files: list[UploadFile] = File(...)):
    gcs_uris = []

    try:
        for file in files:
            if not validate_document(file):
                raise HTTPException(status_code=400, detail=f"Invalid file: {file.filename}")

            # Save locally (optional)
            fname = os.path.join(UPLOAD_DIR, file.filename)
            with open(fname, "wb") as f:
                while content := file.file.read(1024 * 1024):
                    f.write(content)

            # Upload to GCS
            storage_client = storage.Client()
            bucket_name = os.getenv("GCS_BUCKET", "my-rag-upload-bucket")
            gcs_path = f"uploads/{uuid.uuid4()}/{file.filename}"
            blob = storage_client.bucket(bucket_name).blob(gcs_path)

            with open(fname, "rb") as f:
                blob.upload_from_file(f, content_type="application/pdf")

            gcs_uri = f"gs://{bucket_name}/{gcs_path}"
            print(f"Uploaded to GCS: {gcs_uri}")
            gcs_uris.append(gcs_uri)

        # Create agent session
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
            f"Please add the following GCS files to the 'earthwork' corpus:\n"
            f"GCS URIs:\n" + "\n".join([f"- {uri}" for uri in gcs_uris]) + "\n"
            f"Use the add_data tool with paths={gcs_uris} and corpus_name='earthwork'"
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
            "message": f"Uploaded {len(gcs_uris)} files to GCS",
            "gcs_uris": gcs_uris,
            "agent_response": final_response
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
