from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import tempfile
import traceback

from google.adk.agents.invocation_context import InvocationContext  # ✅ Correct import
from google.adk.tools.tool_context import ToolContext
from rag_agent.tools.add_data import add_data

router = APIRouter()

GCS_BUCKET = os.getenv("GCS_BUCKET")

@router.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    corpus_name: str = Form("earthwork")
):
    try:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # ✅ Construct minimal InvocationContext manually
        invocation_context = InvocationContext()
        tool_context = ToolContext(invocation_context)

        print("📂 Uploading to corpus:", corpus_name)
        print("📄 Temp file:", tmp_path)
        print("🪣 GCS_BUCKET:", GCS_BUCKET)
        print("🧠 ToolContext State:", tool_context.state)

        response = add_data(
            corpus_name=corpus_name,
            paths=[],
            tool_context=tool_context,
            local_files=[tmp_path],
            gcs_bucket=GCS_BUCKET,
        )

        print("📦 add_data response:", response)
        return JSONResponse(content=response)

    except Exception as e:
        print("❌ Exception during /upload_pdf:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
