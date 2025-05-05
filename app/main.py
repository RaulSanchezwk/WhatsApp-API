from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from app.infrastructure.database import init_db_pool, get_db_connection
from contextlib import asynccontextmanager
from app.config import settings

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
    print('Webhook recibido:', data)

    conn_gen = get_db_connection()
    conn = await anext(conn_gen)

    await conn.ensure_closed()

    return JSONResponse({"status": "received"})

# try:
    #     citas = await obtener_citas_desde_conn(conn)
    #     if citas:
    #         mensaje = "Fechas disponibles:\n" + "\n".join([str(c[0]) for c in citas])
    #     else:
    #         mensaje = "No hay fechas disponibles por ahora."

    #     await send_whatsapp_message("528135745910", mensaje)

    # finally:
    #     await conn.ensure_closed()  # o conn.close()