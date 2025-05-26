from app.core import constants

class FlowManager:
    def get_next_step(self, current_step: str) -> str:
        match current_step:
            case constants.INITIAL_STEP:
                next_step = "fechas"

            case "sucursales":
                next_step = "fechas"

            case "fechas":
                next_step = "rango horarios"

            case "rango horarios":
                next_step = "hora"
            
        return next_step