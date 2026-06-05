"""
Demand-Supply (Marketplace) Routes

Endpoints for creating, reading, updating offers and requests.
All state changes broadcast real-time updates via WebSocket.
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.models import (
    Listing, User, Match, ListingStatus, OfferRequestType, Review
)
from app.schemas.base import (
    ListingResponse, ListingDetailResponse, ListingCreate, ListingUpdate,
    MatchResponse, MatchCreate, MatchUpdate, ReviewResponse, ReviewCreate,
    UserResponse, PaginatedResponse
)
from app.core.websocket_manager import get_connection_manager
from app.core.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


# ============================================================================
# LISTING ENDPOINTS
# ============================================================================

@router.get("/listings", response_model=PaginatedResponse)
async def get_listings(
    type: Optional[str] = Query(None, description="Filter by type: offer or request"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get all listings with optional filtering.
    
    Real-time updates: Subscribe to 'listing_updates' channel for changes.
    """
    query = db.query(Listing)
    
    # Apply filters
    if type:
        query = query.filter(Listing.type == type)
    if status:
        query = query.filter(Listing.status == status)
    if category:
        query = query.filter(Listing.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%")
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    listings = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [ListingResponse.model_validate(l) for l in listings]
    }


@router.get("/offers", response_model=PaginatedResponse)
async def get_offers(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """Get all offers (simplified endpoint)"""
    return await get_listings(
        type="offer", category=category, search=search,
        skip=skip, limit=limit, db=db
    )


@router.get("/requests", response_model=PaginatedResponse)
async def get_requests(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """Get all requests (simplified endpoint)"""
    return await get_listings(
        type="request", category=category, search=search,
        skip=skip, limit=limit, db=db
    )


@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: ListingCreate,
    creator_id: int = Query(..., description="Current user ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db),
) -> ListingResponse:
    """
    Create a new offer or request.
    
    **Real-time:** Broadcasts `listing_created` event to all clients.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Create listing
    listing = Listing(
        creator_id=creator_id,
        type=listing_data.type,
        title=listing_data.title,
        description=listing_data.description,
        category=listing_data.category,
        price=listing_data.price,
        currency=listing_data.currency,
        price_negotiable=listing_data.price_negotiable,
        tags=listing_data.tags,
        images=listing_data.images,
        location=listing_data.location,
    )
    
    db.add(listing)
    db.commit()
    db.refresh(listing)
    
    # Broadcast real-time update
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="listing_created",
        data={
            "listing_id": listing.id,
            "type": listing.type.value,
            "title": listing.title,
            "category": listing.category,
            "price": listing.price,
            "creator_id": creator_id,
            "created_at": listing.created_at.isoformat(),
        }
    )
    logger.info(f"Listing {listing.id} created by user {creator_id}")
    
    return ListingResponse.model_validate(listing)


@router.get("/listings/{listing_id}", response_model=ListingDetailResponse)
async def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
) -> ListingDetailResponse:
    """Get listing details including matches and reviews"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Increment view count
    listing.view_count += 1
    db.commit()
    
    return ListingDetailResponse.model_validate(listing)


@router.put("/listings/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    user_id: int = Query(..., description="Current user ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db),
) -> ListingResponse:
    """
    Update a listing.
    
    **Real-time:** Broadcasts `listing_updated` event to all clients.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Check authorization
    if listing.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
    
    # Update fields
    update_data = listing_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    
    # Broadcast real-time update
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="listing_updated",
        data={
            "listing_id": listing.id,
            "updated_fields": update_data,
            "updated_at": listing.updated_at.isoformat(),
        }
    )
    logger.info(f"Listing {listing_id} updated by user {user_id}")
    
    return ListingResponse.model_validate(listing)


@router.delete("/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: int,
    user_id: int = Query(..., description="Current user ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db),
):
    """
    Delete a listing.
    
    **Real-time:** Broadcasts `listing_closed` event to all clients.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Check authorization
    if listing.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    
    # Soft delete by marking as cancelled
    listing.status = ListingStatus.CANCELLED
    listing.updated_at = datetime.utcnow()
    db.commit()
    
    # Broadcast real-time update
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="listing_closed",
        data={
            "listing_id": listing_id,
            "status": "cancelled",
            "closed_at": datetime.utcnow().isoformat(),
        }
    )
    logger.info(f"Listing {listing_id} deleted by user {user_id}")


