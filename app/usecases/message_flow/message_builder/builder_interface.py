from abc import ABC, abstractmethod

class MessageBuilder(ABC):
    @abstractmethod
    def build(self, data) -> str:
        pass
