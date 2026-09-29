import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.cv_routes import router as cv_router


app = FastAPI(
    title="AI CV Job Matcher API",
    version="1.0.0"
)


frontend_url = os.getenv("FRONTEND_URL")


allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_url:
    allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(cv_router)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "AI CV Job Matcher API is running"
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "status": "healthy"
    }