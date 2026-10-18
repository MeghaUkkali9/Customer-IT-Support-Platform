from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

settings = get_settings()

# Reads "Authorization: Bearer <token>"; adds an "Authorize" button to /docs
bearer_scheme = HTTPBearer(auto_error=False)

@dataclass(frozen=True)
class CurrentUser:
    id: str
    role: str

    @property
    def is_agent(self) -> bool:
        return self.role == "agent"

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> CurrentUser:
    # Tokens are issued by auth-service. This service only checks the signature and
    # expiry with the shared secret; it never talks to the users database.
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "role", "exp"]},
        )
    except jwt.InvalidTokenError:
        raise unauthorized
    return CurrentUser(id=claims["sub"], role=claims["role"])

def require_agent(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not user.is_agent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agents only")
    return user
