from .connection import get_citas_connection, get_webhook_connection, connection_context
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

async def change_step(wa_id: str, step: str) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE contacts
                    SET step = %s
                    WHERE wa_id = %s
                """, (step, wa_id))

                await conn.commit()
                await cur.close()
            
    except Exception as e:
        logger.exception("❌ Error actualizando step en contacts")
        print(e)
    
async def update_webhook_contact(contact: int, webhook_DB_id: int) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE webhook_notifications
                    SET contact = %s
                    WHERE id = %s
                """, (contact, webhook_DB_id))

                await conn.commit()
                await cur.close()
            
    except Exception as e:
        logger.exception("❌ Error actualizando contact en webhook_notifications")
        print(e)

async def update_chosen_branch(branch: int, wa_id: str) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_branch = %s
                    WHERE contact = (
                        SELECT id
                        FROM contacts
                        WHERE wa_id = %s
                    );
                """, (branch, wa_id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error actualizando chosen_branch")
        print(e)

async def update_chosen_date(date: datetime, wa_id: str) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_date = %s
                    WHERE contact = (
                        SELECT id
                        FROM contacts
                        WHERE wa_id = %s
                    );
                """, (date, wa_id))

                await conn.commit()
                await cur.close()
    
    except Exception as e:
        logger.exception("❌ Error actualizando chosen_date")
        print(e)

async def update_chosen_hours_range(hours_range: str, wa_id: str) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_hours_range = %s
                    WHERE contact = (
                        SELECT id
                        FROM contacts
                        WHERE wa_id = %s
                    );
                """, (hours_range, wa_id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error actualizando chosen_hours_range")
        print(e)

async def update_chosen_hour(horario: time, wa_id: str) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_hour = %s
                    WHERE contact = (
                        SELECT id
                        FROM contacts
                        WHERE wa_id = %s
                    );
                """, (horario, wa_id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error actualizando chosen_hour")
        print(e)
