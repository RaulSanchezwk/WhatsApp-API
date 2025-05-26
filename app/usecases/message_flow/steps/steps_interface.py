from abc import ABC, abstractmethod
from app.usecases.message_flow.message_sender.sender_factory import MessageSenderFactory
from app.usecases.message_flow.message_builder.builder_factory import MessageBuilderFactory
from app.usecases.message_flow.message_builder import builders
from app.usecases.message_flow.message_sender import senders
from app.core import constants

class ConversationStep(ABC):
    def __init__(self, contact, client_message: str):
        self.contact = contact
        self.client_message = client_message

    @abstractmethod
    async def handle(self) -> dict | None:
        pass

    async def validate_selected_option(self, data) -> dict | None:
        if not (self.client_message.isdigit()):
            return await self._send_error(constants.NOT_VALID_OPTION)
        
        elif not (1 <= int(self.client_message) <= len(data)):
            return await self._send_error(constants.NOT_VALID_OPTION)
        
        else:
            return None

    def build_message(self, step: str, data) -> str:
        builder = MessageBuilderFactory().get_builder(step)
        message = builder.build(data)

        return message
    
    async def send_message(self, message_sender: str, message) -> dict | None:
        sender = MessageSenderFactory().get_sender(message_sender)
        instance_sender = sender(self.contact.wa_id, message)

        return await instance_sender.send_message()

    async def _send_error(self, mensaje: str):
        sender = MessageSenderFactory.get_sender("whatsapp")
        instance_sender = sender(self.contact.wa_id, mensaje)
        await instance_sender.send_message()
