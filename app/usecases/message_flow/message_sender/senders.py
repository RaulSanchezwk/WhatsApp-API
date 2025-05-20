from app.usecases.message_flow.message_sender.sender_interface import MessageSender
from app.usecases.message_flow.message_sender.sender_factory import MessageSenderFactory
from app.infrastructure.whatsapp_client import send_whatsapp_text_message 

factory = MessageSenderFactory()

@factory.register_sender("whatsapp")
class WhatsAppMessageSender(MessageSender):
    async def send_message(self, id: str):
        try:
            await send_whatsapp_text_message(id, self.client_message)

        except Exception as e:
            print(f"Error al enviar mensaje desde WhatsApp: {e}")

@factory.register_sender("facebook")
class FacebookMessageSender(MessageSender):
    async def send_message(self, id: str):
        try:
            ###### Enviar mensaje desde Facebook Pages
            pass

        except Exception as e:
            print(f"Error al enviar mensaje desde Facebook: {e}")
