from app.domain.entities import Cliente
from app.infrastructure.whatsapp_client import send_whatsapp_text_message
from app.infrastructure.database.consult import ya_existe_contacto

async def manejar_mensaje(value, conn):

    try:
        wa_id = value.contacts[0].wa_id
        phone_number_id = value.metadata.phone_number_id
    except (IndexError, AttributeError):
        print("⚠️ No se pudo extraer wa_id o phone_number_id")
        return


    ya_existe = await ya_existe_contacto(conn, wa_id, phone_number_id)

    if not ya_existe:
        print(f"📩 Nuevo contacto: {wa_id}")
        await manejar_mensaje_nuevo(conn, wa_id, phone_number_id, value)
    else:
        print(f"📨 Contacto ya conocido: {wa_id}")
        await manejar_mensaje_existente(conn, wa_id, phone_number_id, value)
            

    # es_nuevo = await verificar_si_es_cliente_nuevo(conn, cliente.telefono)

    # if es_nuevo:
    #     pass
    #     respuesta = f"Hola {cliente.nombre}, bienvenido 👋"
    # else:
    #     pass
    #     respuesta = f"¡Qué gusto tenerte de vuelta, {cliente.nombre}!"

async def manejar_mensaje_nuevo(conn, wa_id, phone_number_id, value):
    numeros_permitidos = ['5218135745910', '5218123302217', '5218144883499', '5218116965030', '5218129133326', '5218119043177', '5218182803998', '5218110444217', '5218131240968', '5218182808236']

    if wa_id in numeros_permitidos:
        respuesta = f"Hola, bienvenido"
        await send_whatsapp_text_message(wa_id, respuesta)


def manejar_mensaje_existente():
    pass