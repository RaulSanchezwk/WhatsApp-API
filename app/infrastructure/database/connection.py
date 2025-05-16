import aiomysql
from app.core.config import settings
from contextlib import asynccontextmanager

citas_db_pool = None
webhook_db_pool = None

# Se utiliza aiomysql para crear un pool de conexiones a la base de datos MySQL.
# El pool de conexiones permite manejar múltiples conexiones a la base de datos 
# de manera eficiente, reutilizando conexiones existentes en lugar de crear nuevas cada vez.
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
        charset='utf8mb4',
    )

    webhook_db_pool = await aiomysql.create_pool(
        host=settings.WEBHOOK_DB_HOST,
        port=int(settings.WEBHOOK_DB_PORT),
        user=settings.WEBHOOK_DB_USER,
        password=settings.WEBHOOK_DB_PASSWORD,
        db=settings.WEBHOOK_DB_NAME,
        minsize=1,
        maxsize=5,
        charset='utf8mb4',
    )

# Se definen dos funciones asincrónicas que permiten obtener conexiones a las bases de datos de citas y
# webhook. Estas funciones utilizan el pool de conexiones creado anteriormente para adquirir una conexión
# y devolverla al final del bloque de código.
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

# Se define un contexto asincrónico que permite manejar la conexión a la base de datos de manera más sencilla.
# Este contexto se utiliza para adquirir una conexión a la base de datos y liberarla automáticamente
# al finalizar el bloque de código. Esto es útil para evitar tener que cerrar la conexión manualmente
# y para asegurarse de que la conexión se libere incluso si ocurre un error.
# Uso:
# async with connection_context(get_webhook_connection) as conn:
#     async with conn.cursor() as cur:
#         await cur.execute(...)
@asynccontextmanager
async def connection_context(getter):
    conn = None
    try:
        async for c in getter():
            conn = c
            yield conn
            break  # Rompe el loop tras la primera conexión
    finally:
        if conn:
            conn.close()  # Cierra correctamente la conexión
            await conn.ensure_closed()
