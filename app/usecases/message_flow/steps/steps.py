from app.usecases.message_flow.steps.steps_interface import ConversationStep
from app.usecases.message_flow.steps.steps_factory import ConversationStepsFactory
from app.usecases.message_flow.message_builder.builder_factory import MessageBuilderFactory
from app.usecases.message_flow.message_sender.sender_factory import MessageSenderFactory
from app.usecases.message_flow.message_builder import builders
from app.usecases.message_flow.message_sender import senders
from app.core import constants
from app.usecases.message_flow import utils

factory = ConversationStepsFactory()

@factory.register_step("sucursales")
class SucursalStep(ConversationStep):
    async def handle(self):

        builder = MessageBuilderFactory().get_builder("sucursales")
        message = builder.build(constants.BRANCHES)

        sender = MessageSenderFactory().get_sender("whatsapp", message)
        await sender.send_message(self.contact.wa_id)

@factory.register_step("fechas")
class FechasStep(ConversationStep):
    async def handle(self):

        if not self.client_message.isdigit():
            return await self._send_error("Opción no válida. Por favor, elige una opción válida.")

        selection = int(self.client_message)
        if not (1 <= selection <= len(constants.BRANCHES)):
            return await self._send_error("Opción no válida. Por favor, elige una opción válida.")

        doctor = constants.BRANCHES[selection]["DOCTOR ID"]

        fechas = await utils.available_dates(doctor)
        if not fechas:
            return await self._send_error("No se encontraron fechas con espacios")
        
        builder = MessageBuilderFactory().get_builder("fechas")
        message = builder.build(fechas)

        print(message)

        sender = MessageSenderFactory().get_sender("whatsapp", message)
        await sender.send_message(self.contact.wa_id)

@factory.register_step("rango horarios")
class RangoHorariosStep(ConversationStep):
    async def handle(self):
        pass
