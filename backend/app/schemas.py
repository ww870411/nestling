from pydantic import BaseModel
from typing import Optional, Dict, Any, List

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

# --- Template Schemas ---

class TemplateField(BaseModel):
    field_id: int
    name: str
    label: str
    type: str
    component: str
    width: Optional[int] = None
    fixed: Optional[Any] = None # Allow boolean or other types
    formula: Optional[str] = None

    class Config:
        orm_mode = True

class TemplateMetric(BaseModel):
    metric_id: int
    category: str
    name: str
    unit: Optional[str] = None
    type: str
    formula: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    same_period_editable: Optional[Any] = None # Allow boolean or other types
    required_properties: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class ReportTemplate(BaseModel):
    metrics: List[TemplateMetric]
    fields: List[TemplateField]

    class Config:
        orm_mode = True
