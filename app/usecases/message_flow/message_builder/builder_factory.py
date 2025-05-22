from app.usecases.message_flow.message_builder.builder_interface import MessageBuilder

class MessageBuilderFactory:
    _builders = {}

    @classmethod
    def register_builder(cls, tipo):
        def decorator(builder_cls):
            cls._builders[tipo] = builder_cls
            return builder_cls
        return decorator

    @classmethod
    def get_builder(cls, tipo):
        builder_cls = cls._builders.get(tipo)
        if not builder_cls:
            raise ValueError(f"No hay builder registrado para el tipo: {tipo}")
        return builder_cls()