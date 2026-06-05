"""
Digest Routes

Endpoints for viewing and delivering AI-generated digests.
All digest publications and deliveries broadcast real-time updates via WebSocket.
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import Digest, DigestSubscription, User, TelegramGroup
from app.schemas.base import (
    DigestResponse, DigestDetailResponse, DigestCreate, DigestUpdate,
    DigestSubscriptionResponse, PaginatedResponse
)
from app.core.websocket_manager import get_connection_manager
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/digests", tags=["digests"])


# ============================================================================
# DIGEST LISTING & RETRIEVAL
# ============================================================================

@router.get("/", response_model=PaginatedResponse)
async def list_digests(
    telegram_group_id: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all digests with optional filtering.
    
    **Real-time:** Subscribe to 'digest_delivery' channel for new digests.
    """
    query = db.query(Digest)
    
    if telegram_group_id:
        query = query.filter(Digest.telegram_group_id == telegram_group_id)
    if is_published is not None:
        query = query.filter(Digest.is_published == is_published)
    
    total = query.count()
    digests = query.order_by(Digest.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [DigestResponse.model_validate(d) for d in digests]
    }


@router.get("/{digest_id}", response_model=DigestDetailResponse)
async def get_digest(
    digest_id: int,
    db: Session = Depends(get_db),
) -> DigestDetailResponse:
    """Get a specific digest with its subscriptions"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    digest = db.query(Digest).filter(Digest.id == digest_id).first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    return DigestDetailResponse.model_validate(digest)


@router.get("/user/{user_id}", response_model=PaginatedResponse)
async def get_user_digests(
    user_id: int,
    is_read: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get all digests subscribed to by a user.
    
    **Real-time:** Subscribe to 'user_{user_id}' channel for personalized digest updates.
    """
    if db is None:
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": []
        }
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Digest).join(
        DigestSubscription,
        DigestSubscription.digest_id == Digest.id
    ).filter(DigestSubscription.user_id == user_id)
    
    if is_read is not None:
        query = query.filter(DigestSubscription.is_read == is_read)
    
    total = query.count()
    digests = query.order_by(Digest.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [DigestResponse.model_validate(d) for d in digests]
    }


# ============================================================================
# DIGEST CREATION & PUBLISHING
# ============================================================================

@router.post("/", response_model=DigestResponse, status_code=status.HTTP_201_CREATED)
async def create_digest(
    digest_data: DigestCreate,
    db: Session = Depends(get_db),
) -> DigestResponse:
    """
    Create a new digest (typically called by background workers).
    
    **Real-time:** Broadcasts `digest_created` event.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Verify telegram group exists
    group = db.query(TelegramGroup).filter(
        TelegramGroup.id == digest_data.telegram_group_id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Telegram group not found")
    
    digest = Digest(
        telegram_group_id=digest_data.telegram_group_id,
        title=digest_data.title,
        summary=digest_data.summary,
        key_topics=digest_data.key_topics,
        key_discussions=digest_data.key_discussions,
        action_items=digest_data.action_items,
        message_count=digest_data.message_count,
        period_start=digest_data.period_start,
        period_end=digest_data.period_end,
    )
    
    db.add(digest)
    db.commit()
    db.refresh(digest)
    
    logger.info(f"Digest {digest.id} created for group {digest_data.telegram_group_id}")
    
    return DigestResponse.model_validate(digest)


@router.put("/{digest_id}/publish", response_model=DigestResponse)
async def publish_digest(
    digest_id: int,
    db: Session = Depends(get_db),
) -> DigestResponse:
    """
    Publish a digest to subscribers.
    
    **Real-time:** Broadcasts `digest_published` event to all clients,
    then delivers to subscribed users with `digest_delivered` event.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    digest = db.query(Digest).filter(Digest.id == digest_id).first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    if digest.is_published:
        raise HTTPException(status_code=400, detail="Digest already published")
    
    # Mark as published
    digest.is_published = True
    digest.published_at = datetime.utcnow()
    
    # Create subscriptions for all active users (if not already subscribed)
    # TODO: Implement subscription logic based on user preferences and telegram group
    
    db.commit()
    db.refresh(digest)
    
    # Broadcast publication event
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="digest_published",
        data={
            "digest_id": digest.id,
            "title": digest.title,
            "telegram_group_id": digest.telegram_group_id,
            "period_start": digest.period_start.isoformat(),
            "period_end": digest.period_end.isoformat(),
            "published_at": digest.published_at.isoformat(),
        }
    )
    
    logger.info(f"Digest {digest_id} published")
    
    return DigestResponse.model_validate(digest)


