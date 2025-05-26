import json
from .connection import get_webhook_connection, connection_context
import json
import logging
from aiomysql import Error as sql_error
from app.infrastructure.database import queries
from app.domain.entities import Contact

logger = logging.getLogger(__name__)

# Esta función se encarga de guardar la notificación del webhook en la base de datos.
async def save_webhook_notification(data: dict, ip: str, user_agent: str) -> int:
    try:
        messaging_product = data["entry"][0]["changes"][0]["value"].get("messaging_product", "")
        object_type = data.get("object", "")
        business_account_id = data["entry"][0].get("id", "")
        change_field = data["entry"][0]["changes"][0].get("field", "")
        notification_json = json.dumps(data)


        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO webhook_notifications (
                        messaging_product,
                        object_type,
                        business_account_id,
                        change_field,
                        notification_json,
                        source_ip,
                        user_agent
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    messaging_product,
                    object_type,
                    business_account_id,
                    change_field,
                    notification_json,
                    ip,
                    user_agent
                ))
                await conn.commit()
                # Se retorna el ID de la última fila insertada.
                if cur.lastrowid is not None:
                    await cur.close()
                    return cur.lastrowid
                else:
                    logger.error("❌ cur.lastrowid is None, returning -1")
                    cur.close()
                    return -1
                
                

    except (Exception, sql_error) as e:
        logger.exception("❌ Error al insertar en webhook_notifications")
        print(f"{e}")
        # se retorna -1 en caso de error para poder manejar el error después en el código
        return -1

async def save_contact(wa_id: str, contact_name: str, step: str) -> int:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO contacts (wa_id, contact_name, step)
                    VALUES (%s, %s, %s)
                """, (wa_id, contact_name, step))

                await conn.commit()
                last_row_id = cur.lastrowid

                if last_row_id is not None:
                    await cur.close()
                    return last_row_id
                else:
                    logger.error("❌ cur.lastrowid is None, returning -1")
                    await cur.close()
                    return -1

    except (Exception, sql_error) as e:
        logger.exception("❌ Error al insertar en contacts")
        print(f"{e}")

async def save_appt_intention(contact: Contact) -> int:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO appointment_intentions(contact)
                VALUES (%s);
                """, (contact.id,))

                await conn.commit()
                last_row_id = cur.lastrowid

                if last_row_id is not None:
                    await cur.close()
                    return last_row_id
                else:
                    logger.error("❌ cur.lastrowid is None, returning -1")
                    await cur.close()
                    return -1

    except (Exception, sql_error) as e:
        logger.exception("❌ Error al insertar en appointment_intentions")
        print(f"{e}")

async def save_appt_intention_history(wa_id: str, webhook: int, field: str, new_value: str):
    try:
        old_value = await queries.get_appt_intention(field, wa_id)

        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO appointment_intentions_hist (
                    appt_intention,
                    webhook,
                    modified_field,
                    previous_value,
                    new_value         
                )
                VALUES (
                    (SELECT id
                    FROM appointment_intentions a
                    INNER JOIN contacts c ON a.contact = c.id
                    WHERE c.wa_id = %s),
                    %s, %s, %s, %s);
                """, (wa_id, webhook, field, old_value, new_value))

                await conn.commit()
                last_row_id = cur.lastrowid

                if last_row_id is not None:
                    await cur.close()
                    return last_row_id
                else:
                    logger.error("❌ cur.lastrowid is None, returning -1")
                    await cur.close()
                    return -1

    except (Exception, sql_error) as e:
        logger.exception("❌ Error al insertar en appointment_intention_hist")
        print(f"{e}")
