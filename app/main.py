from fastapi import FastAPI, Request, Query, Depends
from fastapi.responses import JSONResponse
import httpx
from app.database import init_db_pool, get_db_connection
from datetime import datetime, timedelta

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
    obtener_citas(data)
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


# @app.api_route("/enviar_mensaje", methods=["GET", "POST"])
# async def enviar_mensaje_endpoint(request: Request, recipient: str, message: str):
#     # recipient = "528135745910"
#     # message = "Hola, estoy probando el endpoint de FastAPI"
#     await send_whatsapp_message(recipient, message)
#     return {"status": f"mensaje enviado a '{recipient}' desde FastAPI"}

@app.on_event("startup")
async def startup_event():
    await init_db_pool()

@app.get("/obtener-citas")
async def obtener_citas(conn = Depends(get_db_connection)):
    hoy = datetime.today().date()
    dia_semana = datetime.today().date().weekday()
    dias_a_generar = 10
    fecha_inicial = hoy

    rango_fechas = [fecha_inicial + timedelta(days=i) for i in range(dias_a_generar+1)]
    fecha_final=rango_fechas[-1:]

    rango_fechas_x_dia = []

    for i in rango_fechas:
        if i.weekday() == hoy.weekday():
            rango_fechas_x_dia.append(i)

    placeholders = ', '.join(['%s'] * len(rango_fechas_x_dia))

    # x = ", ".join([i.strftime("%Y-%m-%d") for i in rango_fechas_x_dia])
    
    async with conn.cursor() as cur:
        query = f"SELECT fecha FROM dmty_citas WHERE fecha IN ({placeholders}) ORDER BY fecha;"
        await cur.execute(query, rango_fechas_x_dia)
        result = await cur.fetchall()

    return result