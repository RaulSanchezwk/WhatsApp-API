import httpx
from app.core.config import settings

async def send_whatsapp_text_message(recipient_id: str, message: str):
    url = f"https://graph.facebook.com/v22.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print("Respuesta de WhatsApp:", response.status_code, response.json())
        return response.json()