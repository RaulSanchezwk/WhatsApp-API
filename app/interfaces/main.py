# Desde main.py se reciben las peticiones HTTP y se gestionan los webhooks de WhatsApp.
# Se utiliza FastAPI para crear la API y manejar las rutas.

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.infrastructure.database.connection import init_db_pools
from app.infrastructure.database.insertions import save_webhook_notification
from app.core.config import settings
from app.usecases.message_flow.message_router import MessageRouter
from app.core.logging_config import setup_logger
from app.usecases.webhook_processor import WebhookProcessor, FlattenedData
import tracemalloc

# Se inicializa el rastreo de memoria para ayudar a identificar problemas de memoria.
# Esto es útil para el desarrollo y la depuración, pero puede ser costoso en términos de rendimiento.
# Por lo tanto, se debe usar solo en entornos de desarrollo.
if settings.DEBUG:
    tracemalloc.start() 

# lifespan es un contexto asincrónico que se utiliza para inicializar recursos al inicio de la aplicación y liberarlos al finalizar.
# En este caso, se utiliza para configurar el logger y las conexiones a la base de datos.
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    await init_db_pools()
    yield

app = FastAPI(lifespan=lifespan)

# Se define la ruta raíz de la API, que devuelve un mensaje simple indicando que el bot está activo.
# Indica también si la aplicación está en modo de desarrollo (DEBUG).
@app.get("/")
def root():
    return {"message": "Bot activo", "debug": settings.DEBUG}

# Se define la ruta "/webhook" para la verificación del webhook de WhatsApp.
# WhatsApp envía una solicitud GET a esta ruta para verificar que el webhook está activo y configurado correctamente.
# Se espera que la solicitud contenga los parámetros "hub.mode", "hub.verify_token" y "hub.challenge".
# Si el modo es "subscribe" y el token de verificación coincide con el token configurado, se devuelve el desafío (challenge).
# Si no coincide, se devuelve un error 403.
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
    ):
    if hub_mode == "subscribe" and hub_token == settings.VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "Invalid verification token"}, 403

# Se usa también la ruta "/webhook" para recibir las notificaciones de los mensajes de WhatsApp.
# WhatsApp envía una solicitud POST a esta ruta cada vez que hay un nuevo mensaje o evento.
# La función recibe el cuerpo de la solicitud y lo procesa.
# El cuerpo de la solicitud es un JSON que contiene información sobre el mensaje o evento.
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()

    value = data["entry"][0]["changes"][0]["value"]
    
    print(f"\nWebhook recibido: {data}\n")
    
    message = value.get("messages") != None
    status = value.get("statuses") != None
    
    # Guardar la notificación del webhook en la base de datos
    # y obtener el ID de la fila insertada.
    if message:
        numeros_permitidos = ['5218135745910', '5218123302217', '5218144883499', '5218116965030', '5218129133326', '5218119043177', '5218182803998', '5218110444217', '5218131240968', '5218182808236']
        wa_id = value["contacts"][0]["wa_id"]
        if wa_id in numeros_permitidos:
            last_row_id = await save_webhook_notification(
                data=data,
                ip=request.client.host,
                user_agent=request.headers.get("user-agent")
            )

            # Se extraen el ID de WhatsApp y el ID del número de teléfono del mensaje.
            # Estos IDs son necesarios para enviar mensajes de respuesta a través de la API de WhatsApp.
            await MessageRouter(data, last_row_id)

    elif status:
        await manejar_status(value)

    else:
        print(f"⚠️ Tipo de webhook no reconocido: {value}")

    return JSONResponse(content={"status": "ok"}, status_code=200)


async def manejar_status(value: dict):
    pass