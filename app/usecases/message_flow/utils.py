from datetime import datetime, timedelta, time
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

async def available_hours_ranges(date: str, branch: Branch) -> list:
    try:
        rangos_con_espacios = await queries.get_available_ranges(branch, date)

    except Exception as e:
        print(f"Error at available_hours_ranges: {e}")        
        rangos_con_espacios = []

    finally:
        return rangos_con_espacios

async def available_hours(hours_range: str, branch: Branch, date: datetime) -> list[time]:
    try: 
        avilable_hour_context = build_available_hour_context(hours_range)

        start_hour = avilable_hour_context["Start Hour"]
        end_hour = avilable_hour_context["End Hour"]
        allowed_hours = avilable_hour_context["Allowed Hours"]

        occupied_hours = await queries.get_occupied_hours(branch, date, start_hour, end_hour)

        occupied_hours = [((datetime.min + hour).time() if isinstance(hour, timedelta) else hour) for hour in occupied_hours]

        available_hours = list(set(allowed_hours) - set(occupied_hours))

        available_hours = sorted(available_hours)

    except Exception as e:
        print(f"Error at available_hours: {e}")        
        available_hours = []

    finally:
        return available_hours

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
