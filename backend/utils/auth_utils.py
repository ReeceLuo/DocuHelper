from fastapi import Depends, HTTPException, status
from pwdlib import PasswordHash
from datetime import timedelta
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer

from config import get_db, settings

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
oauth2_scheme = OAuth2PasswordBearer(tokenURL = "token")

SECRET_KEY = settings.JWT_SIGNING_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

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

def get_current_user(token: str = Depends(oauth2_scheme)):
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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_from_db(user_id)
    if user is None:
        raise credentials_exception

    return user