from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import UserRegister, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserRegister):
    try:
        return await AuthService.register_user(user)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )