import rsa
import jwt
import base64
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
from routers import analysis, model, crop_health
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

app = FastAPI(
    title="PRJ API",
    description="An API for soil analysis, vegetation indices, and geospatial data processing.",
    version="0.0.1",
    contact={
        "name": "Jan Kozeluh",
        "url": "https://www.linkedin.com/in/jan-kozeluh/",
        "email": "jankozeluh.job@seznam.cz",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
with open("public.pem", "r") as f:
    PUBLIC_KEY = f.read()
    
with open("private.pem", "rb") as f:
    PRIVATE_KEY = rsa.PrivateKey.load_pkcs1(f.read())
    
app.add_middleware(LoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,  # Required for cookies/auth headers
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.mount("/output", StaticFiles(directory="output"), name="output")

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

def decrypt_password(encrypted_password: str) -> str:
    try:
        logger.info(f"Received encrypted password: {encrypted_password}")
        
        # Decode from Base64
        decrypted_bytes = rsa.decrypt(base64.b64decode(encrypted_password), PRIVATE_KEY)
        return decrypted_bytes.decode()
    
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid encryption")

@app.post("/signup", tags=["Auth"])
def signup(user: SignupRequest, db=Depends(get_db)):
    decrypted_password = decrypt_password(user.password)  # Decrypt before hashing
    hashed_password = get_password_hash(decrypted_password)  # Now hash it

    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, full_name, hashed_password) VALUES (?, ?, ?, ?)",
            (user.username, user.email, user.full_name, hashed_password),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400, detail="Username or email already exists"
        )
    finally:
        db.close()
    return {"message": "User created successfully"}

@app.post("/login", tags=["Auth"])
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

@app.post("/logout", tags=["Auth"])
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

@app.post("/validate-token", tags=["Auth"])
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

@app.get("/public-key", tags=["Auth"])
def get_public_key():
    return {"public_key": PUBLIC_KEY}

app.include_router(
    analysis.router,
    tags=["Soil Analysis"]
)

app.include_router(
    model.router,
    tags=["ML Models"]
)

app.include_router(
    crop_health.router,
    tags=["Crop Health"]
)

@app.get("/", tags=["Test"])
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Analysis App is running"}
