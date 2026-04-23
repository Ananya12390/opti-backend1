from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import auth as auth_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("view:all_users")),
):
    """List every user — requires view:all_users privilege."""
    return db.query(models.User).all()


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("view:all_users")),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.post("", response_model=schemas.UserOut, status_code=201)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("manage:users")),
):
    """Create a new user — requires manage:users privilege."""
    return auth_service.create_user(db, payload)


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("manage:users")),
):
    """Update user details — requires manage:users privilege."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    for k, v in payload.dict(exclude_unset=True).items():
        if k == "password":
            user.hashed_password = auth_service.hash_password(v)
        else:
            setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("manage:users")),
):
    """Delete a user — requires manage:users privilege."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
