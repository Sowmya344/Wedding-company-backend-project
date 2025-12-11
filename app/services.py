from fastapi import HTTPException, status
from app.models import Organization, Admin, OrgCreateRequest, OrgUpdateRequest
from app.auth import AuthHandler
from app.database import db

class OrganizationService:
    
    @staticmethod
    async def create_organization(data: OrgCreateRequest):
        # 1. Validate uniqueness
        existing_org = await Organization.find_one(Organization.name == data.organization_name)
        if existing_org:
            raise HTTPException(status_code=400, detail="Organization name already exists")
        
        existing_admin = await Admin.find_one(Admin.email == data.email)
        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin email already exists")

        # 2. Prepare Data
        collection_name = f"org_{data.organization_name.lower().replace(' ', '_')}"
        hashed_password = AuthHandler.get_password_hash(data.password)

        # 3. Create Org Entry
        new_org = Organization(
            name=data.organization_name,
            collection_name=collection_name,
            admin_email=data.email
        )
        await new_org.create()

        # 4. Create Admin Entry
        new_admin = Admin(
            email=data.email,
            password_hash=hashed_password,
            organization_id=str(new_org.id)
        )
        await new_admin.create()

        # 5. Initialize Dynamic Collection (Optional: Create a dummy doc to ensure creation)
        tenant_col = await db.get_tenant_collection(collection_name)
        await tenant_col.insert_one({"info": "Genesis block", "created_at": str(new_org.id)})

        return {"message": "Organization created", "org_id": str(new_org.id), "collection": collection_name}

    @staticmethod
    async def get_organization(name: str):
        org = await Organization.find_one(Organization.name == name)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org

    @staticmethod
    async def update_organization(current_admin_email: str, data: OrgUpdateRequest):
        # Fetch current admin to verify ownership/rights
        admin = await Admin.find_one(Admin.email == current_admin_email)
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        
        org = await Organization.get(admin.organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Handle Name Change and Data Migration
        if data.organization_name and data.organization_name != org.name:
            # Check if new name is taken
            if await Organization.find_one(Organization.name == data.organization_name):
                raise HTTPException(status_code=400, detail="New Organization name already taken")

            old_collection = org.collection_name
            new_collection = f"org_{data.organization_name.lower().replace(' ', '_')}"

            # Rename collection in MongoDB (Zero downtime migration usually)
            await db.rename_collection(old_collection, new_collection)

            # Update Metadata
            org.name = data.organization_name
            org.collection_name = new_collection
            await org.save()

        # Update Admin Creds if provided
        if data.email or data.password:
            if data.email:
                admin.email = data.email
                org.admin_email = data.email
            if data.password:
                admin.password_hash = AuthHandler.get_password_hash(data.password)
            await admin.save()
            await org.save()

        return {"message": "Organization updated successfully", "new_name": org.name}

    @staticmethod
    async def delete_organization(current_admin_email: str, organization_name: str):
        # Verify Auth and Target
        admin = await Admin.find_one(Admin.email == current_admin_email)
        org = await Organization.find_one(Organization.name == organization_name)

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Ensure the admin belongs to the org they are trying to delete
        if str(org.id) != admin.organization_id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this organization")

        # Delete Collection
        await db.delete_collection(org.collection_name)

        # Delete Metadata
        await admin.delete()
        await org.delete()

        return {"message": f"Organization {organization_name} and its data have been deleted"}

class AuthService:
    @staticmethod
    async def login(data: AdminLoginRequest):
        admin = await Admin.find_one(Admin.email == data.email)
        if not admin or not AuthHandler.verify_password(data.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = AuthHandler.create_access_token(
            data={"sub": admin.email, "org_id": admin.organization_id}
        )
        return {"access_token": access_token, "token_type": "bearer"}