# ============================================================================
# MATCH ENDPOINTS
# ============================================================================

@router.get("/listings/{listing_id}/matches", response_model=List[MatchResponse])
async def get_listing_matches(
    listing_id: int,
    db: Session = Depends(get_db),
) -> List[MatchResponse]:
    """Get all matches for a listing"""
    if db is None:
        return []
    
    matches = db.query(Match).filter(Match.listing_id == listing_id).all()
    return [MatchResponse.model_validate(m) for m in matches]


@router.post("/listings/{listing_id}/matches", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    listing_id: int,
    match_data: MatchCreate,
    db: Session = Depends(get_db),
) -> MatchResponse:
    """
    Create a new match for a listing.
    
    **Real-time:** Broadcasts `match_found` event to relevant users.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Verify listing exists
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    match = Match(
        listing_id=listing_id,
        user_id=match_data.user_id,
        match_score=match_data.match_score,
        match_reason=match_data.match_reason,
        notes=match_data.notes,
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    # Broadcast to listing creator and matched user
    manager = get_connection_manager()
    await manager.publish_event(
        event_type="match_found",
        data={
            "match_id": match.id,
            "listing_id": listing_id,
            "user_id": match_data.user_id,
            "match_score": match_data.match_score,
            "created_at": match.created_at.isoformat(),
        },
        target_users=[listing.creator_id, match_data.user_id]
    )
    logger.info(f"Match {match.id} created for listing {listing_id}")
    
    return MatchResponse.model_validate(match)


@router.put("/matches/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    user_id: int = Query(..., description="Current user ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db),
) -> MatchResponse:
    """Update a match status"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    update_data = match_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(match, field, value)
    
    match.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(match)
    
    return MatchResponse.model_validate(match)


# ============================================================================
# REVIEW ENDPOINTS
# ============================================================================

@router.post("/listings/{listing_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    listing_id: int,
    review_data: ReviewCreate,
    reviewer_id: int = Query(..., description="Current user ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Create a review for a listing"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Verify listing exists
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    review = Review(
        listing_id=listing_id,
        reviewer_id=reviewer_id,
        reviewee_id=review_data.reviewee_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return ReviewResponse.model_validate(review)


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws/listings")
async def websocket_listings(
    websocket: WebSocket,
    user_id: Optional[int] = None,
    channels: Optional[str] = None,
):
    """
    WebSocket endpoint for real-time listing updates.
    
    Query parameters:
    - user_id: Current user ID (optional, for user-specific updates)
    - channels: Comma-separated list of channels to subscribe to
               (listing_updates, digest_delivery, marketplace)
    
    Example: ws://localhost:8000/api/v1/marketplace/ws/listings?user_id=123&channels=listing_updates,marketplace
    """
    manager = get_connection_manager()
    
    # Parse channels
    channel_list = ["marketplace"]  # Default
    if channels:
        channel_list = [c.strip() for c in channels.split(",")]
    
    try:
        await manager.connect(websocket, user_id=user_id, channels=channel_list)
        logger.info(f"WebSocket connected: user_id={user_id}, channels={channel_list}")
        
        # Keep connection alive
        while True:
            # Receive any incoming messages (for future interactive features)
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message from user {user_id}: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=user_id, channels=channel_list)
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        try:
            manager.disconnect(websocket, user_id=user_id, channels=channel_list)
        except:
            pass


# ============================================================================
# STATS & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/stats")
async def get_marketplace_stats(db: Session = Depends(get_db)) -> dict:
    """Get marketplace statistics"""
    if db is None:
        return {
            "total_listings": 0,
            "total_offers": 0,
            "total_requests": 0,
            "total_matches": 0,
            "active_listings": 0,
        }
    
    total = db.query(Listing).count()
    offers = db.query(Listing).filter(Listing.type == OfferRequestType.OFFER).count()
    requests_count = db.query(Listing).filter(Listing.type == OfferRequestType.REQUEST).count()
    matches = db.query(Match).count()
    active = db.query(Listing).filter(Listing.status == ListingStatus.ACTIVE).count()
    
    return {
        "total_listings": total,
        "total_offers": offers,
        "total_requests": requests_count,
        "total_matches": matches,
        "active_listings": active,
    }

# - PUT /offers/{id}
# - DELETE /offers/{id}
# - GET /requests
# - POST /requests
# - GET /requests/{id}
# - GET /matches
