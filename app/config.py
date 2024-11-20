from dotenv import load_dotenv
import os
from app.exception.service import InvalidConstantValue

load_dotenv()

SECRET_KEY_ENV = os.getenv("SECRET_KEY")
if SECRET_KEY_ENV is None:
    raise InvalidConstantValue("Secret Key value is None. Exitting")

ALGORITHM_ENV = os.getenv("ALGORITHM")
if ALGORITHM_ENV is None:
    raise InvalidConstantValue("ALGORITHM value is None. Exitting")

ACCESS_TOKEN_EXPIRE_MINUTES_ENV = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if ACCESS_TOKEN_EXPIRE_MINUTES_ENV is None:
    raise InvalidConstantValue("Access token expire minutes value is None. Exitting")

DEFAULT_USER_ENV = os.getenv("DEFAULT_USER")
if DEFAULT_USER_ENV is None:
    raise InvalidConstantValue("Access token expire minutes value is None. Exitting")

DEFAULT_PASSWORD_ENV = os.getenv("DEFAULT_PASSWORD")
if DEFAULT_PASSWORD_ENV is None:
    raise InvalidConstantValue("Access token expire minutes value is None. Exitting")

DEFAULT_EMAIL_ENV = os.getenv("DEFAULT_EMAIL")
if DEFAULT_EMAIL_ENV is None:
    raise InvalidConstantValue("Access token expire minutes value is None. Exitting")

SECRET_KEY = str(SECRET_KEY_ENV)
ALGORITHM = str(ALGORITHM_ENV)
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES_ENV)

DEFAULT_USER = str(DEFAULT_USER_ENV)
DEFAULT_EMAIL = str(DEFAULT_EMAIL_ENV)
DEFAULT_PASSWORD = str(DEFAULT_PASSWORD_ENV)


