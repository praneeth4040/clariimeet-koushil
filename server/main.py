from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import upload, transcribe, summarize, session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(transcribe.router, prefix="/transcribe", tags=["Transcription"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(session.router, prefix="/sessions", tags=["Session Management"])