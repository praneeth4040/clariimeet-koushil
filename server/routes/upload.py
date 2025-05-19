from fastapi import APIRouter, File, UploadFile
import os

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/")
async def upload_audio(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    return {
        "filename": file.filename,
        "file_path": file_location
    }