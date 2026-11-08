from pydantic import conset

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLogin, UserRegister


class AuthService:

    @staticmethod
    async def register_user(user: UserRegister):

        hashed_password = hash_password(user.password)

        user_data = {
            "name": user.name,
            "email": str(user.email).lower(),
            "password_hash": hashed_password
        }

        return await UserRepository.create_user(user_data)

    @staticmethod
    async def login_user(user: UserLogin):
        db_user = await UserRepository.get_by_email(
            str(user.email).lower()
        )

        if not db_user:
            raise ValueError("Invalid email or password")

        is_valid = verify_password(
            user.password,
            db_user["password_hash"]
        )

        if not is_valid:
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            str(db_user["_id"])
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }