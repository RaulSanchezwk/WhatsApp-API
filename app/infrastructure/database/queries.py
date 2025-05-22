from .connection import get_citas_connection, get_webhook_connection, connection_context
from datetime import datetime, time
from app.core import constants
from app.domain.entities import Contact
import logging

logger = logging.getLogger(__name__)

async def get_contact_by_wa_id(wa_id: str) -> Contact | None:

    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT id, wa_id, display_phone_number, contact_name, step
                    FROM contacts
                    WHERE wa_id = %s;
                """, (wa_id,))

                result = await cur.fetchone()

                await cur.close()

                if result:
                    contact = Contact(
                        id=result[0],
                        wa_id=result[1],
                        phone_number=result[2],
                        name=result[3],
                        step=result[4]
                    )
                    return contact
                else:
                    return None
                
    except Exception as e:
        logger.exception("❌ Error consultando si ya existe el contacto")
        print(e)
        return None

async def get_step(wa_id: str) -> str:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT step
                    FROM contact
                    WHERE wa_id = %s;
                """, (wa_id,))

                result = await cur.fetchone()

                await cur.close()

                return result[0] if result else None
            
    except Exception as e:
        logger.exception("❌ Error consultando el estado")
        print(e)
        return -1

async def get_available_dates(start_date, end_date, doctor: int) -> list:
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
                                     (start_date, end_date, doctor))
                result = await cur.fetchall()

                await cur.close()

                print(f"\n\n{result}\n\n")

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
    
async def get_available_ranges(doctor: int, date: str) -> list:

    try:
        async with connection_context(get_citas_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    WITH rangos AS (
                        SELECT '9:00 am - 12:00 pm' AS rango, 9 AS inicio, 11 AS fin
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
                """, (date, doctor))

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

async def get_occupied_hours(doctor: int, date: datetime, start_hour: time, end_hour: time) -> list:

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
                """, (doctor, date, start_hour, end_hour))

                result = await cur.fetchall()

                await cur.close()

                return [row[0] for row in result]
            
    except Exception as e:
        logger.exception("❌ Error consultando los horarios disponibles")
        print(e)
        return []
    
async def get_appt_intention(field: str, wa_id: str):
    try:
        if field not in constants.ALOUD_FIELDS:
            raise ValueError("Campo no permitido")

        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"""
                    SELECT i.{field}
                    FROM appointment_intentions i
                    INNER JOIN contacts c ON i.contact = c.id
                    WHERE c.wa_id = %s;
                """, (wa_id, ))
                
                result = await cur.fetchone()

                await cur.close()

                return result[0] if result else None

    except Exception as e:
        logger.exception(f"❌ Error consultando de appointment_intentions ({field})")
        print(e)
        return -1
