from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine

app = FastAPI(title="AI Resume Analyzer")

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"Database": "Connected"}