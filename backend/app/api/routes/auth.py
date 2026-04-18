# Authentication routes

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# TODO: Implement endpoints
# - POST /register
# - POST /login
# - POST /refresh
# - POST /logout
# - GET /me
