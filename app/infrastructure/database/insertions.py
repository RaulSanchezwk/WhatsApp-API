from datetime import datetime
import json
from .connection import get_webhook_connection, connection_context
import json
import logging

logger = logging.getLogger(__name__)

async def save_webhook_notification(data: dict, ip: str, user_agent: str):
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
                logger.info("✅ Datos insertados correctamente")
                
    except Exception as e:
        logger.exception("❌ Error al guardar webhook_notification")
