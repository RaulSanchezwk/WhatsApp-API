# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import httpx
import os

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

@app.get("/")
def root():
    return {"message": "WhatsApp Bot with FastAPI is running."}

# Endpoint para que Meta verifique el webhook 
@app.get("/webhook")
def verify_webhook(mode: str, challenge: str, verify_token: str):
    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Unauthorized", status_code=403)

# Endpoint para recibir mensajes
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    # Extraer datos del mensaje
    print("Webhook recibido:", data)
    return JSONResponse({"status": "received"})

# Enviar mensajes
async def send_whatsapp_message(recipient_id: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
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
