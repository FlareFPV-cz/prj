import sqlite3
from fastapi import FastAPI
from routers import analysis
from datetime import timedelta
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from dependencies.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    # init_db,
    add_token_to_blacklist,
    get_db,
    get_current_active_user,
    oauth2_scheme,
    is_token_blacklisted
)
from models.user import SignupRequest

# init_db()

app = FastAPI()

app.mount("/output", StaticFiles(directory="output"), name="output")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400, detail="Username or email already exists"
        )
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    if is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been invalidated",
        )
    add_token_to_blacklist(db, token)
    return {"message": "Logged out successfully"}


app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "Analysis App is running"}
