from datetime import datetime
import json
from .connection import get_webhook_connection, connection_context
import json
import logging
from aiomysql import Error as sql_error

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
                    INSERT INTO webhook_notification (
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
        logger.exception("❌ Error al guardar webhook_notification")
        print(f"{e}")
        # se retorna -1 en caso de error para poder manejar el error después en el código
        return -1

async def save_contact(wa_id: str, telefono: str, nombre: str, estado: int) -> int:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO contact (wa_id, display_phone_number, contact_name, estado)
                    VALUES (%s, %s, %s, %s)
                """, (wa_id, telefono, nombre, estado))

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
        logger.exception("❌ Error al guardar contacto")
        print(f"{e}")

async def save_intention(wa_id: int) -> int:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO intencion_agenda(id_contact)
                VALUES (
                    (SELECT id_contact FROM contact WHERE wa_id = %s)
                );
                """, (wa_id,))

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
        logger.exception("❌ Error al guardar intención")
        print(f"{e}")