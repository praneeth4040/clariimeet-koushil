import json
import os
from models.session_model import SessionData

SESSION_FILE = "sessions/saved_sessions.json"
os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
if not os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "w") as f:
        json.dump([], f)

def save_session(session: SessionData):
    with open(SESSION_FILE, "r") as f:
        sessions = json.load(f)
    sessions.append(session.dict())
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def get_all_sessions():
    with open(SESSION_FILE, "r") as f:
        return json.load(f)