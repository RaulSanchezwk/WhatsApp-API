from datetime import datetime
import json

async def save_whatsapp_webhook(pool, data: dict):
    try:
        value = data["entry"][0]["changes"][0]["value"]
        message = value.get("messages", [])[0]
        contact = value.get("contacts", [])[0]

        wa_id = contact["wa_id"]
        user_name = contact["profile"].get("name", "")
        message_id = message["id"]
        message_type = message["type"]
        message_body = message.get("text", {}).get("body", "")
        timestamp = datetime.fromtimestamp(int(message["timestamp"]))
        raw_payload = json.dumps(data)

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO whatsapp_webhooks (
                        wa_id, user_name, message_id, message_type, message_body, timestamp, raw_payload
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    wa_id, user_name, message_id, message_type, message_body, timestamp, raw_payload
                ))
    except Exception as e:
        print("❌ Error guardando webhook:", e)