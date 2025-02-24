from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.user import UserCreate, UserLogin
from utils.security import create_token, get_user_by_email
from models.user import User
from models.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Log the user input for debugging (this should be removed in production)
    print(user)

    # Check if the user with the provided email already exists in the database
    if get_user_by_email(db, user.email):
        # If the email is already registered, raise a Bad Request error (400)
        raise HTTPException(status_code=400, detail="Email already registered")

    # If the email is not registered, create a new user instance
    new_user = User(email=user.email, password=user.password)

    # Add the new user to the session and commit to save it in the database
    db.add(new_user)
    db.commit()

    # Refresh the user object to reflect the database changes
    db.refresh(new_user)

    # Create a JWT token for the new user
    token = create_token(user.email)

    # Return the token in the response
    return {"token": token}



@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Fetch the user from the database using the email provided in the login request
    db_user = get_user_by_email(email=user.email, db=db)

    # If the user is not found or the password does not match, raise an Unauthorized error (401)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # If credentials are valid, create a JWT token for the user and return it
    return {"token": create_token(user.email)}
