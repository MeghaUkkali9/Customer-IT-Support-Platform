from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.auth_exception import EmailAlreadyRegisteredException, InvalidCredentialsException
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schema.user import Role

# Compared against when the email doesn't exist, so a login for an unknown email
# takes as long as a wrong password (doesn't reveal which emails are registered)
_DUMMY_HASH = hash_password("dummy-password-for-timing")

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str, role: Role = Role.CUSTOMER) -> User:
        email = email.lower()
        if await self.user_repo.get_by_email(email):
            raise EmailAlreadyRegisteredException(email)

        user = User(email=email, hashed_password=hash_password(password), role=role.value)
        try:
            return await self.user_repo.create(user)
        except IntegrityError:
            # Two registrations for the same email at the same moment
            raise EmailAlreadyRegisteredException(email)

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email.lower())
        if user is None:
            verify_password(password, _DUMMY_HASH)
            raise InvalidCredentialsException()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        return create_access_token(user_id=user.id, role=user.role)

    async def get_user(self, user_id: str) -> User | None:
        return await self.user_repo.get(user_id)
