from .connection import get_citas_connection, get_webhook_connection, connection_context
import logging

logger = logging.getLogger(__name__)

async def ya_existe_contacto(wa_id: str) -> int:

    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT id_contact 
                    FROM contact 
                    WHERE wa_id = %s;
                """, (wa_id,))

                result = await cur.fetchone()

                await cur.close()

                return result[0] if result else None
    except Exception as e:
        logger.exception("❌ Error consultando si ya existe el contacto")
        print(e)
        return None

async def fechas_con_disponibilidad(fecha_inicio, fecha_fin) -> list:
    try:
        async with connection_context(get_citas_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""SELECT fecha, COUNT(DISTINCT hora) AS total_citas
                                     FROM dmty_citas
                                     WHERE (fecha BETWEEN %s AND %s)
                                     AND (hora BETWEEN '9:00:00' AND '18:00:00')
                                     AND hora NOT IN (
                                     '09:45:00',
                                     '10:45:00',
                                     '11:45:00',
                                     '12:45:00',
                                     '13:45:00',
                                     '14:45:00',
                                     '15:45:00',
                                     '16:45:00',
                                     '17:45:00'
                                     )
                                     GROUP BY fecha
                                     HAVING total_citas < 28
                                     ORDER BY fecha;""",
                                     (fecha_inicio, fecha_fin))
                result = await cur.fetchall()

                await cur.close()

                return [
                    {
                        "fecha": row[0],
                        "total_citas": row[1]
                    }
                    for row in result
                ]
    except Exception as e:
        logger.exception("❌ Error consultando las fechas")
        print(e)
        return []

async def obtener_estado(id_contact: int) -> int:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT estado
                    FROM contact
                    WHERE id_contact = %s;
                """, (id_contact,))

                result = await cur.fetchone()

                await cur.close()

                print(f"Estado consultado: {result}")

                return result[0] if result else None
            
    except Exception as e:
        logger.exception("❌ Error consultando el estado")
        print(e)
        return -1