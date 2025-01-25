import jwt
import logging
import sqlite3
from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
from routers import analysis, model
from utils.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    add_token_to_blacklist,
    get_db,
    oauth2_scheme,
    is_token_blacklisted,
    get_user,
    SECRET_KEY, 
    ALGORITHM
)
from utils.logger import LoggerMiddleware
from models.user import SignupRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.mount("/output", StaticFiles(directory="output"), name="output")

app.add_middleware(LoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,  # Required for cookies/auth headers
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    logger.info(f"Extracted token from cookies: {token}")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = get_user(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup", status_code=201)
def signup(user: SignupRequest, db=Depends(get_db)):
    cursor = db.cursor()
    hashed_password = get_password_hash(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (username, email, full_name, hashed_password) VALUES (?, ?, ?, ?)",
            (user.username, user.email, user.full_name, hashed_password),
        )
        db.commit()
        logger.info(f"User {user.username} signed up successfully.")
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400, detail="Username or email already exists"
        )
    finally:
        db.close()
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username}, expires_delta=timedelta(hours=1))
    logger.info(f"Generated access token for user {user.username}: {access_token}")
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=False,
        samesite="Lax",
    )
    return response

@app.post("/logout")
def logout(request: Request, response: Response, db=Depends(get_db)):
    token = request.cookies.get("access_token")
    logger.info(f"Logout request received. Token: {token}")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been invalidated",
        )

    add_token_to_blacklist(db, token)
    db.close()
    response.delete_cookie("access_token")
    logger.info("Token successfully invalidated and cookie cleared.")
    
    return {"message": "Logged out successfully"}

@app.post("/validate-token")
def validate_token(request: Request):
    token = request.cookies.get("access_token")
    logger.info(f"Validating token: {token}")
    
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"message": "Token is valid"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

app.include_router(analysis.router)
app.include_router(model.router)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Analysis App is running"}
