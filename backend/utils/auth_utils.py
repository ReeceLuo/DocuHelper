from fastapi import Depends, HTTPException, status
from pwdlib import PasswordHash
from datetime import timedelta
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.orm.events import SessionEvents

from models import User
from config import settings
from database import get_db

"""
Password
"""
pwd_password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return pwd_password_hash.hash(password)

def verify_password(password, password_hash):
    return pwd_password_hash.verify(password, password_hash)


"""
JWT
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login") 
# extracts bearer token from Authorization header and enforces the bearer token format
# bearer token - access token for whoever "bears" the token

SECRET_KEY = settings.JWT_SIGNING_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

# Helper to authenticate user in login route before issuing JWT
def authenticate_user(name: str, password: str, db: Session):
    user = db.query(User).filter(User.name == name).first()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes = 15))

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm = ALGORITHM
    )

def get_user_from_db(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials.",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Convert to int if it's a string (some JWT libraries encode as string)
        user_id = int(user_id) if isinstance(user_id, str) else user_id
    except (JWTError, ValueError, TypeError):
        raise credentials_exception
    
    user = get_user_from_db(user_id, db)
    if user is None:
        raise credentials_exception

    return user