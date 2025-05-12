from app.infrastructure.whatsapp_client import send_whatsapp_text_message
from app.infrastructure.database.queries import ya_existe_contacto, fechas_con_disponibilidad
from datetime import datetime, timedelta, date
from babel.dates import format_datetime

# Aquí se define la función principal que maneja los mensajes entrantes de WhatsApp.
# La función recibe el ID de WhatsApp, el ID del número de teléfono y 
# el ID del webhook de la base de datos (last_row_id).
async def manejar_mensaje(value: dict, webhook_DB_id) -> None:
    wa_id = value["contacts"][0]["wa_id"]
    phone_number_id = value["metadata"]["phone_number_id"]
    ya_existe = await ya_existe_contacto(wa_id, phone_number_id)

    if ya_existe:
        await manejar_cliente_existente(value, webhook_DB_id)
    else:
        await manejar_cliente_nuevo(value, webhook_DB_id)
        

async def manejar_cliente_nuevo(value: dict, webhook_DB_id: int) -> None: 
    # Aquí se define una lista de números permitidos para el flujo de mensajes.
    # Estos números son los únicos que pueden interactuar con el bot.
    # Cuando se libere el bot, se eliminará esta lista y su lógica.
    wa_id = value["contacts"][0]["wa_id"]

    numeros_permitidos = ['5218135745910', '5218123302217', '5218144883499', '5218116965030', '5218129133326', '5218119043177', '5218182803998', '5218110444217', '5218131240968', '5218182808236']

    if wa_id in numeros_permitidos:
        respuesta_fecha = f"Por favor, elige una fecha:\n{await formatear_fechas_disponibles(5)}"
        await send_whatsapp_text_message(wa_id, respuesta_fecha)

        # respuesta_am_pm = "¿Te gustaría agendar una cita en la mañana o en la tarde?"
        # await send_whatsapp_text_message(wa_id, respuesta_am_pm)

        # respuesta_horarios = f"Por favor, elige una hora para tu cita:\n {obtener_rango_horarios("mañana")}"
        # await send_whatsapp_text_message(wa_id, respuesta_horarios)


async def manejar_cliente_existente(value, webhook_DB_id) -> None:
    wa_id = value["contacts"][0]["wa_id"]
    profile_name = value["contacts"][0]["profile"]["name"] 
    await send_whatsapp_text_message(wa_id, f"Yo te conozco... ¿verdad {profile_name}?")

async def formatear_fechas_disponibles(dias_a_generar: int) -> str:
    fecha_inicial = datetime.today() + timedelta(days=1)  # Se establece la fecha inicial como mañana
    fecha_final = fecha_inicial + timedelta(days=dias_a_generar)

    
    # Esta función se encarga de obtener las fechas disponibles para agendar una cita.
    # Recibe como parámetros la fecha de inicio y la fecha de fin.
    try:
        fechas_con_espacios = await fechas_con_disponibilidad(fecha_inicial, fecha_final)
        
        text = ''

        for i, fecha in enumerate(fechas_con_espacios):
            # Se formatea la fecha en español usando Babel
            # Se utiliza el formato "EEEE, d 'de' MMMM 'de' y"
            # (miércoles, 1 de enero de 2025)
            text += f"{i+1} - {format_datetime(fecha['fecha'], 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}\nEspacios: {28 - fecha['total_citas']}\n\n"
        
        return text
        
    except Exception as e:
        print(f"Error al obtener fechas: {e}")
        text = f"{e}"
    
    finally:
        return text

