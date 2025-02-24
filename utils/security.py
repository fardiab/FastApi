import jwt
import datetime
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.database import get_db
from models.user import User
import sys

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


def create_token(email: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {"sub": email, "exp": expire}

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return user


def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


MAX_REQUEST_SIZE = 1024 * 1024

def validate_request_size(request: Request):
    max_size = 1 * 1024 * 1024  # 1 MB
    if sys.getsizeof(request) > max_size:
        raise HTTPException(status_code=400, detail="Request payload exceeds the size limit (1MB)")
    return request