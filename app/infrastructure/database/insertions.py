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
                    return cur.lastrowid
                else:
                    logger.error("❌ cur.lastrowid is None, returning -1")
                    return -1

    except (Exception, sql_error) as e:
        logger.exception("❌ Error al guardar webhook_notification")
        # se retorna -1 en caso de error para poder manejar el error después en el código
        return -1
