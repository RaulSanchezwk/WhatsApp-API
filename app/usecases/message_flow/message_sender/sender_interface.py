from abc import ABC, abstractmethod

class MessageSender(ABC):
    def __init__(self, message):
        self.message = message

    @abstractmethod
    async def send_message(self, id: str):
        pass