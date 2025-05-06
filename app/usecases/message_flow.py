from app.domain.entities import Cliente
from app.infrastructure.database import verificar_si_es_cliente_nuevo
from app.infrastructure.whatsapp_client import send_whatsapp_text_message

async def manejar_mensaje(cliente: Cliente, mensaje: str, conn):
    if cliente.telefono == '5218135745910':
        respuesta = f"Hola {cliente.nombre}, bienvenido"
        await send_whatsapp_text_message(cliente.telefono, respuesta)

    # es_nuevo = await verificar_si_es_cliente_nuevo(conn, cliente.telefono)

    # if es_nuevo:
    #     pass
    #     respuesta = f"Hola {cliente.nombre}, bienvenido 👋"
    # else:
    #     pass
    #     respuesta = f"¡Qué gusto tenerte de vuelta, {cliente.nombre}!"

