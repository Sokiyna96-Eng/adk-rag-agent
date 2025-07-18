from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.rag_agent.routers.files import router as upload_router
from app.rag_agent.routers.query import router as query_router
from app.rag_agent.routers.chat import router as chat_router

import os
from dotenv import load_dotenv
from vertexai import init


print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")

    print(" PROJECT_ID (lifespan):", project_id)
    print(" LOCATION (lifespan):", location)

    if project_id and location:
        print(" Initializing Vertex AI...")
        init(project=project_id, location=location)
    else:
        print(" Skipping Vertex AI init (missing config)")

    yield

#  This must match the location in Dockerfile: `main:app`
app = FastAPI(lifespan=lifespan)

#  Basic health check (needed for Cloud Run to verify container started)
@app.get("/")
def health_check():
    return {"status": "ok"}

# Register routes
app.include_router(upload_router)
app.include_router(query_router)
app.include_router(chat_router)
