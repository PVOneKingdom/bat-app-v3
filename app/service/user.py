from fastapi import Request
from passlib import context
import secrets
import re
from datetime import datetime, timedelta, timezone
from app.config import DEFAULT_USER, DEFAULT_EMAIL, DEFAULT_PASSWORD

from app.data import user as data
from app.exception.database import RecordNotFound
from app.exception.service import (
    EndpointDataMismatch,
    IncorectCredentials,
    InvalidFormEntry,
    PasswordResetTokenExpired,
    SendingEmailFailed,
    Unauthorized,
    SMTPCredentialsNotSet,
)
from app.service.authentication import get_password_hash
from app.service.mail import notify_user_created, send_password_reset
from app.model.user import (
    User,
    UserCreate,
    UserPasswordResetToken,
    UserRoleEnum,
    UserSetNewPassword,
    UserUpdate,
)
from uuid import uuid4

# -------------------------------
#   Add default user
# -------------------------------


def add_default_user():

    try:
        users = data.get_all()
        print("Users already present in the database")
        return
    except RecordNotFound as e:
        print("No users found. Creating default one.")

    new_uuid = str(uuid4())

    username = DEFAULT_USER
    email = DEFAULT_EMAIL.lower()
    password = DEFAULT_PASSWORD
    hash: str = ""

    if username is not None and email is not None and password is not None:
        hash = get_password_hash(password)
    else:
        print("Default values for username, admin or password not defined")
        return

    user_object = User(
        user_id=new_uuid,
        username=username,
        email=email,
        hash=hash,
        role=UserRoleEnum.admin,
    )

    new_user = data.create(user_object)

    return new_user


# -------------------------------
#   Basic CRUD operations
# -------------------------------


def create(user: UserCreate, request: Request, current_user: User) -> User:

    if not current_user.can_create_user(user):
        raise Unauthorized(msg="You cannot create this user")

    new_uuid = str(uuid4())

    if user.password:
        if len(user.password) < 12:
            raise InvalidFormEntry(
                msg="Password too short. It needs to be at least 12 characters"
            )
        elif len(user.password) > 128:
            raise InvalidFormEntry(
                msg="Password too long. Sorry we support only up to 128 characters."
            )
    else:
        user.password = secrets.token_urlsafe(128)

    try:
        new_user = data.create(
            User(
                user_id=new_uuid,
                username=user.username,
                email=user.email.lower(),
                hash=get_password_hash(user.password),
                role=user.role,
            )
        )
    except Exception as e:
        print(f"Failed to create user: {e}")
        raise e

    notify_user_created(new_user=new_user, request=request, current_user=current_user)

    return new_user


def get(user_id: str, current_user: User) -> User:

    requesting_own_profile: bool = False
    is_coach_or_admin: bool = False

    if (
        current_user.role == UserRoleEnum.admin
        or current_user.role == UserRoleEnum.coach
    ):
        is_coach_or_admin = True

    if current_user.user_id == user_id:
        requesting_own_profile = True

    if not requesting_own_profile and not is_coach_or_admin:
        raise Unauthorized(msg="You cannot list this user. Insufficient permissions.")

    user = data.get_one(user_id)
    return user


def get_all(current_user: User) -> list[User]:

    if (
        current_user.role != UserRoleEnum.admin
        and current_user.role != UserRoleEnum.coach
    ):
        raise Unauthorized(msg="You cannot list all users, insufficient rights")

    users = data.get_all()
    return users


def get_by_token(token: str) -> User:

    user = data.get_by_token(token=token)
    if user.user_id:
        token_object = data.get_password_reset_token(user_id=user.user_id)
        now = datetime.now(timezone.utc)
        now_int = int(now.timestamp())
        if (
            token_object.reset_token_expires
            and now_int > token_object.reset_token_expires
        ):
            raise PasswordResetTokenExpired(
                msg="Reset token is expired. Apply for new one and try again."
            )

    return user


def get_by_email(email: str, current_user: User) -> User:

    if (
        current_user.role != UserRoleEnum.admin
        and current_user.role != UserRoleEnum.coach
    ):
        raise Unauthorized(msg="You cannot list all users, insufficient rights")

    return data.get_by(field="email", value=email)


def username_from_email(email: str) -> str:

    email = email.lower()
    allowed_chars = r"^[a-zA-Z0-9@._-]+$"

    if not re.fullmatch(allowed_chars, email):
        raise IncorectCredentials(msg="Invalid characters found in email address.")

    if not email:
        raise IncorectCredentials(msg="Email address is empty.")

    return data.username_from_mail(email=email)


def get_by_username(username: str, current_user: User) -> User:

    if (
        current_user.role != UserRoleEnum.admin
        and current_user.role != UserRoleEnum.coach
    ):
        raise Unauthorized(msg="You cannot list all users, insufficient rights")

    return data.get_by(field="username", value=username)


def delete(user_id: str, current_user: User) -> User:

    user_for_deletion: User = data.get_one(user_id)
    if current_user.can_delete_user(user_for_deletion):
        deleted_user = data.delete(user_id)
    else:
        raise Unauthorized(msg="You cannot perform this action")

    return deleted_user


def update(user_id: str, user: UserUpdate, current_user: User) -> User:

    if user_id != user.user_id:
        raise EndpointDataMismatch(
            msg="Endpoint UUID and data UUID are not matching. Something fishy? Or try contacting your admin."
        )

    if not current_user.can_modify_user(user):
        raise Unauthorized(msg="You cannot modify this user")

    current_data: User = data.get_one(user_id)

    if user.password:
        password_hash = get_password_hash(user.password)
    else:
        password_hash = current_data.hash

    updated_data = User(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        hash=password_hash,
        role=user.role,
    )

    modified_user = data.modify(user_id, updated_data)
    return modified_user


def create_password_reset_token(email: str, request: Request) -> bool:

    try:
        user: User = data.get_by(field="email", value=email)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=60)
        reset_token: str = secrets.token_hex(64)
        token_expires: int = int(expires_at.timestamp())
        if not type(user.user_id) == str:
            raise RecordNotFound(msg="User id is not valid id")
        reset_token_object = data.set_password_reset_token(
            user_id=user.user_id, token=reset_token, token_expires=token_expires
        )
    except RecordNotFound as e:
        # Email not found but for preventing leaking infromation
        # no handle should be added here. Unless we want to track if someone
        # is brute forcing the password resset functionality for some reason
        print(f"User with email {email} wasn't found")
        return False

    try:
        send_password_reset(token_object=reset_token_object, request=request)
        return True
    except SendingEmailFailed as e:
        print(f"Failed sending password reset e-mail for: {email}.")
        return False


def set_password_with_token(set_new_password: UserSetNewPassword) -> User:

    password_hash = get_password_hash(set_new_password.password)
    return data.set_password_from_token(
        user_id=set_new_password.user_id,
        token=set_new_password.token,
        password_hash=password_hash,
    )
