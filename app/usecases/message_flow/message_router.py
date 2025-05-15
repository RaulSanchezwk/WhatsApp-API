from app.infrastructure.whatsapp_client import send_whatsapp_text_message
from app.infrastructure.database.queries import ya_existe_contacto, obtener_estado, fechas_con_disponibilidad, rangos_con_disponibilidad, horarios_ocupados, obtener_doctor, obtener_fecha
from app.infrastructure.database.updates import cambiar_estado, relacionar_contacto, agregar_fecha_deseada
from app.infrastructure.database.insertions import save_contact, save_intention
from datetime import datetime, timedelta
from babel.dates import format_datetime
from app.core import constants

async def manejar_mensaje(value: dict, webhook_DB_id: int) -> None:    
    # Aquí se define la función principal que maneja los mensajes entrantes de WhatsApp.
    # La función recibe el value del webhook 
    # y el ID del último webhook que se registró en la base de datos.

    wa_id = value["contacts"][0]["wa_id"]
    contact = await ya_existe_contacto(wa_id)
    
    if contact:

        await manejar_cliente_existente(value, contact)
        await relacionar_contacto(contact, webhook_DB_id)
        
    else:

        telefono = value["messages"][0]["from"]
        nombre = value["contacts"][0]["profile"]["name"]
        id_contact = await save_contact(wa_id, telefono, nombre, 1)

        await relacionar_contacto(id_contact, webhook_DB_id)

        mensaje_cliente = value["messages"][0]["text"]["body"]
        doctor = constants.SUCURSALES[mensaje_cliente]
        id_intention = await save_intention(wa_id, doctor)

        respuesta = await enviar_fechas(doctor, wa_id)
        await send_whatsapp_text_message(wa_id, respuesta)

async def manejar_cliente_existente(value, id_contact: int) -> None:
    
    wa_id = value["contacts"][0]["wa_id"]
    mensaje_cliente = value["messages"][0]["text"]["body"]

    estado = await obtener_estado(id_contact)

    match estado:
        case 1:
            respuesta = await enviar_rango_horarios(mensaje_cliente, wa_id)
            await cambiar_estado(id_contact, 2)

        case 2:
            respuesta = await enviar_horarios(mensaje_cliente, wa_id)
            await cambiar_estado(id_contact, 3)

        case 3:
            respuesta = "case 3"

        case None:
            respuesta = "No se encontró el estado"

        case -1:
            respuesta = "Ocurrió una excepción al consultar el estado"

        case 0:
            respuesta = f"Paso 0, esto no debería de mostrarse"

        case _:
            respuesta = "Caso no contemplado."
        
    await send_whatsapp_text_message(wa_id, respuesta)

    #await send_whatsapp_text_message(wa_id, f"Yo te conozco... ¿verdad {profile_name}?")

async def formatear_fechas_disponibles(doctor: int) -> list:
    
    fecha_inicial = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1) # Se establece la fecha inicial 
                                                                                                # como mañana a las 00:00
    
    fecha_final = fecha_inicial + timedelta(days=constants.DIAS_A_GENERAR) # Se establece la fecha final como la 
                                                                 # fecha inicial + el número de días a generar

    
    try:
        fechas_con_espacios = await fechas_con_disponibilidad(fecha_inicial, fecha_final, doctor)
        
    except Exception as e:
        print(f"Error al obtener fechas: {e}")
        fechas_con_espacios = []
    
    finally:
        return fechas_con_espacios

async def formatear_rango_horarios(fecha: str, doctor: int) -> list:
    try:
        rangos_con_espacios = await rangos_con_disponibilidad(fecha, doctor)

    except Exception as e:
        print(f"Error al formatear el rango de horarios: {e}")        
        rangos_con_espacios = []

    finally:
        return rangos_con_espacios

async def formatear_horarios_disponibles(rango_horarios: int, doctor: int, fecha: datetime) -> list:
    try: 
        parametros_horarios = obtener_parametros_horarios(rango_horarios)

        hora_inicio = parametros_horarios["Hora inicial"]
        hora_fin = parametros_horarios["Hora final"]
        todos_los_horarios = parametros_horarios["Todos los Horarios"]

        horas_ocupadas = await horarios_ocupados(doctor, fecha, hora_inicio, hora_fin)
        horarios_disponibles = list(set(todos_los_horarios) - set(horas_ocupadas))

        horarios_disponibles = sorted(horarios_disponibles)

    except Exception as e:
        print(f"Error al formatear el rango de horarios: {e}")        
        horarios_disponibles = []

    finally:
        return horarios_disponibles

