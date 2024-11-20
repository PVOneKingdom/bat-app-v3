from pydantic import BaseModel
from enum import Enum
from typing import Optional


class UserRole(Enum):
    admin = "admin"
    coach = "coach"
    user  = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: Optional[str]
    username: str
    email: str
    hash: str
    role: UserRole
