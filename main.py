
import os
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from adk_companion.firestore_session_service import FirestoreSessionService

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Instantiate our custom Firestore session service
session_service = FirestoreSessionService(collection="adk_companion_sessions")

# Example allowed origins for CORS
ALLOWED_ORIGINS = ["*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Call the function to get the FastAPI app instance
# Pass the session_service object directly to override the default.
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service=session_service,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# You can add more FastAPI routes or configurations below if needed
# Example:
# @app.get("/hello")
# async def read_root():
#     return {"Hello": "World"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
