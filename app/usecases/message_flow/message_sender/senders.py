from app.usecases.message_flow.message_sender.sender_interface import MessageSender
from app.usecases.message_flow.message_sender.sender_factory import MessageSenderFactory
from app.infrastructure.whatsapp_client import send_whatsapp_text_message 

factory = MessageSenderFactory()

@factory.register_sender("whatsapp")
class WhatsAppMessageSender(MessageSender):
    async def send_message(self) -> dict | None:
        try:
            print(self.message)
            return await send_whatsapp_text_message(self.id, self.message)

        except Exception as e:
            print(f"Error al enviar mensaje desde WhatsApp: {e}")
            return None

@factory.register_sender("facebook")
class FacebookMessageSender(MessageSender):
    async def send_message(self):
        try:
            ###### Enviar mensaje desde Facebook Pages
            pass

        except Exception as e:
            print(f"Error al enviar mensaje desde Facebook: {e}")
