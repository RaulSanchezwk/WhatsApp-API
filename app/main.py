from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
import httpx

from app.config import settings

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bot activo", "debug": settings.DEBUG}

@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
    ):
    if hub_mode == "subscribe" and hub_token == settings.VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "Invalid verification token"}, 403

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


@app.api_route("/enviar_mensaje", methods=["GET", "POST"])
async def enviar_mensaje_endpoint(request: Request):
    recipient = "528135745910"
    message = "Hola, estoy probando el endpoint de FastAPI"
    await send_whatsapp_message(recipient, message)
    return {"status": "mensaje enviado desde FastAPI"}