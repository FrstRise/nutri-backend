from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()

# Global client — created once, reused across requests
_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client


def get_db():
    """Return the database instance."""
    return get_client()[settings.mongo_db_name]


async def ping_db() -> bool:
    """Check MongoDB connectivity on startup."""
    try:
        await get_client().admin.command("ping")
        return True
    except Exception as e:
        print(f"[DB] MongoDB connection failed: {e}")
        return False


async def close_db():
    """Close MongoDB connection on app shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None
