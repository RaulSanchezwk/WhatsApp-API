from datetime import datetime, timedelta
from app.core import constants
from app.infrastructure.database import queries

async def get_fechas_disponibles(doctor: int) -> list:
    
    fecha_inicial = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1) # Se establece la fecha inicial 
                                                                                                # como mañana a las 00:00
    
    fecha_final = fecha_inicial + timedelta(days=constants.DIAS_A_GENERAR + 5) # Se establece la fecha final como la 
                                                                           # fecha inicial + el número de días a generar
                                                                           # + 5 para asegurar un rango completo

    
    try:
        # Aquí se hace la consulta y se limita el número de días a el número de días a generar
        fechas_con_espacios = await queries.fechas_con_disponibilidad(fecha_inicial, fecha_final, doctor)[:constants.DIAS_A_GENERAR - 1]
        
    except Exception as e:
        print(f"Error al obtener fechas: {e}")
        fechas_con_espacios = []
    
    finally:
        return fechas_con_espacios

async def get_rango_horarios(fecha: str, doctor: int) -> list:
    try:
        rangos_con_espacios = await queries.rangos_con_disponibilidad(fecha, doctor)

    except Exception as e:
        print(f"Error al formatear el rango de horarios: {e}")        
        rangos_con_espacios = []

    finally:
        return rangos_con_espacios

async def get_horarios_disponibles(rango_horarios: str, doctor: int, fecha: datetime) -> list:
    try: 
        parametros_horarios = obtener_parametros_horarios(rango_horarios)

        hora_inicio = parametros_horarios["Hora inicial"]
        hora_fin = parametros_horarios["Hora final"]
        todos_los_horarios = parametros_horarios["Todos los Horarios"]

        horas_ocupadas = await queries.horarios_ocupados(doctor, fecha, hora_inicio, hora_fin)
        horas_ocupadas = [((datetime.min + hora).time() if isinstance(hora, timedelta) else hora) for hora in horas_ocupadas]

        horarios_disponibles = list(set(todos_los_horarios) - set(horas_ocupadas))

        horarios_disponibles = sorted(horarios_disponibles)

    except Exception as e:
        print(f"Error al formatear horarios disponibles: {e}")        
        horarios_disponibles = []

    finally:
        return horarios_disponibles

def obtener_parametros_horarios(rango_horarios: str) -> dict:

    if rango_horarios == "9:00 am - 12:00 pm":
        hora_inicio = datetime.strptime("09:00", "%H:%M").time()
        hora_fin = datetime.strptime("11:59", "%H:%M").time()

    elif rango_horarios == "12:00 pm - 3:00 pm":
        hora_inicio = datetime.strptime("12:00", "%H:%M").time()
        hora_fin = datetime.strptime("14:59", "%H:%M").time()

    elif rango_horarios == "3:00 pm - 6:00 pm":
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
            todos_los_horarios.append(hora_actual.time())

        hora_actual += intervalo
    
    return {
        "Hora inicial": hora_inicio,
        "Hora final": hora_fin,
        "Todos los Horarios": todos_los_horarios
    }

def obtener_nombre_sucursal_por_doctor(id_doctor: int) -> str:
    for sucursal in constants.SUCURSALES.values():
        if sucursal["ID DOCTOR"] == id_doctor:
            return sucursal["NOMBRE SUC."]
    return "Sucursal desconocida"