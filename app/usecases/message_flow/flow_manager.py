from app.core import constants

class FlowManager:
    def get_next_step(self, current_step: str) -> str:
        match current_step:
            case constants.INITIAL_STEP:
                return "fechas"
            
            # case "sucursales":
            #     return "fechas"
            
            case "fechas":
                return "rango horarios"
            
            case "rango horarios":
                return "hora"
            