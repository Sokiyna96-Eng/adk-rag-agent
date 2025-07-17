from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import uuid
import traceback

from rag_agent.agent import root_agent

router = APIRouter()

# Shared runner and session service
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="rag-app",
    session_service=session_service
)

@router.post("/query")
async def query_endpoint(
    request: Request,
    query: str = Form(...),
    corpus_name: str = Form("earthwork")
):
    try:
        user_id = "rag_user"  

        # Get or create a session ID — here we generate one per request
        session_id = f"query-session-{uuid.uuid4()}"
        session_service.create_session(
            app_name="rag-app",
            user_id=user_id,
            session_id=session_id
        )

        user_message = (
            f"You are working with a RAG corpus named '{corpus_name}'. "
            f"Please answer the following query using documents from that corpus:\n\n{query}"
        )

        print(" New query received:")
        print("", query)
        print(" Corpus:", corpus_name)
        print(" Session ID:", session_id)

        response_events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part(text=user_message)])
        )

        final_response = None
        for event in response_events:
            if event.is_final_response():
                final_response = event.content.parts[0].text

        print(" Final response:", final_response)

        return JSONResponse(content={
            "query": query,
            "response": final_response,
            "session_id": session_id
        })

    except Exception as e:
        print(" Exception during runner.run:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
