from .connection import get_citas_connection, get_webhook_connection, connection_context
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

async def cambiar_estado(id_contact: int, estado: int) -> None:
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
            
    except Exception as e:
        logger.exception("❌ Error actualizando el estado del webhook")
        print(e)
    
async def relacionar_contacto(id_contact: str, webhook_DB_id: int) -> None:
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
            
    except Exception as e:
        logger.exception("❌ Error actualizando el estado del webhook")
        print(e)

async def agregar_fecha_deseada(fecha: datetime, wa_id: int) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE intencion_agenda
                    SET fecha_deseada = %s
                    WHERE id_intencion = (
                        SELECT i.id_intencion
                        FROM intencion_agenda i
                        INNER JOIN contact c ON i.id_contact = c.id_contact
                        WHERE c.wa_id = %s
                    );
                """, (fecha, wa_id))

                await conn.commit()
                await cur.close()
    
    except Exception as e:
        logger.exception("❌ Error agregando fecha deseada")
        print(e)

async def agregar_rango_horarios(rango_horarios: str, wa_id: int) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE intencion_agenda
                    SET rango = %s
                    WHERE id_contact = (
                        SELECT id_contact
                        FROM contact
                        WHERE wa_id = %s
                    )
                """, (rango_horarios, wa_id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error agregando rango de horarios")
        print(e)