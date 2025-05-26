from app.usecases.message_flow.steps.steps_interface import ConversationStep
from app.usecases.message_flow.steps.steps_factory import ConversationStepsFactory
from app.core import constants
from app.usecases.message_flow import utils
from app.infrastructure.database import queries, updates
from app.domain.entities import Branch

factory = ConversationStepsFactory()

@factory.register_step("sucursales")
class SucursalesStep(ConversationStep):
    async def handle(self) -> dict | None:

        branches = await queries.get_active_branches()

        message = self.build_message("sucursales", branches)
        return await self.send_message("whatsapp", message)

@factory.register_step("fechas")
class FechasStep(ConversationStep):
    async def handle(self) -> dict | None:

        branches = await queries.get_active_branches()
        if not branches:
            print("\n\nError: No se encontraron sucursales activas en: FechasStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE) 

        error_response = await self.validate_selected_option(branches)
        if error_response:
            return error_response

        # I'll change this in the future
        for b in branches:
            if b.id == int(self.client_message):
                branch = b

        await updates.update_chosen_branch(branch, self.contact)

        dates = await utils.available_dates(branch)
        if not dates:
            return await self._send_error("No se encontraron fechas con espacios")
        
        message = self.build_message("fechas", dates)
        return await self.send_message("whatsapp", message)

@factory.register_step("rango horarios")
class RangoHorariosStep(ConversationStep):
    async def handle(self) -> dict | None:
        chosen_branch = await queries.get_appt_intention("chosen_branch", self.contact)

        if not chosen_branch:
            print("\n\nError: No se encontró sucursal en: RangoHorariosStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)
        
        branch = await queries.get_branch_by_id(chosen_branch)
        shown_dates = await utils.available_dates(branch)
        if not shown_dates:
            print("\n\nError: No se encontraron fechas mostradas en: RangoHorariosStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)

        error_response = await self.validate_selected_option(shown_dates)
        if error_response:
            return error_response

        selected_date = shown_dates[int(self.client_message) - 1]["fecha"]

        hours_range = await utils.available_hours_ranges(selected_date, branch)
        if not hours_range:
            return await self._send_error("No se encontraron rangos con horarios disponibles")
        
        message = self.build_message("rango horarios", hours_range)
        return await self.send_message("whatsapp", message)

@factory.register_step
class HorariosStep(ConversationStep):
    async def handle(self) -> dict | None:
        pass