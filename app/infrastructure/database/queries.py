from .connection import get_citas_connection, get_webhook_connection, connection_context
from datetime import datetime, time
from app.core import constants
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

                return result[0] if result else None
            
    except Exception as e:
        logger.exception("❌ Error consultando el estado")
        print(e)
        return -1

async def fechas_con_disponibilidad(fecha_inicio, fecha_fin, doctor: int) -> list:
    try:
        async with connection_context(get_citas_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""SELECT fecha, COUNT(DISTINCT hora) AS total_citas
                                     FROM dmty_citas
                                     WHERE (fecha BETWEEN %s AND %s)
                                     AND doctor = %s
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
                                     (fecha_inicio, fecha_fin, doctor))
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
    
async def rangos_con_disponibilidad(fecha: str, doctor: int) -> list:

    try:
        async with connection_context(get_citas_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    WITH rangos AS (
                        SELECT '9:00 am -12:00 pm' AS rango, 9 AS inicio, 11 AS fin
                        UNION ALL
                        SELECT '12:00 pm - 3:00 pm', 12, 14
                        UNION ALL
                        SELECT '3:00 pm - 6:00 pm', 15, 17
                    ),
                    citas_filtradas AS (
                        SELECT
                            HOUR(hora) AS hora_h,
                            hora
                        FROM dmty_citas
                        WHERE fecha = %s
                            AND hora BETWEEN '9:00:00' AND '18:00:00'
                            AND doctor = %s
                            AND hora NOT IN (
                                '09:45:00', '10:45:00', '11:45:00',
                                '12:45:00', '13:45:00', '14:45:00',
                                '15:45:00', '16:45:00', '17:45:00'
                            )
                        )
                        SELECT
                            r.rango,
                            COUNT(DISTINCT c.hora) AS citas
                        FROM rangos r
                        LEFT JOIN citas_filtradas c
                            ON c.hora_h BETWEEN r.inicio AND r.fin
                        GROUP BY r.rango
                        HAVING COUNT(DISTINCT c.hora) < 9
                        ORDER BY r.inicio;
                """, (fecha, doctor))

                result = await cur.fetchall()

                await cur.close()

                return [
                    {
                        "rango": row[0],
                        "citas": row[1]
                    }
                    for row in result
                ]
            
    except Exception as e:
        logger.exception("❌ Error consultando los rangos")
        print(e)
        return []

async def horarios_ocupados(doctor: int, fecha: datetime, hora_inicio: time, hora_fin: time) -> list:

    try:
        async with connection_context(get_citas_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT hora
                    FROM dmty_citas
                    WHERE doctor = %s
                    AND fecha = %s
                    AND hora BETWEEN %s AND %s
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
                    ORDER BY hora;
                """, (doctor, fecha, hora_inicio, hora_fin))

                result = await cur.fetchall()

                await cur.close()

                return [row[0] for row in result]
            
    except Exception as e:
        logger.exception("❌ Error consultando los horarios disponibles")
        print(e)
        return []
    
async def obtener_de_intencion(campo: str, wa_id: str):
    try:
        if campo not in constants.CAMPOS_PERMITIDOS:
            raise ValueError("Campo no permitido")

        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"""
                    SELECT i.{campo}
                    FROM intencion_agenda i
                    INNER JOIN contact c ON i.id_contact = c.id_contact
                    WHERE c.wa_id = %s;
                """, (wa_id, ))
                
                result = await cur.fetchone()

                await cur.close()

                return result[0] if result else None

    except Exception as e:
        logger.exception(f"❌ Error consultando de intencion_agenda ({campo})")
        print(e)
        return -1
