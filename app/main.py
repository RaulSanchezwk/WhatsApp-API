from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import httpx

from app.config import settings

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bot activo", "debug": settings.DEBUG}

@app.get("/webhook")
def verify_webhook(mode: str, challenge: str, verify_token: str):
    print("Meta intentó verificar:", mode, challenge, verify_token)
    print("Token esperado:", settings.VERIFY_TOKEN)
    if mode == "subscribe" and verify_token == settings.VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    return PlainTextResponse(content="Unauthorized", status_code=403)

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("Webhook recibido:", data)
    return JSONResponse({"status": "received"})

async def send_whatsapp_message(recipient_id: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{settings.PHONE_NUMBER_ID}/messages"
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
