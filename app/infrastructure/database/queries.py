from .connection import get_webhook_connection, connection_context
import logging

logger = logging.getLogger(__name__)

async def ya_existe_contacto(wa_id: str, phone_number_id: str) -> bool:

    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM ch_value v
                        JOIN contact c ON v.id_contact = c.id_contact
                        JOIN metadata m ON v.id_metadata = m.id_metadata
                        WHERE c.wa_id = %s AND m.phone_number_id = %s
                    )
                """, (wa_id, phone_number_id))
                result = await cur.fetchone()
                return bool(result[0])
    except Exception as e:
        logger.exception("❌ Error consultando si ya existe el contacto")
        return False


# async def obtener_citas_disponibles(conn):
#     hoy = datetime.today().date()
#     dias_a_generar = 5
#     fecha_inicial = hoy

#     rango_fechas = [fecha_inicial + timedelta(days=i) for i in range(dias_a_generar + 1)]

#     print(rango_fechas)
#     placeholders = ', '.join(['%s'] * len(rango_fechas))

#     #SELECT * FROM dmty_citas WHERE fecha = CURDATE()

#     async with conn.cursor() as cur:
#         query = f"SELECT DISTINCT fecha FROM dmty_citas WHERE fecha IN ({placeholders}) ORDER BY fecha;"
#         await cur.execute(query, rango_fechas)
#         result = await cur.fetchall()

#     return result