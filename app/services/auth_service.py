from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister


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