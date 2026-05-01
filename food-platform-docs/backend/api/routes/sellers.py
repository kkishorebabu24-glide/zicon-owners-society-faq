"""Seller management routes"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/sellers", tags=["sellers"])


@router.get("/")
async def list_sellers(skip: int = 0, limit: int = 20):
    """List all approved sellers"""
    # TODO: Implement list sellers
    return {"sellers": [], "total": 0}


@router.post("/register")
async def register_seller(name: str, bio: str):
    """Register as a seller"""
    # TODO: Implement seller registration
    return {"message": "Registration submitted for admin approval"}


@router.get("/{seller_id}")
async def get_seller(seller_id: int):
    """Get seller profile and rating"""
    # TODO: Implement get seller
    return {"id": seller_id, "name": "Seller Name", "rating": 4.5}


@router.put("/{seller_id}")
async def update_seller(seller_id: int, bio: str = None):
    """Update seller profile (seller only)"""
    # TODO: Implement update seller
    return {"message": "Profile updated"}


@router.delete("/{seller_id}")
async def delete_seller(seller_id: int):
    """Delete seller account (seller only)"""
    # TODO: Implement delete seller
    return {"message": "Account deleted"}
