from fastapi import FastAPI
from contextlib import asynccontextmanager
from rag_agent.routers.files import router as upload_router
from rag_agent.routers.query import router as query_router
from rag_agent.routers.chat import router as chat_router

import os
from dotenv import load_dotenv
from vertexai import init

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")

    print(" PROJECT_ID (lifespan):", project_id)
    print(" LOCATION (lifespan):", location)

    if project_id and location:
        print(" Initializing Vertex AI from lifespan")
        init(project=project_id, location=location)
    else:
        print(" Vertex AI init skipped: Missing config")

    yield

app = FastAPI(lifespan=lifespan)

# Register routers
app.include_router(upload_router)
app.include_router(query_router)
app.include_router(chat_router)
