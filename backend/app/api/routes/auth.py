# Authentication routes

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
from jose import jwt

from app.db.models import User, UserRole
from app.schemas.base import UserCreate, LoginRequest, TokenResponse, UserResponse
from app.core.jwt_handler import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.dependencies import get_current_active_user
from app.core.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=dict, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    Returns:
        - user_id: New user ID
        - message: Confirmation message
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if phone already exists
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create new user
    try:
        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password),
            bio=user_data.bio,
            address=user_data.address,
            role=UserRole.RESIDENT  # Default role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
        
        return {
            "user_id": new_user.id,
            "email": new_user.email,
            "message": "Registration successful. Please log in."
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user and return JWT tokens
    
    Returns:
        - access_token: JWT access token (valid for 15 minutes)
        - refresh_token: JWT refresh token (valid for 7 days)
        - token_type: "bearer"
        - expires_in: Access token expiration in seconds
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        logger.warning(f"Login failed: User not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Login failed: Invalid password - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: User inactive - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login time
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    # Create tokens
    access_token = create_access_token(user.id, user.email, user.role.value)
    refresh_token = create_refresh_token(user.id, user.email)
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60  # 15 minutes in seconds
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    
    Returns:
        - access_token: New JWT access token
        - refresh_token: Same refresh token
        - token_type: "bearer"
        - expires_in: Access token expiration in seconds
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("user_id")
        email = payload.get("email")
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or not found"
            )

        access_token = create_access_token(user.id, user.email, user.role.value)
        return TokenResponse(
            access_token=access_token,
            refresh_token=token,
            expires_in=15 * 60
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user information
    
    Requires: Valid JWT access token in Authorization header
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout(current_user = Depends(get_current_active_user)):
    """
    Logout user (client-side token deletion)
    
    Note: JWT tokens are stateless, so logout is handled by client
    deleting the token. This endpoint is for logging purposes.
    """
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")
    return {"message": "Logged out successfully"}
