from fastapi import APIRouter
from app.api import auth, users

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)

__all__ = ["api_router"]