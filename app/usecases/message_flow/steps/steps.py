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

        chosen_date = shown_dates[int(self.client_message) - 1]["fecha"]

        await updates.update_chosen_date(chosen_date, self.contact)

        hours_range = await utils.available_hours_ranges(chosen_date, branch)
        if not hours_range:
            return await self._send_error("No se encontraron rangos con horarios disponibles")
        
        message = self.build_message("rango horarios", hours_range)
        return await self.send_message("whatsapp", message)

@factory.register_step("horarios")
class HorariosStep(ConversationStep):
    async def handle(self) -> dict | None:
        chosen_brand = await queries.get_appt_intention("chosen_branch", self.contact)
        if not chosen_brand:
            print("\n\nError: No se encontró sucursal en: HorariosStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)
        
        branch = await queries.get_branch_by_id(chosen_brand)

        date = await queries.get_appt_intention("chosen_date", self.contact)
        if not date:
            print("\n\nError: No se encontró fecha en: HorariosStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)

        shown_ranges = await utils.available_hours_ranges(date, branch)
        if not shown_ranges:
            print("\n\nError: No se encontraron rangos de horarios en: HorariosStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)

        error_response = await self.validate_selected_option(shown_ranges)
        if error_response:
            return error_response
        
        chosen_range = shown_ranges[int(self.client_message) - 1]["rango"]

        await updates.update_chosen_hours_range(chosen_range, self.contact)
        
        available_hours = await utils.available_hours(chosen_range, branch, date)
        if not available_hours:
            return await self._send_error("No se encontraron horarios disponibles")

        message = self.build_message("horarios", available_hours)
        return await self.send_message("whatsapp", message)

@factory.register_step("confirmación")
class ConfirmacionStep(ConversationStep):
    async def handle(self) -> dict | None:
        chosen_branch = await queries.get_appt_intention("chosen_branch", self.contact)

        if not chosen_branch:
            print("\n\nError: No se encontró sucursal en: ConfirmacionStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)
        
        branch = await queries.get_branch_by_id(chosen_branch)

        date = await queries.get_appt_intention("chosen_date", self.contact)
        if not date:
            print("\n\nError: No se encontró fecha en: ConfirmacionStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)
        
        hours_range = await queries.get_appt_intention("chosen_hours_range", self.contact)
        if not hours_range:
            print("\n\nError: No se encontró rango de horarios en: ConfirmacionStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)
        
        shown_hours = await utils.available_hours(hours_range, branch, date)
        if not shown_hours:
            print("\n\nError: No se encontraron horarios en: ConfirmacionStep\n\n")
            return await self._send_error(constants.ERROR_MESSAGE)

        error_response = await self.validate_selected_option(shown_hours)
        if error_response:
            print(f"\n\nError: error response {error_response}\n\n")
            return error_response
        
        chosen_hour = shown_hours[int(self.client_message) - 1]

        await updates.update_chosen_hour(chosen_hour, self.contact)

        data = {"Branch": branch, "Date": date, "Chosen Hour": chosen_hour}
        message = self.build_message("confirmación", data)
        return await self.send_message("whatsapp", message)
