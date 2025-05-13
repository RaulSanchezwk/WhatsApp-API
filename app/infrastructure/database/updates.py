from .connection import get_citas_connection, get_webhook_connection, connection_context
import logging

logger = logging.getLogger(__name__)

async def cambiar_estado(id_contact: int, estado: int) -> bool:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE contact
                    SET estado = %s
                    WHERE id_contact = %s
                """, (estado, id_contact))

                await conn.commit()
                await cur.close()

                return True
            
    except Exception as e:
        logger.exception("❌ Error actualizando el estado del webhook")
        print(f"{e}")
        return False
    

async def relacionar_contacto(id_contact: str, webhook_DB_id: int) -> bool:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE webhook_notification
                    SET id_contact = %s
                    WHERE id_notification = %s
                """, (id_contact, webhook_DB_id))

                await conn.commit()
                await cur.close()

                return True
            
    except Exception as e:
        logger.exception("❌ Error actualizando el estado del webhook")
        print(f"{e}")
        return False