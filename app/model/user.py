from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class UserRoleEnum(Enum):
    admin = "admin"
    coach = "coach"
    user  = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: Optional[str] = Field(..., max_length=36, min_length=36)
    username: str
    email: str
    hash: str
    role: UserRoleEnum

class UserCreate(BaseModel):
    id: Optional[str] = Field(..., max_length=36, min_length=36)
    username: str
    email: str
    password: str = Field(..., min_length=12, max_length=128)
    role: UserRoleEnum
