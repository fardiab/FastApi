from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from schemas.user import UserCreate
from schemas.post import PostCreate, PostOut
from models.user import User
from models.post import Post
from utils.security import create_token, get_user_by_email, validate_request_size
from fastapi_cache.decorator import cache
from models.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from utils.security import get_user_by_email, get_user_from_token
from fastapi import Request


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/add-post")
async def add_post(
    post: PostCreate,  # Pydantic model for validating the input data
    db: Session = Depends(get_db),  # Dependency injection to get the database session
    token: str = Depends(oauth2_scheme),  # Dependency injection to get the token from the OAuth2 scheme
    request: Request = None,  # Optional dependency for the incoming HTTP request
):
    # Call the validate_request_size function to ensure the size of the request is acceptable
    validate_request_size(request)

    # Get the email from the token
    email = get_user_from_token(token)

    # Query the database to get the user by email
    user = get_user_by_email(db=db, email=email)

    # If the user is not found, raise an HTTPException with a 401 Unauthorized status
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Create a new Post object and associate it with the user
    new_post = Post(user_id=user.id, text=post.text)

    # Add the new post to the session and commit it to the database
    db.add(new_post)
    db.commit()

    # Refresh the instance to get the updated data (including auto-generated fields like id)
    db.refresh(new_post)

    # Return the newly created post
    return new_post



@router.get("/get-posts")
def get_posts(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decode the token to get the user's email
    email = get_user_from_token(token)

    # Fetch the user from the database using the email extracted from the token
    user = get_user_by_email(db, email=email)

    # If no user is found, raise a 401 Unauthorized exception
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Query the database for posts that belong to the authenticated user
    posts = db.query(Post).filter(Post.user_id == user.id).all()

    # Return the list of posts associated with the user
    return posts



@router.delete("/post-delete/{post_id}")
def delete_post(
    post_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # Decode the token to get the user's email
    email = get_user_from_token(token)

    # Fetch the user from the database using the email extracted from the token
    user = get_user_by_email(db, email=email)

    # If no user is found, raise a 401 Unauthorized exception
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch the post to be deleted by its ID, ensuring it belongs to the authenticated user
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()

    # If no post is found, raise a 404 Not Found exception
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Delete the post from the database
    db.delete(post)

    # Commit the transaction to apply the changes
    db.commit()

    # Return a success message indicating the post has been deleted
    return {"message": "Post deleted successfully"}
