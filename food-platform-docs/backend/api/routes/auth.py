"""Authentication routes"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register")
async def register(email: str, role: str):
    """
    Register a new user and send OTP to email

    - **email**: User email address
    - **role**: User role (buyer | seller | admin)
    """
    # TODO: Implement user registration
    return {"message": "OTP sent to email"}


@router.post("/login")
async def login(email: str, otp: str):
    """
    Verify OTP and return JWT token

    - **email**: User email address
    - **otp**: 6-digit OTP code
    """
    # TODO: Implement OTP verification
    return {"access_token": "token", "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token():
    """Refresh access token using refresh token"""
    # TODO: Implement token refresh
    return {"access_token": "new_token", "token_type": "bearer"}


@router.get("/me")
async def get_current_user():
    """Get current authenticated user information"""
    # TODO: Implement get current user
    return {"id": 1, "email": "user@example.com", "role": "buyer"}


@router.post("/logout")
async def logout():
    """Logout current user"""
    # TODO: Implement logout
    return {"message": "Logged out successfully"}
