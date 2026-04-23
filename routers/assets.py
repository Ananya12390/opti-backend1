from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import auth as auth_service

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=list[schemas.AssetOut])
def list_assets(
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    """
    Admins/Managers see ALL assets.
    Employees see only assets assigned to them.
    """
    if auth_service.user_has_privilege(current_user, "view:all_assets"):
        return db.query(models.Asset).all()
    return (
        db.query(models.Asset)
        .filter(models.Asset.assigned_to == current_user.id)
        .all()
    )


@router.get("/{asset_id}", response_model=schemas.AssetOut)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    # Employees can only view their own assets
    if (
        not auth_service.user_has_privilege(current_user, "view:all_assets")
        and asset.assigned_to != current_user.id
    ):
        raise HTTPException(403, "Access denied — not your asset")
    return asset


@router.post("", response_model=schemas.AssetOut, status_code=201)
def create_asset(
    payload: schemas.AssetCreate,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("manage:inventory")),
):
    """Create an asset — requires manage:inventory privilege."""
    asset = models.Asset(**payload.dict())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.put("/{asset_id}", response_model=schemas.AssetOut)
def update_asset(
    asset_id: int,
    payload: schemas.AssetUpdate,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("manage:inventory")),
):
    """Update an asset — requires manage:inventory privilege."""
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(asset, k, v)
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("delete:asset")),
):
    """
    Delete an asset — requires delete:asset privilege.
    Only Admins have this privilege; Managers cannot delete.
    """
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    db.delete(asset)
    db.commit()