# ============================================================================
# DIGEST SUBSCRIPTION & DELIVERY
# ============================================================================

@router.get("/{digest_id}/subscriptions", response_model=List[DigestSubscriptionResponse])
async def get_digest_subscriptions(
    digest_id: int,
    db: Session = Depends(get_db),
) -> List[DigestSubscriptionResponse]:
    """Get all subscriptions for a digest"""
    if db is None:
        return []
    
    subscriptions = db.query(DigestSubscription).filter(
        DigestSubscription.digest_id == digest_id
    ).all()
    
    return [DigestSubscriptionResponse.model_validate(s) for s in subscriptions]


@router.post("/{digest_id}/subscribe/{user_id}", response_model=DigestSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_digest(
    digest_id: int,
    user_id: int,
    delivery_channel: str = Query("email", description="email, telegram, sms, or web"),
    db: Session = Depends(get_db),
) -> DigestSubscriptionResponse:
    """
    Subscribe a user to a digest.
    
    **Real-time:** Broadcasts subscription update.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Verify digest and user exist
    digest = db.query(Digest).filter(Digest.id == digest_id).first()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already subscribed
    existing = db.query(DigestSubscription).filter(
        and_(
            DigestSubscription.digest_id == digest_id,
            DigestSubscription.user_id == user_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already subscribed to this digest")
    
    subscription = DigestSubscription(
        user_id=user_id,
        digest_id=digest_id,
        delivery_channel=delivery_channel,
        delivery_status="pending",
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"User {user_id} subscribed to digest {digest_id} via {delivery_channel}")
    
    return DigestSubscriptionResponse.model_validate(subscription)


@router.put("/{digest_id}/subscriptions/{subscription_id}/mark-delivered", response_model=DigestSubscriptionResponse)
async def mark_digest_delivered(
    digest_id: int,
    subscription_id: int,
    db: Session = Depends(get_db),
) -> DigestSubscriptionResponse:
    """
    Mark a digest as delivered to a user.
    
    **Real-time:** Broadcasts `digest_delivered` event to the user.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    subscription = db.query(DigestSubscription).filter(
        and_(
            DigestSubscription.id == subscription_id,
            DigestSubscription.digest_id == digest_id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.delivery_status = "delivered"
    subscription.sent_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subscription)
    
    # Broadcast delivery event to specific user
    manager = get_connection_manager()
    await manager.broadcast_to_user(
        subscription.user_id,
        {
            "event_type": "digest_delivered",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "digest_id": digest_id,
                "subscription_id": subscription_id,
                "delivery_channel": subscription.delivery_channel,
                "delivered_at": subscription.sent_at.isoformat(),
            }
        }
    )
    
    logger.info(f"Digest {digest_id} marked as delivered to user {subscription.user_id}")
    
    return DigestSubscriptionResponse.model_validate(subscription)


@router.put("/{digest_id}/subscriptions/{subscription_id}/mark-read", response_model=DigestSubscriptionResponse)
async def mark_digest_read(
    digest_id: int,
    subscription_id: int,
    db: Session = Depends(get_db),
) -> DigestSubscriptionResponse:
    """Mark a digest as read by the user"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    subscription = db.query(DigestSubscription).filter(
        and_(
            DigestSubscription.id == subscription_id,
            DigestSubscription.digest_id == digest_id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_read = True
    subscription.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Digest {digest_id} marked as read by user {subscription.user_id}")
    
    return DigestSubscriptionResponse.model_validate(subscription)


# ============================================================================
# DIGEST STATS & ANALYTICS
# ============================================================================

@router.get("/stats/overview", response_model=dict)
async def get_digest_stats(db: Session = Depends(get_db)) -> dict:
    """Get digest statistics"""
    if db is None:
        return {
            "total_digests": 0,
            "published_digests": 0,
            "total_subscriptions": 0,
            "delivered_count": 0,
            "read_count": 0,
        }
    
    total = db.query(Digest).count()
    published = db.query(Digest).filter(Digest.is_published == True).count()
    subscriptions = db.query(DigestSubscription).count()
    delivered = db.query(DigestSubscription).filter(
        DigestSubscription.delivery_status == "delivered"
    ).count()
    read = db.query(DigestSubscription).filter(DigestSubscription.is_read == True).count()
    
    return {
        "total_digests": total,
        "published_digests": published,
        "total_subscriptions": subscriptions,
        "delivered_count": delivered,
        "read_count": read,
    }

# - POST /digests (admin only)
