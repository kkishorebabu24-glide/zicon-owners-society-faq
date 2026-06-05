"""
Pydantic schemas for API request/response validation
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# ENUMS
# ============================================================================

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    RESIDENT = "resident"


class OfferRequestTypeEnum(str, Enum):
    OFFER = "offer"
    REQUEST = "request"


class ListingStatusEnum(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class DigestFrequencyEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    IMMEDIATE = "immediate"


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    bio: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    digest_frequency: Optional[DigestFrequencyEnum] = None
    receive_notifications: Optional[bool] = None
    notification_channels: Optional[Dict[str, bool]] = None


class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    is_active: bool
    email_verified: bool
    phone_verified: bool
    avatar_url: Optional[str]
    digest_frequency: DigestFrequencyEnum
    receive_notifications: bool
    notification_channels: Dict[str, bool]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================================
# LISTING / OFFER / REQUEST SCHEMAS
# ============================================================================

class ListingBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    price_negotiable: bool = False
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    location: Optional[str] = None


class ListingCreate(ListingBase):
    type: OfferRequestTypeEnum


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    price_negotiable: Optional[bool] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    location: Optional[str] = None
    status: Optional[ListingStatusEnum] = None


class ListingResponse(ListingBase):
    id: int
    type: OfferRequestTypeEnum
    status: ListingStatusEnum
    creator_id: int
    creator: Optional[UserResponse] = None
    view_count: int
    interest_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ListingDetailResponse(ListingResponse):
    matches: List["MatchResponse"] = []
    reviews: List["ReviewResponse"] = []


# ============================================================================
# MATCH SCHEMAS
# ============================================================================

class MatchBase(BaseModel):
    match_score: float = Field(default=0.0, ge=0.0, le=1.0)
    match_reason: Optional[str] = None
    notes: Optional[str] = None


class MatchCreate(MatchBase):
    listing_id: int
    user_id: int


class MatchUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|accepted|rejected|completed)$")
    notes: Optional[str] = None


class MatchResponse(MatchBase):
    id: int
    listing_id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# REVIEW SCHEMAS
# ============================================================================

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    listing_id: int
    reviewee_id: int


class ReviewResponse(ReviewBase):
    id: int
    listing_id: int
    reviewer_id: int
    reviewee_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DIGEST SCHEMAS
# ============================================================================

class DigestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    summary: str
    key_topics: List[str] = Field(default_factory=list)
    key_discussions: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)


class DigestCreate(DigestBase):
    telegram_group_id: int
    message_count: int = 0
    period_start: datetime
    period_end: datetime


class DigestUpdate(BaseModel):
    is_published: Optional[bool] = None
    is_delivered: Optional[bool] = None
    published_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class DigestResponse(DigestBase):
    id: int
    telegram_group_id: int
    message_count: int
    period_start: datetime
    period_end: datetime
    is_published: bool
    is_delivered: bool
    created_at: datetime
    published_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True


class DigestDetailResponse(DigestResponse):
    subscriptions: List["DigestSubscriptionResponse"] = []


class DigestSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    digest_id: int
    delivery_status: str
    delivery_channel: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class SocietyNotificationBase(BaseModel):
    type: str
    title: str
    message: str
    icon: Optional[str] = None
    color: str = "primary"


class SocietyNotificationCreate(SocietyNotificationBase):
    user_id: int
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SocietyNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None


class SocietyNotificationResponse(SocietyNotificationBase):
    id: int
    user_id: int
    related_type: Optional[str]
    related_id: Optional[int]
    action_url: Optional[str]
    metadata: Optional[Dict[str, Any]]
    is_read: bool
    is_archived: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedNotifications(BaseModel):
    items: List[SocietyNotificationResponse]
    total: int
    unread_count: int
    skip: int
    limit: int


# ============================================================================
# TELEGRAM GROUP SCHEMAS
# ============================================================================

class TelegramGroupBase(BaseModel):
    chat_id: str
    title: str
    description: Optional[str] = None


class TelegramGroupCreate(TelegramGroupBase):
    pass


class TelegramGroupResponse(TelegramGroupBase):
    id: int
    is_active: bool
    is_monitored: bool
    member_count: int
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# WEBSOCKET EVENT SCHEMAS
# ============================================================================

class WebSocketEventBase(BaseModel):
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]


class ListingCreatedEvent(WebSocketEventBase):
    """Event sent when a new listing is created"""
    event_type: str = "listing_created"
    data: Dict[str, Any]  # Contains listing info


class ListingUpdatedEvent(WebSocketEventBase):
    """Event sent when a listing is updated"""
    event_type: str = "listing_updated"
    data: Dict[str, Any]  # Contains listing_id and updated fields


class MatchFoundEvent(WebSocketEventBase):
    """Event sent when a match is found"""
    event_type: str = "match_found"
    data: Dict[str, Any]  # Contains match info


class DigestPublishedEvent(WebSocketEventBase):
    """Event sent when a digest is published"""
    event_type: str = "digest_published"
    data: Dict[str, Any]  # Contains digest info


class DigestDeliveredEvent(WebSocketEventBase):
    """Event sent when a digest is delivered to a user"""
    event_type: str = "digest_delivered"
    data: Dict[str, Any]  # Contains digest_id, user_id


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[Any]


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    redis_connected: bool = False
    database_connected: bool = False
