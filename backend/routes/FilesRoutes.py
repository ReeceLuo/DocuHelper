from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from models import Files, User
from database import get_db
from schemas import FileUploadResponse, FileListResponse
from utils.auth_utils import get_current_user
from utils.file_utils import save_uploaded_file, get_file_type

router = APIRouter(
    prefix = "/files",
    tags = ["Files"]
)


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Save file to disk
        file_path, file_size = save_uploaded_file(file, current_user.id)
        
        # Get file type
        file_type = get_file_type(file.filename)
        
        # Create database record
        db_file = Files(
            user_id=current_user.id,
            file_name=file.filename,  # Store original filename
            file_type=file_type,
            summary=None  # Will be populated later during document processing
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return db_file
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        # Handle any other errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/", response_model=FileListResponse)
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all files uploaded by the authenticated user
    
    Returns: List of all user's files
    """
    files = db.query(Files).filter(Files.user_id == current_user.id).all()
    return FileListResponse(files=files)


@router.get("/{file_id}", response_model=FileUploadResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific file by ID (only if it belongs to the current user)
    
    - **file_id**: The ID of the file to retrieve
    """
    file = db.query(Files).filter(
        Files.id == file_id,
        Files.user_id == current_user.id
    ).first()
    
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file