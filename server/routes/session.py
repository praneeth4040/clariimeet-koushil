from fastapi import APIRouter, Body
from models.session_model import SessionData
from database.db import save_session, get_all_sessions

router = APIRouter()

@router.post("/save")
def save(session: SessionData):
    save_session(session)
    return {"status": "Session saved"}

@router.get("/all")
def get_sessions():
    return get_all_sessions()