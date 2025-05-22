from app.usecases.message_flow.message_sender.sender_interface import MessageSender

class MessageSenderFactory:
    _senders = {}

    @classmethod
    def register_sender(cls, name: str):
        def decorator(sender_cls):
            cls._senders[name] = sender_cls
            return sender_cls
        return decorator
    
    @classmethod
    def get_sender(cls, name: str, message: str) -> MessageSender:
        sender_cls = cls._senders.get(name)
        if not sender_cls:
            raise ValueError(f"No hay un sender registrado como: {name}")
        return sender_cls(message)
