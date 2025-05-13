from app.infrastructure.whatsapp_client import send_whatsapp_text_message
from app.infrastructure.database.queries import ya_existe_contacto, obtener_estado, fechas_con_disponibilidad, rangos_con_disponibilidad, horarios_ocupados
from app.infrastructure.database.updates import cambiar_estado, relacionar_contacto
from app.infrastructure.database.insertions import save_contact
from datetime import datetime, timedelta
from babel.dates import format_datetime

async def manejar_mensaje(value: dict, webhook_DB_id: int) -> None:    
    # Aquí se define la función principal que maneja los mensajes entrantes de WhatsApp.
    # La función recibe el value del webhook 
    # y el ID del último webhook que se registró en la base de datos.

    wa_id = value["contacts"][0]["wa_id"]
    phone_number_id = value["metadata"]["phone_number_id"]
    contact = await ya_existe_contacto(wa_id)
    doctor = 43692

    if contact:
        await manejar_cliente_existente(value, webhook_DB_id, contact)
        await relacionar_contacto(contact, webhook_DB_id)
    else:
        print("\n\nCliente nuevo\n\n")
        wa_id = value["contacts"][0]["wa_id"]
        respuesta_fecha = f"Por favor, elige una fecha:\n{await formatear_fechas_disponibles(5, doctor)}"
        await send_whatsapp_text_message(wa_id, respuesta_fecha)
        id_contact = await save_contact(wa_id, value["messages"][0]["from"], value["contacts"][0]["profile"]["name"], 1)
        await relacionar_contacto(id_contact, webhook_DB_id)

async def manejar_cliente_existente(value, webhook_DB_id: int, id_contact: int) -> None:
    print("\n\nCliente existente\n\n")
    wa_id = value["contacts"][0]["wa_id"]
    profile_name = value["contacts"][0]["profile"]["name"]
    doctor = 43692
    rango_horarios = 1
    fecha = datetime(2025, 5, 13)
    numeros_permitidos = ['5218135745910', '5218123302217', '5218144883499', '5218116965030', '5218129133326', '5218119043177', '5218182803998', '5218110444217', '5218131240968', '5218182808236']

    if wa_id in numeros_permitidos:
        estado = await obtener_estado(id_contact)

        match estado:
            case 1:
                # respuesta_cliente = value["messages"][0]["text"]["body"]
                # print(f"Respuesta del cliente: {respuesta_cliente}")
                # respuesta = f"Tu respuesta fue: {respuesta_cliente}"

                # if respuesta not in ["1", "2", "3", "4", "5"]:
                #     respuesta = "Opción no válida. Por favor, elige una opción válida."
                #     await send_whatsapp_text_message(wa_id, respuesta)
                #     return
                
                respuesta = f"Elige un rango de horarios:\n{ await formatear_rango_horarios(fecha, doctor) }"
                await cambiar_estado(id_contact, 2)

            case 2:
                respuesta = f"Elige un horario:\n{ await formatear_horarios_disponibles(rango_horarios, doctor, fecha) }"
                await cambiar_estado(id_contact, 3)

            case None:
                respuesta = "No se encontró el estado"

            case -1:
                respuesta = "Ocurrió una excepción al consultar el estado"

            case 0:
                respuesta = f"Paso 0, esto no debería de mostrarse"

            case _:
                respuesta = "Caso no contemplado. Haz llegado al fin."
                print(f"\nRespuesta: {respuesta}\n")


        await send_whatsapp_text_message(wa_id, respuesta)

    #await send_whatsapp_text_message(wa_id, f"Yo te conozco... ¿verdad {profile_name}?")

async def formatear_fechas_disponibles(dias_a_generar: int, doctor: int) -> str:
    # Se establece la fecha inicial como mañana a las 00:00
    fecha_inicial = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1)
    # Se establece la fecha final como la fecha inicial + el número de días a generar
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
        
    except Exception as e:
        print(f"Error al obtener fechas: {e}")
        text = f"{e}"
    
    finally:
        return text

async def formatear_rango_horarios(fecha: str, doctor: int) -> str:
    try:
        rangos_con_espacios = await rangos_con_disponibilidad(fecha, doctor)

        print(f"\nRangos: {rangos_con_espacios}\n\n")

        text = ''

        for i, rango in enumerate(rangos_con_espacios):
            text += f"{i+1} - {rango['rango']}\n\n"

    except Exception as e:
        print(f"Error al formatear el rango de horarios: {e}")
        text = f"{e}"
    
    finally:
        return text

async def formatear_horarios_disponibles(rango_horarios: int, doctor: int, fecha: datetime) -> str:
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

    text = ''

    try:
        horas_ocupadas = await horarios_ocupados(doctor, fecha, hora_inicio, hora_fin)
        horarios_disponibles = list(set(todos_los_horarios) - set(horas_ocupadas))

        horarios_disponibles = sorted(horarios_disponibles)

        for i, horario in enumerate(horarios_disponibles):
            text += f"{i+1} - {horario}\n"
        return text
    
    except Exception as e:
        print(f"Error al formatear horarios: {e}")
        return str(e)