from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from app.infrastructure.database.connection import init_db_pool, get_db_connection
from contextlib import asynccontextmanager
from app.config import settings
from app.schemas import WebhookPayload
from app.domain.entities import Cliente
from app.usecases.message_flow.message_router import manejar_mensaje
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

    # value = payload.entry[0].changes[0].value

    # if not value.messages or not value.contacts:
    #     return {"status": "sin mensajes o sin contacto"}

    # mensaje = value.messages[0].text.body if value.messages[0].text else ""
    # numero = value.messages[0].from_
    # nombre = value.contacts[0].profile.name

    # cliente = Cliente(nombre=nombre, telefono=numero)

    conn_gen = get_db_connection()
    conn = await anext(conn_gen)

    try:
        await manejar_payload(payload, conn)
    finally:
        await conn.ensure_closed()

    return {"status": "ok"}


async def manejar_payload(payload: WebhookPayload, conn):
    for entry in payload.entry:
        for change in entry.changes:
            tipo = change.field

            # Verificamos si es tipo mensaje
            if tipo == "messages":
                manejar_mensaje(change.value, conn)

            elif tipo == "statuses":
                print("🔁 Webhook de tipo status recibido")
                await manejar_status(conn, change.value)

            else:
                print(f"⚠️ Tipo de webhook no reconocido: {tipo}")


def manejar_status():
    pass

### Tipos de Webhooks



## Mensaje Recibido
 
# {
#   "object": "whatsapp_business_account",
#   "entry": [
#     {
#       "id": "1224129935909135",
#       "changes": [
#         {
#           "value": {
#             "messaging_product": "whatsapp",
#             "metadata": {
#               "display_phone_number": "5218134462645",
#               "phone_number_id": "589111897626816"
#             },
#             "contacts": [
#               {
#                 "profile": {
#                   "name": "Ra\u00fal"
#                 },
#                 "wa_id": "5218135745910"
#               }
#             ],
#             "messages": [
#               {
#                 "from": "5218135745910",
#                 "id": "wamid.HBgNNTIxODEzNTc0NTkxMBUCABIYFDNBNTgxMzI3MkYyRTlGOTgzNDNEAA==",
#                 "timestamp": "1746550314",
#                 "text": {
#                   "body": "Hola"
#                 },
#                 "type": "text"
#               }
#             ]
#           },
#           "field": "messages"
#         }
#       ]
#     }
#   ]
# }

## Mensaje enviado