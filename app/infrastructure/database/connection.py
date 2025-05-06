import aiomysql
from app.config import settings
from datetime import datetime, timedelta

db_pool = None

async def init_db_pool():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        db=settings.DB_NAME,
        minsize=1,
        maxsize=5,
    )

async def get_db_connection():
    global db_pool
    if db_pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() at startup.")
    async with db_pool.acquire() as conn:
        yield conn