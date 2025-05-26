from abc import ABC, abstractmethod

class MessageSender(ABC):
    def __init__(self, id, message):
        self.id = id
        self.message = message

    @abstractmethod
    async def send_message(self):
        pass