async def formatear_horarios_disponibles(fecha: str, rango_horarios: str) -> str:
    # Esta función se encarga de formatear los horarios disponibles para una fecha específica.
    # Recibe como parámetros la fecha y el rango de horarios.

    if rango_horarios == "9-12":
        hora_inicio = datetime.strptime("09:00", "%H:%M").time()
        hora_fin = datetime.strptime("12:00", "%H:%M").time()
    elif rango_horarios == "12-3":
        hora_inicio = datetime.strptime("12:00", "%H:%M").time()
        hora_fin = datetime.strptime("15:00", "%H:%M").time()
    elif rango_horarios == "3-6":
        hora_inicio = datetime.strptime("15:00", "%H:%M").time()
        hora_fin = datetime.strptime("18:00", "%H:%M").time()
    


    try:
        text = f"Horarios disponibles para {fecha}:\n"
        for i, horario in enumerate(rango_horarios):
            text += f"{i+1} - {horario}\n"
        return text
    except Exception as e:
        print(f"Error al formatear horarios: {e}")
        return str(e)

def obtener_rango_fechas(dias_a_generar: int) -> str:
    # Esta función se encarga de obtener un rango de fechas en los que se puede agendar una cita.

    fecha_inicial = datetime.today() + timedelta(days=1)  # Se establece la fecha inicial como mañana

    # Se genera un rango de fechas desde la fecha inicial hasta el número de días a generar + 1,
    # este +1 está ya que se filtran las fechas para eliminar los domingos (weekday() != 6)
    # y en caso de el rango de fechas no contenga un domingo se agrega un día más
    # para luego filtrar solo {dias_a_generar} días hábiles.
    rango_fechas = [
    fecha_inicial + timedelta(days=i)
    for i in range(dias_a_generar + 1)
    if (fecha_inicial + timedelta(days=i)).weekday() != 6
    ][:dias_a_generar]

    rango_fechas_format = []
    for fecha in rango_fechas:
        rango_fechas_format.append(format_datetime(fecha, 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES'))

    rango_horarios = {}
    for fecha in rango_fechas_format:
        rango_horarios[fecha] = obtener_rango_horarios()

    # for key, value in rango_horarios:
    #     #fecha_dt = datetime.combine(fecha, datetime.min.time())  # convierte date → datetime
    #     # Se formatea la fecha en español usando Babel
    #     # Se utiliza el formato "EEEE, d 'de' MMMM 'de' y"
    #     # (miércoles, 1 de enero de 2025)
    #     text += f"{1} - {format_datetime(key, 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')} : {value}\n\n"

    text = ''
    for i, fecha in enumerate(rango_horarios.keys()):
        text += f"\n\n{i+1} - {fecha}:\n"
        for j, horario in enumerate(rango_horarios[fecha]):
            text += f"{i+1}.{j+1} - {horario}\n"
    print(text)

    return text

# Esta función se encarga de obtener un rango de horarios en los que se puede agendar una cita.
# Recibe un string que indica el horario ("9-12", "12-3" o "3-6").
def obtener_rango_horarios() -> str: #horario: str
    # if horario == "9-12":
    #     horario_inicio = datetime.strptime("09:00", "%H:%M").time()
    #     horario_fin = datetime.strptime("12:00", "%H:%M").time()
    # if horario == "12-3":
    #     horario_inicio = datetime.strptime("12:00", "%H:%M").time()
    #     horario_fin = datetime.strptime("15:00", "%H:%M").time()
    # elif horario == "3-6":
    #     horario_inicio = datetime.strptime("15:00", "%H:%M").time()
    #     horario_fin = datetime.strptime("18:00", "%H:%M").time()
    horario_inicio = datetime.strptime("09:00", "%H:%M").time()
    horario_fin = datetime.strptime("18:00", "%H:%M").time()

    # Sólo se pueden agendar citas cada 15 minutos desde redes sociales
    intervalo = timedelta(minutes=15)
    horarios = []
    hora_actual = datetime.combine(datetime.today(), horario_inicio)
    

    while hora_actual.time() <= horario_fin:
        # No se pueden agendar citas después de las {hora}:45
        # Es decir, la última cita se puede agendar a las {hora}:30
        # (1:30, 2:30, 3:30, 4:30...)
        if hora_actual.minute < 45:
            horarios.append(hora_actual.strftime("%H:%M"))

        hora_actual += intervalo


    # text = ''

    # for i, horario in enumerate(horarios):
    #     text += f"{i+1} - {horario}\n"

    return horarios