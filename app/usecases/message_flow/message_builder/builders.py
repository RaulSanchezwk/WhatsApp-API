from app.usecases.message_flow.message_builder.builder_factory import MessageBuilderFactory
from app.usecases.message_flow.message_builder.builder_interface import MessageBuilder
from babel.dates import format_datetime
from app.domain.entities import Branch

factory = MessageBuilderFactory()

@factory.register_builder("sucursales")
class SucursalesMessageBuilder(MessageBuilder):
    def build(self, branches: list[Branch]):
        message = "Elige una sucursal:\n"
        for branch in branches:
            message += f"{branch.id} - {branch.branch_name}\n"
        return message
    
@factory.register_builder("fechas")
class FechasMessageBuilder(MessageBuilder):
    def build(self, fechas_con_espacios: list):
        message = f"Por favor, elige una fecha:\n\n"
        for i, fecha in enumerate(fechas_con_espacios):
            message += f"{i+1} - {format_datetime(fecha['fecha'], 'EEEE, d \'de\' MMMM \'de\' y', locale='es_ES')}\nEspacios: {28 - fecha['total_citas']}\n\n"
        return message

@factory.register_builder("rango horarios")
class RangosMessageBuilder(MessageBuilder):
    def build(self, rango_horarios: list):
        message = f"Elige un rango de horarios:\n\n"
        for i, rango in enumerate(rango_horarios):
            message += f"{i+1} - {rango["rango"]}\nEspacios: {9 - rango["citas"]}\n\n"
        return message

@factory.register_builder("horarios")
class HorariosMessageBuilder(MessageBuilder):
    def build(self, horarios_disponibles: list):
        message = f"Elige un horario:\n\n"
        for i, horario in enumerate(horarios_disponibles):
            message += f"{i+1} - {horario}\nEspacios: {9 - horario["citas"]}"
        return message
