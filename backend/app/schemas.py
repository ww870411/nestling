from pydantic import BaseModel
from typing import Optional, Dict, Any

# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# --- User Schemas ---

# Schema for creating a new user
class UserCreate(BaseModel):
    username: str
    password: str
    unit: str
    global_role: Optional[str] = None
    roles_by_project: Optional[Dict[str, Any]] = None

# Schema for reading/returning a user from the API
class User(BaseModel):
    id: int
    username: str
    unit: str
    global_role: Optional[str] = None
    roles_by_project: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True # This allows the model to be created from an ORM object
