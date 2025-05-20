from app.usecases.message_flow.message_builder.builder_interface import MessageBuilder

class MessageBuilderFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, tipo: str):
        def decorator(builder_cls):
            self._builders[tipo] = builder_cls()
            return builder_cls
        return decorator

    def get_builder(self, tipo: str) -> MessageBuilder:
        if tipo not in self._builders:
            raise ValueError(f"No hay builder registrado para el tipo: {tipo}")
        return self._builders[tipo]
