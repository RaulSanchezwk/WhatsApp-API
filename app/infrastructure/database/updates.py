from .connection import get_citas_connection, get_webhook_connection, connection_context
from datetime import datetime, time
import logging
from app.domain.entities import Contact, Branch

logger = logging.getLogger(__name__)

async def update_phone_number(contact: Contact):
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE contacts
                    SET display_phone_number = %s
                    WHERE id = %s
                """, (contact.phone_number, contact.id))

                await conn.commit()
                await cur.close()
            
    except Exception as e:
        logger.exception("❌ Error actualizando phone_number en contacts")
        print(e)

async def change_step(contact: Contact) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE contacts
                    SET step = %s
                    WHERE id = %s
                """, (contact.step, contact.id))
                
                await conn.commit()
                await cur.close()
            
    except Exception as e:
        logger.exception("❌ Error actualizando step en contacts")
        print(e)
    
async def update_webhook_contact(contact: Contact, webhook_DB_id: int) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE webhook_notifications
                    SET contact = %s
                    WHERE id = %s
                """, (contact.id, webhook_DB_id))

                await conn.commit()
                await cur.close()
            
    except Exception as e:
        logger.exception("❌ Error actualizando contact en webhook_notifications")
        print(e)

async def update_chosen_branch(branch: Branch, contact: Contact) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_branch = %s
                    WHERE contact = %s;
                """, (branch.id, contact.id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error actualizando chosen_branch")
        print(e)

async def update_chosen_date(date: datetime, contact: Contact) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_date = %s
                    WHERE contact = %s;
                """, (date, contact.id))

                await conn.commit()
                await cur.close()
    
    except Exception as e:
        logger.exception("❌ Error actualizando chosen_date")
        print(e)

async def update_chosen_hours_range(hours_range: str, contact: Contact) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_hours_range = %s
                    WHERE contact = %s;
                """, (hours_range, contact.id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error actualizando chosen_hours_range")
        print(e)

async def update_chosen_hour(horario: time, contact: Contact) -> None:
    try:
        async with connection_context(get_webhook_connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE appointment_intentions
                    SET chosen_hour = %s
                    WHERE contact = %s;
                """, (horario, contact.id))

                await conn.commit()
                await cur.close()

    except Exception as e:
        logger.exception("❌ Error actualizando chosen_hour")
        print(e)
