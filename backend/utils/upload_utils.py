import os
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from config import settings
from datetime import datetime


def get_file_type(filename: str) -> str:
    return filename.split(".")[-1].lower() if "." in filename else "unknown"

def validate_file_type(filename: str) -> bool:
    type = get_file_type(filename)
    return type in settings.ALLOWED_FILE_TYPES

# Create upload directory for user (if it does not exist)
def create_user_upload_dir(user_id: int) -> Path:
    user_dir = Path(settings.UPLOAD_DIR) / str(user_id)
    user_dir.mkdir(parents = True, exist_ok = True) # exist_ok -> no exception if alr exists
    return user_dir

# Save the uploaded file to disk
def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[Path, int]:
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"File type not allowed. Allowed types: {", ".join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    user_dir = create_user_upload_dir(user_id)

    # Add timestamp to file name to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{file.filename}"
    file_path = user_dir / new_filename

    # Read and save file
    content = file.file.read()
    file_size = len(content)

    # Check file size
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Max file size exceeded. Must be under {settings.MAX_FILE_SIZE_MB}MB"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path, file_size
