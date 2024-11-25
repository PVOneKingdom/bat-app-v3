from fastapi import HTTPException, Request
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, \
        SECRET_KEY, ALGORITHM

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from app.exception.database import RecordNotFound
from app.exception.web import NonHTMXRequestException, RedirectToLoginException
from app.exception.service import IncorectCredentials, InvalidBearerToken
from app.model.user import User

# Function to retrieve the user and pasword hash
from app.data.user import get_one as get_user_by_user_id
from app.data.user import get_by as get_user_by


"""From all of this, there are 2 main functions to keep in mind.
1) handle_token_creation()
    - takes in username and password and creates token if credentials valid
2) get_current_user()
    - takes in token and returns user if token is valid"""


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)


def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def jwt_to_user_id(token:str) -> str | None:
    """Return user id from JWT access <token>"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not (username := payload.get("user_id")):
            return None
    except ExpiredSignatureError:
        raise InvalidBearerToken(msg="Token is expired.")
    except JWTError as e:
        raise InvalidBearerToken(msg="Token is invalid, or has been tempered with.")
    return username



def generate_bearer_token(data: dict, expires_delta: timedelta | None = None ) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token_value = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    bearer_token = f"Bearer {token_value}"
    return bearer_token


def auth_user(username: str, password: str) -> User:
    """Authenticate user <name> and <plain> password"""
    user: User = get_user_by(field="username", value=username)
    if not verify_password(password=password, hash=user.hash):
        raise IncorectCredentials("Incorrect Credentials")
    return user

def handle_token_creation(username:str, password:str) -> str:
    """Handles creation on the sign in. Takes in username and password and returns 
    bearer token: Bearer <token-value>."""
    # Checks username and password validity
    user: User = auth_user(username=username, password=password)
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token: str = generate_bearer_token(data={"user_id":user.user_id}, expires_delta=expires_delta)
    return token

    

# -------------------------------------
#   Retrieving the User Object
# -------------------------------------

def lookup_user(user_id: str) -> User:
    """Return a matching User fron the database for ID"""
    user: User = get_user_by_user_id(user_id=user_id)
    return user

def get_current_user(token: str) -> User | None:
    """Dependecy that extracts data from token and returns User object"""

    if not (user_id := jwt_to_user_id(token)):
        raise InvalidBearerToken("Invalid Bearer Token")
    if (user := get_user_by_user_id(user_id=user_id)):
        return user


async def user_htmx_dep(request: Request) -> User | None:

    is_htmx = request.headers.get("HX-Request") == "true"
    token = request.headers.get("Authorization")

    if not is_htmx:
        raise NonHTMXRequestException(detail="Wait while we redirect your request.")

    if token:
        token_stripped = token.split("Bearer ")[1]
        try:
            current_user = get_current_user(token=token_stripped)
            return current_user
        except InvalidBearerToken as e:
            raise RedirectToLoginException(detail=e.msg)
        
    raise RedirectToLoginException(detail="Unauthorized, probalby expired session or not loged in.")


