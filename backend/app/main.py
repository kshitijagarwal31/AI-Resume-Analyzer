from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine, Base
from app import models
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Resume Analyzer & Parser")
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"Database": "Connected"}