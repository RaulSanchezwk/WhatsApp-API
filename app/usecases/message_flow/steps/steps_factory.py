from app.usecases.message_flow.steps.steps_interface import ConversationStep

class ConversationStepsFactory:
    _steps = {}

    @classmethod
    def register_step(cls, step: str):
        def decorator(step_cls):
            cls._steps[step] = step_cls
            return step_cls
        return decorator

    @classmethod
    def get_step(cls, step: str) -> ConversationStep:
        step_cls = cls._steps.get(step)
        if not step_cls:
            raise ValueError(f"No hay un paso registrado llamado: '{step}'")
        return step_cls
