from datetime import datetime, timedelta
from app.core import constants
from app.infrastructure.database import queries
from app.domain.entities import Branch

async def available_dates(branch: Branch) -> list:
    
    fecha_inicial = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(days=1) # Se establece la fecha inicial 
                                                                                                # como mañana a las 00:00
    
    fecha_final = fecha_inicial + timedelta(days=constants.DAYS_TO_SHOW) # Se establece la fecha final como la 
                                                                           # fecha inicial + el número de días a generar
    
    try:
        fechas_con_espacios = await queries.get_available_dates(fecha_inicial, fecha_final, branch)
        
    except Exception as e:
        print(f"Error at available_dates: {e}")
        fechas_con_espacios = []
    
    finally:
        return fechas_con_espacios

async def available_hours_ranges(fecha: str, doctor: int) -> list:
    try:
        rangos_con_espacios = await queries.get_available_ranges(fecha, doctor)

    except Exception as e:
        print(f"Error at available_hours_ranges: {e}")        
        rangos_con_espacios = []

    finally:
        return rangos_con_espacios

async def available_hours(rango_horarios: str, doctor: int, fecha: datetime) -> list:
    try: 
        parametros_horarios = build_available_hour_context(rango_horarios)

        hora_inicio = parametros_horarios["Hora inicial"]
        hora_fin = parametros_horarios["Hora final"]
        todos_los_horarios = parametros_horarios["Todos los Horarios"]

        horas_ocupadas = await queries.horarios_ocupados(doctor, fecha, hora_inicio, hora_fin)
        horas_ocupadas = [((datetime.min + hora).time() if isinstance(hora, timedelta) else hora) for hora in horas_ocupadas]

        horarios_disponibles = list(set(todos_los_horarios) - set(horas_ocupadas))

        horarios_disponibles = sorted(horarios_disponibles)

    except Exception as e:
        print(f"Error at available_hours: {e}")        
        horarios_disponibles = []

    finally:
        return horarios_disponibles

def build_available_hour_context(hours_range: str) -> dict:

    if hours_range == "9:00 am - 12:00 pm":
        start_hour = datetime.strptime("09:00", "%H:%M").time()
        end_hour = datetime.strptime("11:59", "%H:%M").time()

    elif hours_range == "12:00 pm - 3:00 pm":
        start_hour = datetime.strptime("12:00", "%H:%M").time()
        end_hour = datetime.strptime("14:59", "%H:%M").time()

    elif hours_range == "3:00 pm - 6:00 pm":
        start_hour = datetime.strptime("15:00", "%H:%M").time()
        end_hour = datetime.strptime("17:59", "%H:%M").time()

    interval = timedelta(minutes=15) # Sólo se pueden agendar citas cada 15 minutos desde redes sociales
    allowed_hours = []
    actual_hour = datetime.combine(datetime.today(), start_hour)
    
    while actual_hour.time() <= end_hour:
        # No se pueden agendar citas después de las {hora}:45
        # Es decir, la última cita se puede agendar a las {hora}:30
        # (1:30, 2:30, 3:30, 4:30...)
        if actual_hour.minute < 45:
            allowed_hours.append(actual_hour.time())

        actual_hour += interval
    
    return {
        "Allowed Hours": allowed_hours,
        "Start Hour": start_hour,
        "End Hour": end_hour,
    }

def branch_name_by_doctor_id(doctor_id: int) -> str:
    for branch in constants.BRANCHES.values():
        if branch["DOCTOR ID"] == doctor_id:
            return branch["BRANCH NAME"]
    return f"branch_name_by_doctor_id: Unknown branch with DOCTOR ID: {doctor_id}"

def doctor_id_by_branch_name(branch: str) -> str:
    for b in constants.BRANCHES.values():
        if b["BRANCH NAME"] == branch.upper():
            return b["DOCTOR ID"]
    return f"doctor_id_by_branch_name: Unknown doctor for branch: {branch}"
