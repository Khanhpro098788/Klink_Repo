import motor.motor_asyncio
from qdrant_client import AsyncQdrantClient
from app.config import settings

class DatabaseManager:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.qdrant_client = None

    def connect(self):
        # Initialize Motor Async MongoClient
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.mongo_client[settings.MONGODB_DB_NAME]
        
        # Initialize Async Qdrant Client if host is configured
        if settings.QDRANT_HOST:
            self.qdrant_client = AsyncQdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
            )

    def disconnect(self):
        if self.mongo_client:
            self.mongo_client.close()

db_manager = DatabaseManager()

async def get_mongodb():
    if db_manager.db is None:
        db_manager.connect()
    return db_manager.db

async def get_qdrant():
    if db_manager.qdrant_client is None:
        db_manager.connect()
    return db_manager.qdrant_client
