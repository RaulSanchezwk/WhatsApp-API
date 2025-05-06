from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from app.infrastructure.database import init_db_pool, get_db_connection
from contextlib import asynccontextmanager
from app.config import settings
from app.schemas import WebhookPayload
from app.domain.entities import Cliente
from app.usecases.message_flow import manejar_mensaje
from app.infrastructure.database import get_db_connection
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    yield

app = FastAPI(lifespan=lifespan)


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

    print("Webhook recibido:\n", json.dumps(data, indent=2))

    try:
        payload = WebhookPayload(**data)
    except Exception as e:
        print("❌ Error al parsear a WebhookPayload:", str(e))
        return JSONResponse(status_code=400, content={"error": "Formato inválido", "detalle": str(e)})

    value = payload.entry[0].changes[0].value

    if not value.messages or not value.contacts:
        return {"status": "sin mensajes o sin contacto"}

    mensaje = value.messages[0].text.body if value.messages[0].text else ""
    numero = value.messages[0].from_
    nombre = value.contacts[0].profile.name

    cliente = Cliente(nombre=nombre, telefono=numero)
    conn_gen = get_db_connection()
    conn = await anext(conn_gen)

    try:
        await manejar_mensaje(cliente, mensaje, conn)
    finally:
        await conn.ensure_closed()

    return {"status": "ok"}


# try:
    #     citas = await obtener_citas_desde_conn(conn)
    #     if citas:
    #         mensaje = "Fechas disponibles:\n" + "\n".join([str(c[0]) for c in citas])
    #     else:
    #         mensaje = "No hay fechas disponibles por ahora."

    #     await send_whatsapp_message("528135745910", mensaje)

    # finally:
    #     await conn.ensure_closed()  # o conn.close()