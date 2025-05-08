from app.domain.entities import Cliente
from app.infrastructure.whatsapp_client import send_whatsapp_text_message
from app.infrastructure.database.queries import ya_existe_contacto
from datetime import datetime, timedelta, date
from babel.dates import format_datetime

async def manejar_mensaje(value):

    try:
        wa_id = value.contacts[0].wa_id
        phone_number_id = value.metadata.phone_number_id
    except (IndexError, AttributeError):
        print("⚠️ No se pudo extraer wa_id o phone_number_id")
        return


    ya_existe = await ya_existe_contacto(wa_id, phone_number_id)

    if ya_existe:
        print(f"📨 Contacto ya conocido: {wa_id}")
        await manejar_mensaje_existente(wa_id, phone_number_id, value)
    else:
        print(f"📩 Nuevo contacto: {wa_id}")
        await manejar_mensaje_nuevo(wa_id, phone_number_id, value)
        ###### agregar a la base de datos el nuevo contacto
        

async def manejar_mensaje_nuevo(wa_id: str, phone_number_id: str, value): 
    numeros_permitidos = ['5218135745910', '5218123302217', '5218144883499', '5218116965030', '5218129133326', '5218119043177', '5218182803998', '5218110444217', '5218131240968', '5218182808236']

    if wa_id in numeros_permitidos:
        respuesta_fecha = f"Por favor, elige una fecha:\n{obtener_rango_fechas(5)}"
        await send_whatsapp_text_message(wa_id, respuesta_fecha)

        # respuesta_am_pm = "¿Te gustaría agendar una cita en la mañana o en la tarde?"
        # await send_whatsapp_text_message(wa_id, respuesta_am_pm)

        # respuesta_horarios = f"Por favor, elige una hora para tu cita:\n {obtener_rango_horarios("mañana")}"
        # await send_whatsapp_text_message(wa_id, respuesta_horarios)


async def manejar_mensaje_existente(wa_id: str, phone_number_id: str, value) -> None:
    await send_whatsapp_text_message(wa_id, f"Yo te conozco... ¿verdad {value.contacts[0].profile.name}?")

def obtener_rango_fechas(dias_a_generar: int) -> str:

    fecha_inicial = date.today()# + timedelta(days=5)
    dias_a_generar = 5

    rango_fechas = [fecha_inicial + timedelta(days=i) for i in range(dias_a_generar + 1)]
    rango_fechas_sin_domingo = [fecha for fecha in rango_fechas if fecha.weekday() != 6]
    text = ''

    for i, fecha in enumerate(rango_fechas_sin_domingo[:5]):
        fecha_dt = datetime.combine(fecha, datetime.min.time())  # convierte date → datetime
        text += f"{i+1} - {format_datetime(fecha_dt, 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}\n"
    
    return text

def obtener_rango_horarios(horario: str) -> str:
    if horario == "mañana":
        horario_inicio = datetime.strptime("09:00", "%H:%M").time()
        horario_fin = datetime.strptime("12:30", "%H:%M").time()
    elif horario == "tarde":
        horario_inicio = datetime.strptime("13:00", "%H:%M").time()
        horario_fin = datetime.strptime("18:00", "%H:%M").time()

    intervalo = timedelta(minutes=15)
    horarios = []
    hora_actual = datetime.combine(datetime.today(), horario_inicio)
    
    while hora_actual.time() <= horario_fin:
        if hora_actual.minute < 45:
            horarios.append(hora_actual.strftime("%H:%M"))

        hora_actual += intervalo


    text = ''

    for i, horario in enumerate(horarios):
        text += f"{i+1} - {horario}\n"

    return text