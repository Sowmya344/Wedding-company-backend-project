from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database import db
from app.models import OrgCreateRequest, OrgUpdateRequest, AdminLoginRequest, TokenResponse
from app.services import OrganizationService, AuthService
from app.auth import AuthHandler

app = FastAPI(title="Organization Management Service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

# --- Dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = AuthHandler.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("sub") # Returns email

# --- Events ---
@app.on_event("startup")
async def start_db():
    await db.connect()

# --- Routes ---

@app.post("/org/create", status_code=201)
async def create_organization(payload: OrgCreateRequest):
    return await OrganizationService.create_organization(payload)

@app.get("/org/get")
async def get_organization(organization_name: str):
    return await OrganizationService.get_organization(organization_name)

@app.put("/org/update")
async def update_organization(payload: OrgUpdateRequest, user_email: str = Depends(get_current_user)):
    return await OrganizationService.update_organization(user_email, payload)

@app.delete("/org/delete")
async def delete_organization(organization_name: str, user_email: str = Depends(get_current_user)):
    return await OrganizationService.delete_organization(user_email, organization_name)

@app.post("/admin/login", response_model=TokenResponse)
async def login(payload: AdminLoginRequest):
    return await AuthService.login(payload)