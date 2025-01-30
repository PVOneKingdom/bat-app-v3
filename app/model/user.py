from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional
from app.model.assesment import Assessment


class UserRoleEnum(Enum):
    admin = "admin"
    coach = "coach"
    user  = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    user_id: Optional[str] = Field(None, max_length=36, min_length=36)
    username: str
    email: str
    password: str
    role: UserRoleEnum


class UserUpdate(BaseModel):
    user_id: Optional[str] = Field(None, max_length=36, min_length=36)
    username: str
    email: str
    password: Optional[str] = Field(None, min_length=12, max_length=128)
    role: UserRoleEnum

    @field_validator("password", mode="before")
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value


class UserPasswordResetToken(BaseModel):
    user_id: str = Field(..., max_length=36, min_length=36)
    password_reset_token: str | None
    reset_token_expires: str | None


class User(BaseModel):
    user_id: Optional[str] = Field(..., max_length=36, min_length=36)
    username: str
    email: str
    hash: str
    role: UserRoleEnum

    def can_grant_roles(self) -> list:
        if self.role == UserRoleEnum.admin:
            return ["admin", "coach", "user"]
        if self.role == UserRoleEnum.coach:
            return ["coach", "user"]
        else:
            return []

    def can_create_user(self, new_user) -> bool:
        if self.role == UserRoleEnum.admin:
            return True
        if self.role == UserRoleEnum.coach:
            if new_user.role == UserRoleEnum.coach:
                return True
            if new_user.role == UserRoleEnum.user:
                return True
        else:
            return False
        return False

    def can_delete_user(self, user_for_deletion) -> bool:
        if self.role == UserRoleEnum.admin:
            return True
        if self.role == UserRoleEnum.coach:
            return False if user_for_deletion.role == UserRoleEnum.admin else True
        else:
            return False


    def can_modify_user(self, user_for_modification) -> bool:
        if self.user_id == user_for_modification.user_id:
            return True
        if self.role == UserRoleEnum.admin:
            return True
        if (
            self.role == UserRoleEnum.coach
            and (
                user_for_modification.role == UserRoleEnum.coach
                or user_for_modification.role == UserRoleEnum.user
                )
            ):
            return True
        else:
            return False

    def can_manage_questions(self) -> bool:
        if self.role == UserRoleEnum.admin or self.role == UserRoleEnum.coach:
            return True
        return False

    def can_manage_assessments(self) -> bool:
        if self.role == UserRoleEnum.admin or self.role == UserRoleEnum.coach:
            return True
        return False

    def can_manage_notes(self) -> bool:
        if self.role == UserRoleEnum.admin or self.role == UserRoleEnum.coach:
            return True
        return False

    def can_manage_reports(self) -> bool:
        if self.role == UserRoleEnum.admin or self.role == UserRoleEnum.coach:
            return True
        return False

    def can_send_emails(self) -> bool:
        if self.role == UserRoleEnum.admin or self.role == UserRoleEnum.coach:
            return True
        return False
