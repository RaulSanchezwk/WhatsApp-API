from app.usecases.message_flow.steps.steps_interface import ConversationStep
from app.usecases.message_flow.steps.steps_factory import ConversationStepsFactory
from app.usecases.message_flow.message_builder.builder_factory import MessageBuilderFactory
from app.usecases.message_flow.message_sender.sender_factory import MessageSenderFactory
from app.core import constants
import utils

factory = ConversationStepsFactory()

@factory.register_step("sucursal")
class SucursalStep(ConversationStep):
    async def handle(self):

        builder = MessageBuilderFactory().get_builder("sucursal")
        mensaje = builder.build(constants.SUCURSALES)

        sender = MessageSenderFactory().get_sender("whatsapp")
        await sender.send_message(self.client.wa_id, mensaje)

@factory.register_step("fechas")
class FechasStep(ConversationStep):
    async def handle(self):
        if not self.client_message.isdigit():
            return await self._send_error("Opción no válida. Por favor, elige una opción válida.")

        seleccion = int(self.client_message)
        if not (1 <= seleccion <= len(constants.SUCURSALES)):
            return await self._send_error("Opción no válida. Por favor, elige una opción válida.")

        doctor = constants.SUCURSALES[seleccion]["ID DOCTOR"]
        self.client.doctor = doctor
        self.client.estado_conv = "fechas"

        fechas = await utils.get_fechas_disponibles(doctor)
        if not fechas:
            return await self._send_error("No se encontraron fechas con espacios")
        
        builder = MessageBuilderFactory().get_builder("fechas")
        mensaje = builder.build(fechas)

        sender = MessageSenderFactory().get_sender("whatsapp")
        await sender.send_message(self.client.wa_id, mensaje)

@factory.register_step("rango_horarios")
class RangoHorariosStep(ConversationStep):
    async def handle(self):
        pass