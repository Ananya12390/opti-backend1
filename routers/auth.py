from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import schemas
import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate with username + password, receive a JWT."""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = auth_service.create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserOut.from_orm(user),
    }


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user=Depends(auth_service.get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
