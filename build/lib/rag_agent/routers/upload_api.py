from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import tempfile
from dotenv import load_dotenv
from rag_agent.tools.add_data import add_data

# Use dummy ToolContext
class DummyContext:
    def __init__(self):
        self.state = {}

load_dotenv()
GCS_BUCKET = os.getenv("GCS_BUCKET")

app = FastAPI()

@app.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    corpus_name: str = Form("earthwork")  # or make it user-defined
):
    try:
        # Save to temp file
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Call add_data
        tool_context = DummyContext()
        response = add_data(
            corpus_name=corpus_name,
            paths=[],
            local_files=[tmp_path],
            gcs_bucket=GCS_BUCKET,
            tool_context=tool_context,
        )

        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
