"""
Society notifications routes
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import SocietyNotification, User
from app.schemas.base import SocietyNotificationResponse, SocietyNotificationUpdate, SocietyNotificationCreate, PaginatedNotifications
from app.core.dependencies import get_current_active_user
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=PaginatedNotifications)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated notifications for current user
    
    Query Parameters:
        - skip: Number of items to skip (default 0)
        - limit: Number of items to return (default 20, max 100)
        - unread_only: Return only unread notifications (default false)
    """
    query = db.query(SocietyNotification).filter(
        SocietyNotification.user_id == current_user.user_id,
        SocietyNotification.is_archived == False
    )
    
    if unread_only:
        query = query.filter(SocietyNotification.is_read == False)
    
    # Get total count
    total = query.count()
    
    # Get unread count
    unread_count = db.query(SocietyNotification).filter(
        SocietyNotification.user_id == current_user.user_id,
        SocietyNotification.is_read == False,
        SocietyNotification.is_archived == False
    ).count()
    
    # Get paginated results (newest first)
    items = query.order_by(SocietyNotification.created_at.desc()).offset(skip).limit(limit).all()
    
    return PaginatedNotifications(
        items=[SocietyNotificationResponse.model_validate(item) for item in items],
        total=total,
        unread_count=unread_count,
        skip=skip,
        limit=limit
    )


@router.get("/{notification_id}", response_model=SocietyNotificationResponse)
async def get_notification(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification"""
    notification = db.query(SocietyNotification).filter(
        SocietyNotification.id == notification_id,
        SocietyNotification.user_id == current_user.user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return SocietyNotificationResponse.model_validate(notification)


@router.put("/{notification_id}", response_model=SocietyNotificationResponse)
async def update_notification(
    notification_id: int,
    update_data: SocietyNotificationUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update notification (mark as read/archived)"""
    notification = db.query(SocietyNotification).filter(
        SocietyNotification.id == notification_id,
        SocietyNotification.user_id == current_user.user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Update fields
    if update_data.is_read is not None:
        notification.is_read = update_data.is_read
        if update_data.is_read and notification.read_at is None:
            notification.read_at = datetime.utcnow()
    
    if update_data.is_archived is not None:
        notification.is_archived = update_data.is_archived
    
    db.commit()
    db.refresh(notification)
    
    logger.info(f"Notification {notification_id} updated by user {current_user.user_id}")
    
    return SocietyNotificationResponse.model_validate(notification)


@router.put("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(SocietyNotification).filter(
        SocietyNotification.id == notification_id,
        SocietyNotification.user_id == current_user.user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.put("/mark-all-read")
async def mark_all_read(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications as read"""
    db.query(SocietyNotification).filter(
        SocietyNotification.user_id == current_user.user_id,
        SocietyNotification.is_read == False
    ).update({
        SocietyNotification.is_read: True,
        SocietyNotification.read_at: datetime.utcnow()
    })
    db.commit()
    
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete/archive a notification"""
    notification = db.query(SocietyNotification).filter(
        SocietyNotification.id == notification_id,
        SocietyNotification.user_id == current_user.user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_archived = True
    db.commit()
    
    logger.info(f"Notification {notification_id} deleted by user {current_user.user_id}")
    
    return {"message": "Notification deleted"}


@router.get("/stats/unread-count")
async def get_unread_count(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    unread_count = db.query(SocietyNotification).filter(
        SocietyNotification.user_id == current_user.user_id,
        SocietyNotification.is_read == False,
        SocietyNotification.is_archived == False
    ).count()
    
    return {"unread_count": unread_count}
