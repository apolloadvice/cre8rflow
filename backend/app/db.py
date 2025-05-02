import asyncpg
from typing import Optional
from contextlib import asynccontextmanager

from app.core.config import settings


class Database:
    """Database connection manager for asyncpg pool."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def connect(self):
        """Create database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                user=settings.postgres_user,
                password=settings.postgres_password,
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                min_size=5,
                max_size=20
            )
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def connection(self):
        """Get a connection from the pool as a context manager."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            yield conn


# Create a global instance
db = Database() 