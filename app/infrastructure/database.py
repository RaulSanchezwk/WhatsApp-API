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

async def verificar_si_es_cliente_nuevo(conn, telefono):
    async with conn.cursor() as cur:
        query = f"SELECT * FROM messages WHERE wa_id = %s"
        await cur.execute(query, telefono)
        result = await cur.fetchall()
    
    if len(result) > 0:
        return True
    else:
        return False

async def obtener_citas_disponibles(conn):
    hoy = datetime.today().date()
    dias_a_generar = 5
    fecha_inicial = hoy

    rango_fechas = [fecha_inicial + timedelta(days=i) for i in range(dias_a_generar + 1)]

    print(rango_fechas)
    placeholders = ', '.join(['%s'] * len(rango_fechas))

    async with conn.cursor() as cur:
        query = f"SELECT DISTINCT fecha FROM dmty_citas WHERE fecha IN ({placeholders}) ORDER BY fecha;"
        await cur.execute(query, rango_fechas)
        result = await cur.fetchall()

    return result