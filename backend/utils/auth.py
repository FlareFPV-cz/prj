import os
import jwt
import sqlite3
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models.user import User, UserInDB, TokenData

# Load environment variables
load_dotenv(".env")

DB_PATH = os.getenv("DB_PATH", "users.db")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Secure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased bcrypt rounds for security
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Database connection
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)  # Set timeout to prevent locking issues
    conn.row_factory = sqlite3.Row
    return conn

# Blacklist token storage (JWT invalidation)
def add_token_to_blacklist(db, token: str):
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO token_blacklist (token) VALUES (?)", (token,))
        db.commit()
    except sqlite3.IntegrityError:
        pass  # Prevent duplicate entries

def is_token_blacklisted(db, token: str) -> bool:
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM token_blacklist WHERE token = ? LIMIT 1", (token,))
    return cursor.fetchone() is not None

# Password security functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Secure user retrieval with parameterized queries
def get_user(db, username: str) -> Optional[UserInDB]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    return UserInDB(**user) if user else None

# User authentication
def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    db = get_db()
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None  # Do NOT reveal if the username is invalid
    return user

# Secure JWT creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Secure token validation and retrieval
def get_current_user(request: Request, db=Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    
    if not token or is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode JWT securely
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        exp: int = payload.get("exp")

        # Ensure token is not expired
        if exp is None or datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user securely
    user = get_user(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user