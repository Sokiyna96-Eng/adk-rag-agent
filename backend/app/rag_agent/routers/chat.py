from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from google.adk.runtime.runner import Runner
from google.adk.runtime.context import InMemorySessionService
from google.adk.types import Content

from rag_agent.agent import root_agent

router = APIRouter()

# Create an agent runner with in-memory session support
runner = Runner(agent=root_agent, session_service=InMemorySessionService())

@router.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message")

        if not user_message:
            return JSONResponse(status_code=400, content={"error": "Missing 'message' field"})

        # Wrap user message in ADK Content
        content = Content(text=user_message)

        # Call the agent via Runner
        result = await runner.run_async(content)

        return {"response": result.final_response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
