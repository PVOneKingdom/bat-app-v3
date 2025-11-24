from dotenv import load_dotenv
import os
from pathlib import Path
from app.exception.service import InvalidConstantValue

load_dotenv()

# Centralized path configuration for single volume deployment
# All persistent data stored under /app/data/ directory
APP_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = APP_ROOT / "data"
DB_DIR = DATA_ROOT / "db"
UPLOADS_DIR = DATA_ROOT / "uploads"
DB_PATH = DB_DIR / "database.db"

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

FORCE_HTTPS_PATHS_ENV = os.getenv("FORCE_HTTPS_PATHS")

CF_TURNSTILE_SITE_KEY = os.getenv("CF_TURNSTILE_SITE_KEY")
CF_TURNSTILE_SECRET_KEY = os.getenv("CF_TURNSTILE_SECRET_KEY")

if CF_TURNSTILE_SITE_KEY and CF_TURNSTILE_SECRET_KEY:
    CF_TURNSTILE_ENABLED = True
else:
    CF_TURNSTILE_ENABLED = False

SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")


if ( SMTP_LOGIN is None or SMTP_PASSWORD is None or SMTP_EMAIL is None
    or SMTP_SERVER is None or SMTP_PORT is None ):
    SMTP_ENABLED = False
else:
    SMTP_ENABLED = True



SECRET_KEY = str(SECRET_KEY_ENV)
ALGORITHM = str(ALGORITHM_ENV)
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES_ENV)

DEFAULT_USER = str(DEFAULT_USER_ENV)
DEFAULT_EMAIL = str(DEFAULT_EMAIL_ENV)
DEFAULT_PASSWORD = str(DEFAULT_PASSWORD_ENV)
