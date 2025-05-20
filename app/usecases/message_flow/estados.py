from app.infrastructure.whatsapp_client import send_whatsapp_text_message


class EnviarMensaje:
    async def __init__(self, wa_id, mensaje_cliente, id_contact, estado, respuesta_cliente):
        pass

    async def enviar_fechas(self) -> bool:
        try:
            if not (self.respuesta_cliente.isdigit()):
                return "Opción no válida. Por favor, elige una opción válida."

            if not (1 <= int(self.respuesta_cliente) <= len(constants.SUCURSALES)):
                return"Opción no válida. Por favor, elige una opción válida."

            doctor = constants.SUCURSALES[int(self.respuesta_cliente)]["ID DOCTOR"]

            fechas_con_espacios = await utils.get_fechas_disponibles(doctor)
            if not fechas_con_espacios:
                return "No se encontraron fechas con espacios"

            

            await send_whatsapp_text_message(self.wa_id, respuesta)

            return True
        
        except Exception as e:
            print(f"Error al enviar fechas: {e}")
            return False

    async def enviar_rango_horarios(self) -> bool:
        try:
            doctor = await queries.obtener_de_intencion("doctor", self.wa_id)
            if not doctor:
                return "No se encontró doctor"
            
            fechas_mostradas = await utils.get_fechas_disponibles(doctor)
            if not fechas_mostradas:
                return "No se encontraron fechas mostradas"

            if not (self.respuesta_cliente.isdigit()):
                return "Opción no válida. Por favor, elige una opción válida."
            if not (1 <= int(self.respuesta_cliente) <= len(fechas_mostradas)):
                return "Opción no válida. Por favor, elige una opción válida."
            
            fecha_seleccionada = fechas_mostradas[int(self.respuesta_cliente) - 1]["fecha"]

            rango_horarios = await utils.get_rango_horarios(fecha_seleccionada, doctor)
            if not rango_horarios:
                return "No se encontraron rangos de horarios disponibles"

            
            await send_whatsapp_text_message(self.wa_id, respuesta)

            return True
        
        except Exception as e:
            print(f"Error al enviar rango de horarios: {e}")
            return False

    async def enviar_horarios(self) -> bool:
        try:
            doctor = await queries.obtener_de_intencion("doctor", self.wa_id)
            if not doctor:
                return "No se encontró doctor"

            fecha = await queries.obtener_de_intencion("fecha_deseada", self.wa_id)
            if not fecha:
                return "No se encontró la fecha"

            rangos_mostrados = await utils.get_rango_horarios(fecha, doctor)
            if not rangos_mostrados:
                return "No se encontraron los rangos mostrados"

            if not (self.respuesta_cliente.isdigit()):
                return "Opción no válida. Por favor, elige una opción válida."
            if not (1 <= int(self.respuesta_cliente) <= len(rangos_mostrados)):
                return "Opción no válida. Por favor, elige una opción válida."
            
            rango_seleccionado = rangos_mostrados[int(self.respuesta_cliente) - 1]["rango"]

            await updates.agregar_rango_horarios(rango_seleccionado, self.wa_id)

            horarios_disponibles = await utils.get_horarios_disponibles(rango_seleccionado, doctor, fecha)
            if not horarios_disponibles:
                return "No se encontraron horarios disponibles"

            respuesta = f"Elige un horario:\n\n"

            for i, horario in enumerate(horarios_disponibles):
                respuesta += f"{i+1} - {horario.strftime('%I:%M %p').lstrip('0').lower()}\n"

            await send_whatsapp_text_message(self.wa_id, respuesta)
            return True
        
        except Exception as e:
            print(f"Error al enviar horarios: {e}")
            return False

    async def enviar_confirmacion(self) -> bool:
        try:
            doctor = await queries.obtener_de_intencion("doctor", self.wa_id)
            if not doctor:
                return "No se encontró doctor"

            fecha = await queries.obtener_de_intencion("fecha_deseada", self.wa_id)
            if not fecha:
                return "No se encontró la fecha"
            
            rango_horarios = await queries.obtener_de_intencion("rango", self.wa_id)
            if not rango_horarios:
                return "No se encontró el rango de horarios"
            
            horarios_mostrados = await utils.get_horarios_disponibles(rango_horarios, doctor, fecha)
            if not horarios_mostrados:
                return "No se encontraron los horarios mostrados"

            if not (self.respuesta_cliente.isdigit()):
                return "Opción no válida. Por favor, elige una opción válida."
            if not (1 <= int(self.respuesta_cliente) <= len(horarios_mostrados)):
                return "Opción no válida. Por favor, elige una opción válida."
            
            hora_seleccionada = horarios_mostrados[int(self.respuesta_cliente) - 1]

            respuesta = f"""
                        !Tu cita quedó agendada! 😁

                        📅 Para el día: {format_datetime(fecha, 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}

                        📍 En la sucursal: {utils.obtener_nombre_sucursal_por_doctor(doctor)}

                        🕐 A las: {hora_seleccionada.strftime('%I:%M %p').lstrip('0').lower()}"""
            
            await send_whatsapp_text_message(self.wa_id, respuesta)
            return True
        
        except Exception as e:
            print(f"Error al enviar confirmación: {e}")
            return False