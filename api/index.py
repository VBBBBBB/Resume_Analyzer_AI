# api/index.py
import sys
import os

# Ensure the backend directory is in the path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app as backend_app
from fastapi import FastAPI

app = FastAPI()

# Mount the existing FastAPI app on /api
app.mount("/api", backend_app)

# Root for the /api endpoint
@app.get("/api")
def root():
    return {"message": "Resume Analyzer API on Vercel is ready!"}
