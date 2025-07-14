from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

from rag_agent.agent import root_agent

router = APIRouter()

runner = Runner(
    agent=root_agent,
    session_service=InMemorySessionService(),
    app_name="rag_app"
)

@router.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message")

        if not user_message:
            return JSONResponse(status_code=400, content={"error": "Missing 'message' field"})

        content = Content(text=user_message)

        result = await runner.run_async(content)
        return {"response": result.final_response.text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
