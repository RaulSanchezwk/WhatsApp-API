from abc import ABC, abstractmethod

class MessageSender(ABC):
    def __init__(self, client_message):
        self.client_message = client_message

    @abstractmethod
    async def send_message(self, id: str):
        pass