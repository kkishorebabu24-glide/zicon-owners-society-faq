"""Menu management routes"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/menus", tags=["menus"])


@router.get("/sellers/{seller_id}")
async def get_seller_menus(seller_id: int):
    """Get all available menu items for a seller"""
    # TODO: Implement get seller menus
    return {"items": []}


@router.post("/")
async def create_menu_item(seller_id: int, name: str, category: str, price: float):
    """Create a new menu item (seller only)"""
    # TODO: Implement create menu item
    return {"id": 1, "name": name, "category": category, "price": price}


@router.put("/{menu_id}")
async def update_menu_item(menu_id: int, name: str = None, price: float = None):
    """Update menu item (seller only)"""
    # TODO: Implement update menu item
    return {"message": "Menu item updated"}


@router.delete("/{menu_id}")
async def delete_menu_item(menu_id: int):
    """Delete menu item (seller only)"""
    # TODO: Implement delete menu item
    return {"message": "Menu item deleted"}


@router.patch("/{menu_id}/availability")
async def toggle_availability(menu_id: int, is_available: bool):
    """Toggle menu item availability (seller only)"""
    # TODO: Implement toggle availability
    return {"is_available": is_available}
