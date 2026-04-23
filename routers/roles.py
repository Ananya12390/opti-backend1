from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import auth as auth_service

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@router.get("", response_model=list[schemas.RoleOut])
def list_roles(
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("view:all_users")),
):
    """List all roles with their permission sets."""
    return db.query(models.Role).all()


@router.get("/{role_id}", response_model=schemas.RoleOut)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("view:all_users")),
):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")
    return role


@router.put("/{role_id}", response_model=schemas.RoleOut)
def update_role_permissions(
    role_id: int,
    payload: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("manage:settings")),
):
    """Update a role's permission list — requires manage:settings privilege."""
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(role, k, v)
    db.commit()
    db.refresh(role)
    return role