async def enviar_fechas(doctor: int, wa_id: str) -> str:
    fechas_con_espacios = await formatear_fechas_disponibles(doctor)
    if not fechas_con_espacios:
        return "No se encontraron fechas con espacios"

    text = ''
    for i, fecha in enumerate(fechas_con_espacios):
        text += f"{i+1} - {format_datetime(fecha['fecha'], 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}\nEspacios: {28 - fecha['total_citas']}\n\n"
    
    respuesta = f"Tu doctor es: {doctor}\n"
    respuesta += f"Por favor, elige una fecha:\n{text}"
    
    return respuesta

async def enviar_rango_horarios(respuesta_cliente: str, wa_id: str) -> str:
    
    doctor = await obtener_doctor(wa_id)
    if not doctor:
        return "No se encontró doctor"
    
    fechas_mostradas = await formatear_fechas_disponibles(doctor)
    if not fechas_mostradas:
        return "No se encontraron fechas mostradas"
    
    if not (respuesta_cliente.isdigit()) or not (1 <= int(respuesta_cliente) <= len(fechas_mostradas)):
        return "Opción no válida. Por favor, elige una opción válida."
    
    fecha_seleccionada = fechas_mostradas[int(respuesta_cliente) - 1]["fecha"]

    await agregar_fecha_deseada(fecha_seleccionada, wa_id)

    rango_horarios = await formatear_rango_horarios(fecha_seleccionada, doctor)
    if not rango_horarios:
        return "No se encontraron rangos de horarios disponibles"

    respuesta = f"Tu doctor es: {doctor}\n"
    respuesta += f"Has seleccionado la fecha: {format_datetime(fecha_seleccionada, 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}\n\n"

    respuesta += f"Elige un rango de horarios:\n"
    for rango in rango_horarios:
        respuesta += rango

    return respuesta
    
async def enviar_horarios(respuesta_cliente: str, wa_id: str) -> str:
    
    fecha = await obtener_fecha(wa_id)
    if not fecha:
        return "No se encontró la fecha"

    doctor = await obtener_doctor(wa_id)
    if not doctor:
        return "No se encontró doctor"

    rangos_mostrados = await formatear_rango_horarios(fecha, doctor)
    if not rangos_mostrados:
        return "No se encontraron los rangos mostrados"

    if not (respuesta_cliente.isdigit()) or not (1 <= int(respuesta_cliente) <= len(rangos_mostrados)):
        return "Opción no válida. Por favor, elige una opción válida."

    horarios_disponibles = await formatear_horarios_disponibles(int(respuesta_cliente), doctor, fecha)
    if not horarios_disponibles:
        return "No se encontraron horarios disponibles"

    respuesta = f"Tu doctor es: {doctor}\n"
    respuesta += f"Has seleccionado la fecha: {format_datetime(fecha, 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}\n"
    respuesta += f"Has seleccionado el rango: {rangos_mostrados}\n\n"

    respuesta += f"Elige un horario:\n"

    for i, horario in enumerate(horarios_disponibles):
            respuesta += f"{i+1} - {horario}\n"

    return respuesta

def obtener_parametros_horarios(rango_horarios: int) -> dict:

    if rango_horarios == 1:
        hora_inicio = datetime.strptime("09:00", "%H:%M").time()
        hora_fin = datetime.strptime("11:59", "%H:%M").time()

    elif rango_horarios == 2:
        hora_inicio = datetime.strptime("12:00", "%H:%M").time()
        hora_fin = datetime.strptime("14:59", "%H:%M").time()

    elif rango_horarios == 3:
        hora_inicio = datetime.strptime("15:00", "%H:%M").time()
        hora_fin = datetime.strptime("17:59", "%H:%M").time()


    intervalo = timedelta(minutes=15) # Sólo se pueden agendar citas cada 15 minutos desde redes sociales
    todos_los_horarios = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    
    while hora_actual.time() <= hora_fin:
        # No se pueden agendar citas después de las {hora}:45
        # Es decir, la última cita se puede agendar a las {hora}:30
        # (1:30, 2:30, 3:30, 4:30...)
        if hora_actual.minute < 45:
            todos_los_horarios.append(hora_actual.strftime("%H:%M"))

        hora_actual += intervalo
    
    return {
        "Hora inicial": hora_inicio,
        "Hora final": hora_fin,
        "Todos los Horarios": todos_los_horarios
    }