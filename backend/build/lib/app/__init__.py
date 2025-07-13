from dotenv import load_dotenv
import os

# Load .env values
load_dotenv()

# Print to debug
print("🔁 LOADED .env early in __init__.py")
print("✅ GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# Required fields
PROJECT_ID = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("LOCATION") or os.getenv("GOOGLE_CLOUD_LOCATION")

print("✅ FINAL PROJECT_ID:", PROJECT_ID)
print("✅ FINAL LOCATION:", LOCATION)

# Now import Vertex after env is loaded
from vertexai import init

if PROJECT_ID and LOCATION:
    print("🚀 Calling vertexai.init()...")
    init(project=PROJECT_ID, location=LOCATION)
else:
    print("❌ vertexai.init() skipped: PROJECT_ID or LOCATION missing")
