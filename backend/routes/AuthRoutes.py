from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import User
from database import get_db
from schemas import UserCreate, UserResponse
from utils.auth_utils import get_password_hash


router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)


@router.post("/", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "This email is already registered."
        )
    
    password_hash = get_password_hash(user.password)
    new_user = User(
        name = user.name,
        email = user.email,
        password_hash = password_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 
    # since response_model is UserResponse, password will be omitted when instantiating


@router.post("/login")
def login():
    pass

