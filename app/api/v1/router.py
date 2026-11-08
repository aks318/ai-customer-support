from fastapi import APIRouter

from app.api.v1.endpoints import auth, conversations, health

router = APIRouter()

router.include_router(
    health.router,
    tags=["health"]
)

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["Conversations"]
)