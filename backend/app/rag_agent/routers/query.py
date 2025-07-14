# backend/app/rag_agent/routers/query.py

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from rag_agent.agent import root_agent  # your main Gemini agent

router = APIRouter()

runner = Runner(
    agent=root_agent,
    app_name="rag-app",
    session_service=InMemorySessionService()
)

@router.post("/query")
async def query_endpoint(
    query: str = Form(...),
    corpus_name: str = Form("earthwork")
):
    try:
        response = runner.run(
            prompt=f"Query the corpus named '{corpus_name}' for the following: {query}",
            tool_context_inputs={"corpus_name": corpus_name}
        )
        return JSONResponse(content={"query": query, "response": response})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
