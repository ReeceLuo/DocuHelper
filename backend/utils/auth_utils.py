from pwdlib import PasswordHash
from datetime import timedelta
from jose import jwt
from typing import Optional
from datetime import datetime, timezone

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
SECRET_KEY = settings.JWT_SIGNING_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes = 15))