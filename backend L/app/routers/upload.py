import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter()

@router.post("/upload-xray")
async def upload_xray(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed")

    # Generate a unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{filename}"

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": filename, "message": "X-ray uploaded successfully!"}