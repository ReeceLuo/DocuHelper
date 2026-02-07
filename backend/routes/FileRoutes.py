from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from models import FileModel, User
from database import get_db
from schemas import FileResponse, FileListResponse
from utils.auth_utils import get_current_user
from utils.upload_utils import save_uploaded_file, get_file_type
from utils.summary_utils import extract_text_from_file, summarizer

router = APIRouter(
    prefix = "/files",
    tags = ["Files"]
)


@router.post("/upload", response_model = FileResponse, status_code = status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...), # ... -> param is required in FastAPI
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_path, file_size = save_uploaded_file(file, current_user.id)
        file_type = get_file_type(file)

        extracted_text = extract_text_from_file(file_path, file_type)
        if extracted_text != "":
            summary = summarizer.summarize_document(extracted_text)

        # Create database record
        db_file = FileModel(
            user_id = current_user.id,
            file_name = file.filename,
            file_type = file_type,
            summary = summary
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error uploading file: {str(e)}"
        )

# Get list of all file information from a user
@router.get("/", response_model = FileListResponse)
def get_file_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    files = db.query(FileModel).filter(FileModel.user_id == current_user.id).all()
    return FileListResponse(files = files)

# Get file by file_id
@router.get("/{file_id}", response_model = FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    if file is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"File with id: {file_id} could not be found."
        )
    return file
