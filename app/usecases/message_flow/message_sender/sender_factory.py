from app.usecases.message_flow.message_sender.sender_interface import MessageSender

class MessageSenderFactory:
    def __init__(self):
        self._senders = {}

    def register_sender(self, tipo: str):
        def decorator(sender_cls):
            self._senders[tipo] = sender_cls()
            return sender_cls
        return decorator
    
    def get_sender(self, tipo: str) -> MessageSender:
        if tipo not in self._senders:
            raise ValueError(f"No hay sender registrado para: {tipo}")
        return self._senders[tipo]
