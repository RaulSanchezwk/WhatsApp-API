from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.infrastructure.database.connection import init_db_pools
from app.infrastructure.database.insertions import save_webhook_notification
from app.config import settings
from app.usecases.message_flow.message_router import manejar_mensaje
from app.schemas import WebhookPayload
from app.logging_config import setup_logger
import json
import tracemalloc

tracemalloc.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    await init_db_pools()
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

    print("Webhook recibido:\n", json.dumps(data, indent=1))

    await save_webhook_notification(
        data=data,
        ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    try:
        payload = WebhookPayload(**data)
    except Exception as e:
        print("❌ Error al parsear a WebhookPayload:", str(e))
        JSONResponse(status_code=200, content={"status": "ok"})

    await manejar_payload(payload)

    return JSONResponse(status_code=200, content={"status": "ok"})


async def manejar_payload(payload):
    for entry in payload.entry:
        for change in entry.changes:
            mensaje = change.value.statuses == None

            # Verificamos si es tipo mensaje
            if mensaje:
                await manejar_mensaje(change.value)

            elif not mensaje:
                print("🔁 Webhook de tipo status recibido")
                await manejar_status(change.value) 

            else:
                print(f"⚠️ Tipo de webhook no reconocido: {mensaje}")


async def manejar_status(value):
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