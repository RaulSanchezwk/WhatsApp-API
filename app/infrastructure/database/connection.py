import aiomysql
from app.config import settings
from contextlib import asynccontextmanager

citas_db_pool = None
webhook_db_pool = None

async def init_db_pools():
    global citas_db_pool, webhook_db_pool

    citas_db_pool = await aiomysql.create_pool(
        host=settings.CITAS_DB_HOST,
        port=int(settings.CITAS_DB_PORT),
        user=settings.CITAS_DB_USER,
        password=settings.CITAS_DB_PASSWORD,
        db=settings.CITAS_DB_NAME,
        minsize=1,
        maxsize=5,
    )

    webhook_db_pool = await aiomysql.create_pool(
        host=settings.WEBHOOK_DB_HOST,
        port=int(settings.WEBHOOK_DB_PORT),
        user=settings.WEBHOOK_DB_USER,
        password=settings.WEBHOOK_DB_PASSWORD,
        db=settings.WEBHOOK_DB_NAME,
        minsize=1,
        maxsize=5,
    )

async def get_citas_connection():
    if citas_db_pool is None:
        raise Exception("Citas DB pool not initialized.")
    async with citas_db_pool.acquire() as conn:
        yield conn

async def get_webhook_connection():
    if webhook_db_pool is None:
        raise Exception("Webhook DB pool not initialized.")
    async with webhook_db_pool.acquire() as conn:
        yield conn


# Uso:
# async with connection_context(get_webhook_connection) as conn:
#     async with conn.cursor() as cur:
#         await cur.execute(...)
@asynccontextmanager
async def connection_context(getter):
    async for conn in getter():
        yield conn
        break  # Rompe el loop tras la primera conexión
