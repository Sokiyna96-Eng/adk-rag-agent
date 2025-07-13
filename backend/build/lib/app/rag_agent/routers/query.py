from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from rag_agent.tools.rag_query import rag_query  # This is your RAG tool



# Create router to register with FastAPI app
router = APIRouter()

# Dummy context to simulate tool execution
class DummyContext:
    def __init__(self):
        self.state = {}

@router.post("/query")
async def query_rag(
    query: str = Form(...),              
    corpus_name: str = Form("earthwork") 
):
    tool_context = DummyContext()

    result = rag_query(
        corpus_name=corpus_name,
        query=query,
        tool_context=tool_context,
    )

    return JSONResponse(content=result)
