from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import auth as auth_service

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("")
def get_stats(
    db: Session = Depends(get_db),
    _=Depends(auth_service.RequirePrivilege("view:all_assets")),
):
    """
    Aggregated dashboard stats — requires view:all_assets privilege.
    Only Admins and Managers can access.
    """
    total_assets = db.query(models.Asset).count()
    total_users = db.query(models.User).count()
    assigned = (
        db.query(models.Asset)
        .filter(models.Asset.assigned_to.isnot(None))
        .count()
    )
    unassigned = total_assets - assigned

    # Count by category
    by_category: dict[str, int] = {}
    for asset in db.query(models.Asset).all():
        by_category[asset.category] = by_category.get(asset.category, 0) + 1

    # Count by status
    by_status: dict[str, int] = {}
    for asset in db.query(models.Asset).all():
        by_status[asset.status] = by_status.get(asset.status, 0) + 1

    # Assets per user (top 5)
    assets_per_user = []
    for user in db.query(models.User).all():
        count = (
            db.query(models.Asset)
            .filter(models.Asset.assigned_to == user.id)
            .count()
        )
        if count > 0:
            assets_per_user.append({"user": user.name, "count": count})
    assets_per_user.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_assets": total_assets,
        "total_users": total_users,
        "assigned_assets": assigned,
        "unassigned_assets": unassigned,
        "by_category": by_category,
        "by_status": by_status,
        "assets_per_user": assets_per_user[:5],
    }
