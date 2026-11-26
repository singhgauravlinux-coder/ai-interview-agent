from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db import engine
from app.config import settings
from app.api import router

app = FastAPI(title="AI Interview Agent API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status":"ok","service":"ai-interview-agent"}

@app.get("/ready")
def ready():
    # Readiness verifies that the API can reach its primary datastore.
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status":"ready","database":"ok"}
