"""
Database Models for Society App

Defines SQLAlchemy ORM models for:
- User & Authentication
- Offers & Requests (Demand-Supply Marketplace)
- Digests & Messages
- Telegram Integration
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, 
    Enum as SQLEnum, JSON, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    RESIDENT = "resident"


class OfferRequestType(str, Enum):
    """Type of marketplace listing"""
    OFFER = "offer"
    REQUEST = "request"


class ListingStatus(str, Enum):
    """Status of an offer or request"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class DigestFrequency(str, Enum):
    """Frequency of digest delivery"""
    DAILY = "daily"
    WEEKLY = "weekly"
    IMMEDIATE = "immediate"


# ============================================================================
# USER & AUTHENTICATION MODELS
# ============================================================================

class User(Base):
    """User account model"""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_phone', 'phone'),
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('phone', name='uq_user_phone'),
        CheckConstraint('email != \'\'', name='chk_email_not_empty'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    
    # Password (hashed)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    
    # Role & Status
    role = Column(SQLEnum(UserRole), default=UserRole.RESIDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Preferences
    digest_frequency = Column(SQLEnum(DigestFrequency), default=DigestFrequency.DAILY)
    receive_notifications = Column(Boolean, default=True)
    notification_channels = Column(JSON, default={"email": True, "telegram": False, "sms": False})
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    listings = relationship("Listing", back_populates="creator", cascade="all, delete-orphan")
    reviews_given = relationship(
        "Review", foreign_keys="Review.reviewer_id", 
        back_populates="reviewer", cascade="all, delete-orphan"
    )
    reviews_received = relationship(
        "Review", foreign_keys="Review.reviewee_id",
        back_populates="reviewee", cascade="all, delete-orphan"
    )
    matches = relationship("Match", back_populates="user", cascade="all, delete-orphan")
    digest_subscriptions = relationship("DigestSubscription", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"


# ============================================================================
# TELEGRAM INTEGRATION MODELS
# ============================================================================

class TelegramGroup(Base):
    """Telegram group monitored by the application"""
    __tablename__ = "telegram_groups"
    __table_args__ = (
        Index('idx_chat_id', 'chat_id'),
        UniqueConstraint('chat_id', name='uq_telegram_chat_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_monitored = Column(Boolean, default=True)
    
    # Stats
    member_count = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="telegram_group", cascade="all, delete-orphan")
    digests = relationship("Digest", back_populates="telegram_group")

    def __repr__(self):
        return f"<TelegramGroup {self.chat_id}: {self.title}>"


class Message(Base):
    """Message from Telegram group"""
    __tablename__ = "messages"
    __table_args__ = (
        Index('idx_telegram_group_id', 'telegram_group_id'),
        Index('idx_message_id', 'telegram_message_id'),
        Index('idx_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    telegram_group_id = Column(Integer, ForeignKey("telegram_groups.id"), nullable=False)
    
    # Telegram Data
    telegram_message_id = Column(Integer, nullable=False)
    sender_name = Column(String(255), nullable=False)
    sender_id = Column(String(50), nullable=True)
    
    # Content
    text = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, photo, document, etc.
    
    # Processing
    is_processed = Column(Boolean, default=False)
    processing_errors = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    telegram_group = relationship("TelegramGroup", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_name}>"


# ============================================================================
# MARKETPLACE MODELS (Offers & Requests)
# ============================================================================

class Listing(Base):
    """Base model for Offers and Requests"""
    __tablename__ = "listings"
    __table_args__ = (
        Index('idx_creator_id', 'creator_id'),
        Index('idx_type', 'type'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
        CheckConstraint('price >= 0', name='chk_price_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Creator
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Core Data
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    
    # Type & Status
    type = Column(SQLEnum(OfferRequestType), nullable=False)  # OFFER or REQUEST
    status = Column(SQLEnum(ListingStatus), default=ListingStatus.ACTIVE)
    
    # Pricing
    price = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    price_negotiable = Column(Boolean, default=False)
    
    # Details
    tags = Column(JSON, default=[])
    images = Column(JSON, default=[])  # List of image URLs
    location = Column(String(255), nullable=True)
    
    # Engagement
    view_count = Column(Integer, default=0)
    interest_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="listings")
    matches = relationship("Match", back_populates="listing", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="listing", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<{self.type.value.title()} {self.id}: {self.title}>"


class Match(Base):
    """Match between offer and request (or two users)"""
    __tablename__ = "matches"
    __table_args__ = (
        Index('idx_listing_id', 'listing_id'),
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Core Match Info
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Interested user
    
    # Match Details
    match_score = Column(Float, default=0.0)  # 0.0 - 1.0 confidence score
    match_reason = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, accepted, rejected, completed
    
    # Communication
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    listing = relationship("Listing", back_populates="matches")
    user = relationship("User", back_populates="matches")

    def __repr__(self):
        return f"<Match {self.id}: User {self.user_id} + Listing {self.listing_id}>"


class Review(Base):
    """Review/Rating for users after transaction"""
    __tablename__ = "reviews"
    __table_args__ = (
        Index('idx_listing_id', 'listing_id'),
        Index('idx_reviewer_id', 'reviewer_id'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='chk_rating_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Listing & Users
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    listing = relationship("Listing", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")

    def __repr__(self):
        return f"<Review {self.id}: {self.rating}★ by User {self.reviewer_id}>"


# ============================================================================
# DIGEST MODELS
# ============================================================================

class Digest(Base):
    """AI-generated daily/weekly digest from Telegram messages"""
    __tablename__ = "digests"
    __table_args__ = (
        Index('idx_telegram_group_id', 'telegram_group_id'),
        Index('idx_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    telegram_group_id = Column(Integer, ForeignKey("telegram_groups.id"), nullable=False)
    
    # Content
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    key_topics = Column(JSON, default=[])  # List of topics
    key_discussions = Column(JSON, default=[])  # List of important discussions
    action_items = Column(JSON, default=[])  # List of action items
    
    # Metadata
    message_count = Column(Integer, default=0)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Relationships
    telegram_group = relationship("TelegramGroup", back_populates="digests")
    subscriptions = relationship("DigestSubscription", back_populates="digest", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Digest {self.id}: {self.title}>"


class DigestSubscription(Base):
    """User subscription to digest delivery"""
    __tablename__ = "digest_subscriptions"
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_digest_id', 'digest_id'),
        UniqueConstraint('user_id', 'digest_id', name='uq_user_digest'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    digest_id = Column(Integer, ForeignKey("digests.id"), nullable=False)
    
    # Delivery Status
    delivery_status = Column(String(20), default="pending")  # pending, sent, delivered, failed
    delivery_channel = Column(String(20), default="email")  # email, telegram, sms, web
    
    # Read Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="digest_subscriptions")
    digest = relationship("Digest", back_populates="subscriptions")

    def __repr__(self):
        return f"<DigestSubscription {self.id}: User {self.user_id} -> Digest {self.digest_id}>"


# ============================================================================
# NOTIFICATION & ACTIVITY MODELS
# ============================================================================

class Activity(Base):
    """Activity log for real-time updates"""
    __tablename__ = "activities"
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_related_type', 'related_type'),
        Index('idx_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Activity Type
    event_type = Column(String(50), nullable=False)  # listing_created, listing_updated, match_found, digest_published, etc.
    action = Column(String(100), nullable=False)
    
    # Related Entity
    related_type = Column(String(50), nullable=False)  # listing, digest, match, user, etc.
    related_id = Column(Integer, nullable=True)
    
    # Data
    data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Activity {self.id}: {self.event_type} on {self.related_type}>"


class SocietyNotification(Base):
    """Notifications for society members"""
    __tablename__ = "society_notifications"
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_type', 'type'),
        Index('idx_is_read', 'is_read'),
        Index('idx_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification Content
    type = Column(String(50), nullable=False)  # announcement, listing_match, digest_ready, admin_message, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    icon = Column(String(100), nullable=True)  # Material icon name
    color = Column(String(50), default="primary")  # Material-UI color
    
    # Related Entity
    related_type = Column(String(50), nullable=True)  # listing, digest, user, etc.
    related_id = Column(Integer, nullable=True)
    
    # Additional Data
    action_url = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime, nullable=True)
    
    # User Relationship
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<SocietyNotification {self.id}: {self.type} for User {self.user_id}>"
