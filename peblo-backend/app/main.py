from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingest, quiz

app = FastAPI(title="Peblo Backend API", description="AI-powered learning platform backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(quiz.router, prefix="/api", tags=["quiz"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Peblo AI Backend"}
