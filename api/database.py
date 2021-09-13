from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

import settings


class DataBase:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

mongo_obj = DataBase()

def get_client() -> AsyncIOMotorClient:
    return mongo_obj.client

def get_db() -> AsyncIOMotorDatabase:
    return mongo_obj.db

async def connect_db():
    mongo_obj.client = AsyncIOMotorClient(settings.MONGO_URL)
    mongo_obj.db = mongo_obj.client.get_database(settings.MONGO_DB)

async def close_db():
    mongo_obj.client.close()
