from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Organization, Admin
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGO_URI)
        # Initialize Master DB Models
        await init_beanie(database=cls.client[settings.MASTER_DB_NAME], document_models=[Organization, Admin])
        print("Connected to Master Database")

    @classmethod
    async def get_tenant_collection(cls, collection_name: str):
        """Returns a reference to the dynamic collection within the Master DB (or separate DB)"""
        # Strategy: We keep tenant collections in the SAME database but with prefixes 
        # to simplify connection management, though separate DBs are also valid.
        return cls.client[settings.MASTER_DB_NAME][collection_name]
    
    @classmethod
    async def rename_collection(cls, old_name: str, new_name: str):
        db = cls.client[settings.MASTER_DB_NAME]
        # Check if old collection exists
        cols = await db.list_collection_names()
        if old_name in cols:
            await db[old_name].rename(new_name)
    
    @classmethod
    async def delete_collection(cls, collection_name: str):
        db = cls.client[settings.MASTER_DB_NAME]
        await db[collection_name].drop()

db = Database()