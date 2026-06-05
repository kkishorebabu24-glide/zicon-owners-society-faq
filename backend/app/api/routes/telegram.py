# Telegram webhook routes

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.db.models import TelegramGroup, Message
from app.schemas.base import (
    TelegramGroupResponse, TelegramGroupCreate, PaginatedResponse, TelegramGroupUpdate
)
from app.core.database import get_db
from app.core.dependencies import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


class TelegramGroupResponse:
    """Response schema for Telegram groups"""
    pass


class TelegramGroupCreate:
    """Create schema for Telegram groups"""
    pass


class TelegramGroupUpdate:
    """Update schema for Telegram groups"""
    pass


# ============================================================================
# TELEGRAM GROUP MANAGEMENT
# ============================================================================

@router.get("/groups", response_model=PaginatedResponse)
async def get_telegram_groups(
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all configured Telegram groups
    
    Requires: Admin role
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    query = db.query(TelegramGroup)
    
    if is_active is not None:
        query = query.filter(TelegramGroup.is_active == is_active)
    
    total = query.count()
    groups = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": groups
    }


@router.post("/groups")
async def create_telegram_group(
    group_data: dict,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Telegram group configuration
    
    Requires: Admin role
    
    Body:
        - chat_id: Telegram chat ID
        - title: Group title
        - description: Group description
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    # Check if group already exists
    existing = db.query(TelegramGroup).filter(
        TelegramGroup.chat_id == group_data.get("chat_id")
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram group already configured"
        )
    
    group = TelegramGroup(
        chat_id=group_data.get("chat_id"),
        title=group_data.get("title"),
        description=group_data.get("description"),
        is_active=True,
        is_monitored=True
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    logger.info(f"Telegram group created: {group.chat_id} ({group.title})")
    
    return {
        "id": group.id,
        "chat_id": group.chat_id,
        "title": group.title,
        "message": "Telegram group configured successfully"
    }


@router.get("/groups/{group_id}")
async def get_telegram_group(
    group_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific Telegram group details"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram group not found"
        )
    
    return {
        "id": group.id,
        "chat_id": group.chat_id,
        "title": group.title,
        "description": group.description,
        "is_active": group.is_active,
        "is_monitored": group.is_monitored,
        "member_count": group.member_count,
        "message_count": group.message_count,
        "created_at": group.created_at
    }


@router.put("/groups/{group_id}")
async def update_telegram_group(
    group_id: int,
    update_data: dict,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update Telegram group configuration"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram group not found"
        )
    
    # Update fields
    if "is_active" in update_data:
        group.is_active = update_data["is_active"]
    if "is_monitored" in update_data:
        group.is_monitored = update_data["is_monitored"]
    if "title" in update_data:
        group.title = update_data["title"]
    if "description" in update_data:
        group.description = update_data["description"]
    
    db.commit()
    db.refresh(group)
    
    logger.info(f"Telegram group updated: {group.chat_id}")
    
    return {
        "id": group.id,
        "message": "Telegram group updated successfully"
    }


@router.delete("/groups/{group_id}")
async def delete_telegram_group(
    group_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete Telegram group configuration"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram group not found"
        )
    
    db.delete(group)
    db.commit()
    
    logger.info(f"Telegram group deleted: {group.chat_id}")
    
    return {"message": "Telegram group deleted successfully"}


# ============================================================================
# TELEGRAM WEBHOOK
# ============================================================================

@router.post("/webhook")
async def telegram_webhook(payload: dict, db: Session = Depends(get_db)):
    """
    Receive Telegram updates from bot
    
    This endpoint is called by Telegram servers when new messages arrive.
    Configuration: Set webhook in Telegram Bot API with this URL.
    """
    try:
        # Extract message data from Telegram payload
        message = payload.get("message")
        if not message:
            return {"ok": True}
        
        chat_id = str(message.get("chat", {}).get("id"))
        message_id = message.get("message_id")
        text = message.get("text", "")
        from_user = message.get("from", {})
        
        # Find the telegram group
        group = db.query(TelegramGroup).filter(
            TelegramGroup.chat_id == chat_id
        ).first()
        
        if not group or not group.is_monitored:
            logger.info(f"Ignoring message from unmonitored group: {chat_id}")
            return {"ok": True}
        
        # Store message
        msg_obj = Message(
            telegram_group_id=group.id,
            telegram_message_id=message_id,
            sender_name=from_user.get("first_name", "Unknown"),
            sender_id=str(from_user.get("id")),
            text=text,
            message_type="text"
        )
        
        db.add(msg_obj)
        group.message_count += 1
        db.commit()
        
        logger.info(f"Message stored from {from_user.get('first_name')}: {chat_id}")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Telegram webhook error: {str(e)}")
        return {"ok": False, "error": str(e)}


# ============================================================================
# TELEGRAM MESSAGES
# ============================================================================

@router.get("/groups/{group_id}/messages")
async def get_group_messages(
    group_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages from a specific Telegram group"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or moderator role required"
        )
    
    # Verify group exists
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram group not found"
        )
    
    messages = db.query(Message).filter(
        Message.telegram_group_id == group_id
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": db.query(Message).filter(
            Message.telegram_group_id == group_id
        ).count(),
        "skip": skip,
        "limit": limit,
        "items": messages
    }
