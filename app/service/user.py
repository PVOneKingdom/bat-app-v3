from app.config import  DEFAULT_USER, \
        DEFAULT_EMAIL, DEFAULT_PASSWORD

from app.data import user as data
from app.service.auth import get_password_hash
from app.model.user import User, UserRoleEnum
from uuid import uuid4
# -------------------------------
#   Add default user
# -------------------------------

def add_default_user():

    new_uuid = str(uuid4())

    username = DEFAULT_USER
    email = DEFAULT_EMAIL
    password = DEFAULT_PASSWORD
    hash: str = ""

    if username is not None and email is not None and password is not None:
        hash = get_password_hash(password)
    else:
        print("Default values for username, admin or password not defined")
        return 

    user_object = User(
        id=new_uuid,
        username=username,
        email=email,
        hash=hash,
        role=UserRoleEnum.admin
        )

    new_user = data.create(user_object)

    return new_user

