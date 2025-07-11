import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_agent.tools.add_data import add_data

load_dotenv()
GCS_BUCKET = os.getenv("GCS_BUCKET")

# Dummy ToolContext replacement
class DummyContext:
    def __init__(self):
        self.state = {}

tool_context = DummyContext()

response = add_data(
    corpus_name="earthwork",
    paths=[],
    tool_context=tool_context,
    local_files=["C:\\Users\\Sokyn\\Downloads\\stm32l476rg.pdf"],  
    gcs_bucket=GCS_BUCKET
)

print(response)
