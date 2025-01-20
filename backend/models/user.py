from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class TokenData(BaseModel):
    username: Optional[str] = None
    
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str