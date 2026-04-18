# Telegram webhook routes

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])

# TODO: Implement endpoints
# - POST /webhook (receive Telegram updates)
# - POST /config (configure bot groups)
# - GET /groups (list configured groups)
