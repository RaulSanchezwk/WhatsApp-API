from app.domain.entities import Cliente
from app.infrastructure.database import verificar_si_es_cliente_nuevo
from app.infrastructure.whatsapp_client import send_whatsapp_text_message

async def manejar_mensaje(cliente: Cliente, mensaje: str, conn):
    numeros_permitidos = ['5218135745910', '5218123302217', '5218144883499', '5218116965030', '5218129133326', '5218119043177', '5218182803998', '5218110444217', '5218131240968', '5218182808236']
    if cliente.telefono in numeros_permitidos:
        respuesta = f"Hola {cliente.nombre}, bienvenido"
        await send_whatsapp_text_message(cliente.telefono, respuesta)

    # es_nuevo = await verificar_si_es_cliente_nuevo(conn, cliente.telefono)

    # if es_nuevo:
    #     pass
    #     respuesta = f"Hola {cliente.nombre}, bienvenido 👋"
    # else:
    #     pass
    #     respuesta = f"¡Qué gusto tenerte de vuelta, {cliente.nombre}!"

