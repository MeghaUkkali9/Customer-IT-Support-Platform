from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Role(str, Enum):
    CUSTOMER = "customer"
    AGENT = "agent"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    role: Role

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
