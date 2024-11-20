from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hash: str) -> bool:
    return pwd_context.verify(plain, hash)


def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def get_jwt_username(token:str) -> str | None:
    """Return username from JWT access <token>"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not (username := payload.get("sub")):
            return None
    except ExpiredSignatureError:
        raise InvalidBearerToken(msg="Token is expired.")
    except JWTError as e:
        raise InvalidBearerToken(msg="Token is invalid, or has been tempered with.")
    return username


def create_access_token(data: dict, expires_delta: timedelta | None = None ) -> Token:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token: Token = Token(
            access_token=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM),
            token_type="Bearer"
            )
    return token


def auth_user(username: str, plain: str) -> User:
    """Authenticate user <name> and <plain> password"""
    user: User = lookup_user(username=username)
    if not verify_password(plain, user.hash):
        raise IncorectCredentials("Incorrect Credentials")
    return user

def handle_token_creation(username:str, plain:str) -> Token:
    
    # Checks username and password validity
    user: User = auth_user(username=username, plain=plain)
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token: Token = create_access_token(data={"sub":user.username}, expires_delta=expires_delta)
    return token

    

# -------------------------------------
#   Stripping down public user
# -------------------------------------

def lookup_user(username: str) -> User:
    """Return a matching User fron the database for <name>"""
    user: User = data.get_by(field="username", value=username)
    return user

def get_current_user(token: str) -> User:
    """Decode an OAuth access <token> and return the User"""
    if not (username := get_jwt_username(token)):
        raise InvalidBearerToken("Invalid Bearer Token")
    if (user := lookup_user(username)):
        return user

def user_to_pub_user(user: User) -> PublicUser:
    return PublicUser(
            uuid=user.uuid,
            username=user.username,
            email=user.email,
            role=user.role
            )
