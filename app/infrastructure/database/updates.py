from .connection import get_citas_connection, get_webhook_connection, connection_context
import logging

logger = logging.getLogger(__name__)

async def cambiar_estado(wa_id: str, status: int, webhook_DB_id: int) -> bool:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE webhook_notification
                    SET estado = %s
                    WHERE wa_id = %s AND id = %s
                """, (status, wa_id, webhook_DB_id))
                await conn.commit()
                await cur.close()
                return True
    except Exception as e:
        logger.exception("❌ Error actualizando el estado del webhook")
        return False