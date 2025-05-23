from abc import ABC, abstractmethod
from app.usecases.message_flow.message_sender.sender_factory import MessageSenderFactory

class ConversationStep(ABC):
    def __init__(self, contact, client_message: str):
        self.contact = contact
        self.client_message = client_message

    @abstractmethod
    async def handle(self) -> None:
        pass

    async def _send_error(self, mensaje: str):
        sender = MessageSenderFactory.get_sender("whatsapp")
        await sender.send_message(self.contact.wa_id, mensaje)
