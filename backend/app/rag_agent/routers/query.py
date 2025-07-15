from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import traceback

from rag_agent.agent import root_agent

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
        user_message = (
            f"You are working with a RAG corpus named '{corpus_name}'. "
            f"Please answer the following query using documents from that corpus:\n\n{query}"
        )

        print("🟡 Received query:", query)
        print("🟢 Sending to runner...")

        response_events = runner.run(
            user_id="rag_user",
            session_id="query_session_default",
            new_message=Content(role="user", parts=[Part(text=user_message)])
        )

        print("✅ Agent responded. Checking for final response...")

        final_response = None
        for event in response_events:
            if event.is_final_response():
                final_response = event.content.parts[0].text

        return JSONResponse(content={
            "query": query,
            "response": final_response
        })

    except Exception as e:
        print("🔴 Exception during runner.run:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
