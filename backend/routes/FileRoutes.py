from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from models import UserModel, FileModel, ChunkModel
from database import get_db
from schemas import FileResponse, FileListResponse
from utils.auth_utils import get_current_user
from utils.upload_utils import save_uploaded_file, get_file_type
from utils.file_utils import extract_text_from_file, file_helper
from utils.embedding_utils import generate_embedding

router = APIRouter(
    prefix = "/files",
    tags = ["Files"]
)


@router.post("/upload", response_model = FileResponse, status_code = status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...), # ... -> param is required in FastAPI
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_path, file_size = save_uploaded_file(file, current_user.id)
        file_type = get_file_type(file)

        extracted_text = extract_text_from_file(file_path, file_type)
        if extracted_text != "":
            summary = file_helper.summarize_document(extracted_text)

        # Create database record
        file_record = FileModel(
            user_id = current_user.id,
            file_name = file.filename,
            file_type = file_type,
            summary = summary
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        chunks = file_helper.split_text(extracted_text)
        chunk_records = []

        for chunk in chunks:
            embedding = generate_embedding(chunk)
            if embedding is not None:
                chunk_record = ChunkModel(file_id = file_record.id, text = chunk, embedding = embedding.tolist())
                chunk_records.append(chunk_record)

        db.bulk_save_objects(chunk_records)
        db.commit()

        return file_record

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
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    files = db.query(FileModel).filter(FileModel.user_id == current_user.id).all()
    return FileListResponse(files = files)

# Get file by file_id
@router.get("/{file_id}", response_model = FileResponse)
def get_file(
    file_id: int,
    current_user: UserModel = Depends(get_current_user),
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
