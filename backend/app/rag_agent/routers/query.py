from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import uuid
import traceback

from app.rag_agent.agent import root_agent

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

        # Add debugging: check if corpus exists before querying
        from rag_agent.tools.utils import check_corpus_exists
        from rag_agent.tools.get_corpus_info import get_corpus_info
        from rag_agent.tools.list_corpora import list_corpora
        from google.adk.tools.tool_context import ToolContext
        
        # Create a temporary tool context for debugging
        temp_context = ToolContext()
        temp_context.state = {}
        
        print(f"🔍 DEBUGGING: Checking corpus '{corpus_name}'...")
        
        # First, list all available corpora
        try:
            all_corpora = list_corpora()
            print(f"📋 Available corpora: {all_corpora}")
        except Exception as e:
            print(f"❌ Error listing corpora: {str(e)}")
        
        # Check if our target corpus exists
        corpus_exists = check_corpus_exists(corpus_name, temp_context)
        print(f"📁 Corpus '{corpus_name}' exists: {corpus_exists}")
        
        if corpus_exists:
            try:
                corpus_info = get_corpus_info(corpus_name, temp_context)
                print(f"📊 Corpus info: {corpus_info}")
                file_count = corpus_info.get('file_count', 0)
                print(f"📄 Files in corpus: {file_count}")
                
                if file_count == 0:
                    print(f"⚠️  WARNING: Corpus '{corpus_name}' exists but has NO files!")
                    print("   This means files were uploaded to GCS but never added to the corpus.")
                    print("   The upload_agent may not have called add_data properly.")
                else:
                    print(f"✅ Corpus '{corpus_name}' has {file_count} files")
            except Exception as e:
                print(f"❌ Error getting corpus info: {str(e)}")
        else:
            print(f"❌ WARNING: Corpus '{corpus_name}' does not exist!")
            print("   This is why you're getting null responses.")
            print("   Please upload files first to create and populate the corpus.")

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

        # Add debugging to see if agent called rag_query tool
        print("🔍 DEBUGGING: Checking if agent called rag_query tool...")
        
        # Check the response events to see what tools were called
        tool_calls = []
        for event in response_events:
            if hasattr(event, 'tool_calls') and event.tool_calls:
                for tool_call in event.tool_calls:
                    tool_calls.append({
                        'tool_name': tool_call.name,
                        'arguments': tool_call.args
                    })
        
        if tool_calls:
            print(f"📋 Agent called {len(tool_calls)} tools:")
            for i, tool_call in enumerate(tool_calls):
                print(f"  {i+1}. {tool_call['tool_name']}: {tool_call['arguments']}")
        else:
            print("❌ Agent did not call any tools!")
            print("   This is why the response is null - the agent should have called rag_query")
        
        if not final_response:
            print("❌ WARNING: final_response is None!")
            print("   This means the agent didn't provide a proper response.")
            print("   The agent should have called rag_query and provided an answer based on the results.")

        return JSONResponse(content={
            "query": query,
            "response": final_response,
            "session_id": session_id
        })

    except Exception as e:
        print(" Exception during runner.run:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/corpus-status/{corpus_name}")
async def get_corpus_status(corpus_name: str):
    """Debug endpoint to check corpus status"""
    try:
        from rag_agent.tools.utils import check_corpus_exists
        from rag_agent.tools.get_corpus_info import get_corpus_info
        from rag_agent.tools.list_corpora import list_corpora
        from google.adk.tools.tool_context import ToolContext
        
        temp_context = ToolContext()
        temp_context.state = {}
        
        # Check if corpus exists
        corpus_exists = check_corpus_exists(corpus_name, temp_context)
        
        if corpus_exists:
            corpus_info = get_corpus_info(corpus_name, temp_context)
            return JSONResponse(content={
                "corpus_name": corpus_name,
                "exists": True,
                "info": corpus_info
            })
        else:
            # List all available corpora
            all_corpora = list_corpora()
            return JSONResponse(content={
                "corpus_name": corpus_name,
                "exists": False,
                "available_corpora": all_corpora
            })
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
