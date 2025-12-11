from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr

# --- Database Models (Master DB) ---

class Organization(Document):
    name: Indexed(str, unique=True) # Unique Organization Name
    collection_name: str
    admin_email: str
    
    class Settings:
        name = "organizations"

class Admin(Document):
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    organization_id: str # Link to Organization ID
    
    class Settings:
        name = "admins"

# --- Request/Response Schemas ---

class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdateRequest(BaseModel):
    organization_name: str # New Name
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str